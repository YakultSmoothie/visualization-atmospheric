#!/usr/bin/env python3
"""
Input:
    extract_wrf_to_nc.py files: ./extract_wrf_to_nc/??.nc

Output:
    NetCDF files: {OUTPUT_FILE}

Author: CYC(YakultSmoothie)
Date: 2025.09.23
Modified: 2025.09.24 - Support iterative processing (member-time-level) for memory efficiency
"""
#==================================================================================================
import numpy as np
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
import argparse
import os
#=========================================================================

def process_multiple_levels_iterative(INPUT_DIR, OUTPUT_FILE, LEVELS):
    """
    逐成員、逐時間、逐層處理資料並輸出到同一個檔案
    
    Parameters:
    -----------
    INPUT_DIR : str
        輸入資料目錄
    OUTPUT_FILE : str  
        輸出檔案路徑
    LEVELS : list
        氣壓層列表 (hPa)
    """
    print(f"\n=== Processing Multiple Levels Iteratively: {LEVELS} hPa ===")
    print(f"Reading data from: {INPUT_DIR}")

    input_file = {}
    input_file['eth'] = f'{INPUT_DIR}/eth.nc'
    input_file['uv'] = f'{INPUT_DIR}/ua,va.nc'

    # 列出使用到的檔案
    print("Files to be used:")
    for key, path in input_file.items():
        print(f"  {key}: {path}")

    # 開啟資料集（保持開啟以便逐一讀取）
    print(f"Opening datasets...")
    ds_eth = xr.open_dataset(input_file['eth'])
    ds_wind = xr.open_dataset(input_file['uv'])
    
    # 讀取基本座標資訊
    lons = ds_eth['XLONG'].values * units('degree')
    lats = ds_eth['XLAT'].values * units('degree')
    times = ds_eth['Time'].values
    members = ds_eth['member'].values
    available_levels = ds_eth['interp_level'].values

    print(f"    Available pressure levels: {available_levels}")
    print(f"    Requested levels: {LEVELS}")
    
    # 檢查所有要求的氣壓層是否存在
    missing_levels = [level for level in LEVELS if level not in available_levels]
    if missing_levels:
        print(f"    Warning: Missing levels {missing_levels}")
        LEVELS = [level for level in LEVELS if level in available_levels]
        print(f"    Processing available levels: {LEVELS}")

    print(f"    Members: {len(members)} ({members})")
    print(f"    Times: {len(times)} ({times[0]} to {times[-1]})")
    print(f"    Levels: {len(LEVELS)} ({LEVELS})")
    print(f"    Grid size: {lats.shape}")

    # 計算網格間距（一次計算，後續重複使用）
    dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)
    print(f"    Grid spacing: dx={dx.mean():.1f}, dy={dy.mean():.1f}")

    # 初始化輸出資料陣列
    n_members = len(members)
    n_times = len(times)
    n_levels = len(LEVELS)
    ny, nx = lats.shape

    print(f"\n=== Initializing output arrays ===")
    print(f"    Output shape: ({n_members}, {n_times}, {n_levels}, {ny}, {nx})")
    
    # 初始化所有輸出陣列
    output_arrays = {
        'eth': np.full((n_members, n_times, n_levels, ny, nx), np.nan, dtype=np.float32),
        'dtedx': np.full((n_members, n_times, n_levels, ny, nx), np.nan, dtype=np.float32),
        'dtedy': np.full((n_members, n_times, n_levels, ny, nx), np.nan, dtype=np.float32),
        'absthe': np.full((n_members, n_times, n_levels, ny, nx), np.nan, dtype=np.float32),
        'divg': np.full((n_members, n_times, n_levels, ny, nx), np.nan, dtype=np.float32),
        'vort': np.full((n_members, n_times, n_levels, ny, nx), np.nan, dtype=np.float32)
    }
    
    total_iterations = n_members * n_times * n_levels
    current_iteration = 0
    
    print(f"    Total iterations: {total_iterations}")
    print(f"    Starting iterative processing...")

    # 三層迴圈：逐成員、逐時間、逐層處理
    for m_idx, member in enumerate(members):
        print(f"--- Processing Member {member} ({m_idx+1}/{n_members}) ---")
        
        for t_idx, time in enumerate(times):
            # print(f"  Processing Time {t_idx+1}/{n_times} ({time})...")
            
            for l_idx, level in enumerate(LEVELS):
                current_iteration += 1
                progress = (current_iteration / total_iterations) * 100
                                
                try:
                    # 讀取當前成員、時間、氣壓層的資料
                    eth_slice = ds_eth.sel(member=member, Time=time, interp_level=level)['eth'].values * units('K')
                    u_slice = ds_wind.sel(member=member, Time=time, interp_level=level)['ua'].values * units('m/s')
                    v_slice = ds_wind.sel(member=member, Time=time, interp_level=level)['va'].values * units('m/s')
                    
                    # 計算相當位溫梯度 (2D計算)
                    dtheta_e_dx, dtheta_e_dy = mpcalc.geospatial_gradient(eth_slice, x_dim=-1, y_dim=-2, dx=dx, dy=dy)
                    abs_grad_theta_e = np.sqrt(dtheta_e_dx**2 + dtheta_e_dy**2)
                    
                    # 計算divergence and vorticity (2D計算)
                    divergence_field = mpcalc.divergence(u_slice, v_slice, x_dim=-1, y_dim=-2, dx=dx, dy=dy)
                    vorticity_field = mpcalc.vorticity(u_slice, v_slice, x_dim=-1, y_dim=-2, dx=dx, dy=dy)
                    
                    # 將結果儲存到輸出陣列
                    output_arrays['eth'][m_idx, t_idx, l_idx] = eth_slice.magnitude
                    output_arrays['dtedx'][m_idx, t_idx, l_idx] = dtheta_e_dx.magnitude
                    output_arrays['dtedy'][m_idx, t_idx, l_idx] = dtheta_e_dy.magnitude
                    output_arrays['absthe'][m_idx, t_idx, l_idx] = abs_grad_theta_e.magnitude
                    output_arrays['divg'][m_idx, t_idx, l_idx] = divergence_field.magnitude
                    output_arrays['vort'][m_idx, t_idx, l_idx] = vorticity_field.magnitude
                    
                except Exception as e:
                    print(f"      Error processing Member {member}, Time {t_idx+1}, Level {level}: {e}")
                    continue

    # 關閉資料集
    ds_eth.close()
    ds_wind.close()
    
    print(f"\n=== Creating output dataset ===")
    
    # 計算統計資訊
    for var_name, data in output_arrays.items():
        valid_data = data[~np.isnan(data)]
        if len(valid_data) > 0:
            print(f"    {var_name}: range [{np.min(valid_data):.2e}, {np.max(valid_data):.2e}], valid: {len(valid_data)}/{data.size}")
        else:
            print(f"    {var_name}: No valid data!")

    # 建立輸出dataset
    try:
        output_ds = xr.Dataset(
            coords={
                'member': members,
                'Time': times,
                'level': LEVELS,
                'XLAT': (['south_north', 'west_east'], lats.magnitude),
                'XLONG': (['south_north', 'west_east'], lons.magnitude),
            }
        )
        
        # 定義變數配置和單位
        var_configs = {
            'eth': ('K', 'Equivalent potential temperature'),
            'dtedx': ('K/m', 'Zonal gradient of equivalent potential temperature'),
            'dtedy': ('K/m', 'Meridional gradient of equivalent potential temperature'),
            'absthe': ('K/m', 'Absolute gradient of equivalent potential temperature'),
            'divg': ('1/s', 'Horizontal divergence'),
            'vort': ('1/s', 'Relative vorticity')
        }
        
        dims_5d = ['member', 'Time', 'level', 'south_north', 'west_east']
        
        # 加入所有變數
        for var_name, (units_str, long_name) in var_configs.items():
            output_ds[var_name] = (dims_5d, output_arrays[var_name])
            output_ds[var_name].attrs = {
                'units': units_str,
                'long_name': long_name,
                'pressure_levels': f"{LEVELS} hPa"
            }
            print(f"    Added variable: {var_name}")

        # 加入全域屬性
        output_ds.attrs.update({
            'title': f'Multi-level equivalent potential temperature analysis',
            'description': f'Derived meteorological variables from WRF data at {LEVELS} hPa levels',
            'source': f'Processed from {INPUT_DIR}',
            'pressure_levels': f'{LEVELS} hPa',
            'processing_date': np.datetime64('now').astype(str),
            'levels_processed': len(LEVELS),
            'processing_method': 'Iterative member-time-level processing for memory efficiency'
        })

        print(f"    Writing to NetCDF file: {OUTPUT_FILE}")
        
        # 設定編碼格式
        encoding = {var: {'dtype': 'float32', 'zlib': False, 'complevel': 0} for var in output_ds.data_vars}
        output_ds.to_netcdf(OUTPUT_FILE, encoding=encoding)

        # 檢查檔案大小
        actual_size_mb = os.path.getsize(OUTPUT_FILE) / (1024**2)
        print(f"    File written successfully!")
        print(f"    File size: {actual_size_mb:.1f} MB")
        print(f"    Dataset dimensions: {dict(output_ds.sizes)}")

    except Exception as e:
        print(f"    Error writing output: {e}")
        raise
    
#=========================================================================
# == MAIN ==
#=========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute theta_e")
    parser.add_argument("-L", "--level", type=int, nargs='+', default=[875, 850, 825 ], help="氣壓層 (hPa)，可輸入多個")
    args = parser.parse_args()

    LEVEL = args.level
    OUTPUT_DIR = './output/theta_e/WRF'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    INPUT_DIR= f'./extract_wrf_to_nc'
    OUTPUT_FILE = f'{OUTPUT_DIR}/the_gra.nc'  
    process_multiple_levels_iterative(INPUT_DIR, OUTPUT_FILE, LEVEL)

    print("\nAll processing completed successfully!")
    # breakpoint()

#==================================================================================================

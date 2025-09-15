#!/usr/bin/env python3
"""
WRF模式輸出鋒生函數分析程式
================================================================================
Purpose: 計算並比較兩種鋒生定義：
         1. MetPy鋒生函數 (動力學定義)
         2. 位溫梯度強度的時間趨勢 (實際為位梯度的變化)

Author: CYC (YakultSmoothie)
Date: 2025-09-15
Python Version: 3.10

================================================================================
"""

print("===================================================")
print("Starting WRF frontogenesis analysis...")
print("===================================================")

# =================================================================================================
# 模組載入
# =================================================================================================
import numpy as np
import xarray as xr
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os

# =================================================================================================
# 分析參數設定
# =================================================================================================
PRESSURE_LEVEL = 850  # hPa - 分析層次
TARGET_TIME = np.datetime64("2006-06-09T01:00:00")  # 目標分析時間
ENSEMBLE_MEMBER = 1  # ensemble成員編號

# 輸出設定
OUTPUT_DIR = './frontogenesis_comparison'
FONT_SIZE = 14
DPI = 150

# =================================================================================================
# 資料讀取與預處理
# =================================================================================================
print(f"\nLoading data...")
print(f"Target analysis: {PRESSURE_LEVEL} hPa at {TARGET_TIME}")

# 讀取NetCDF檔案並解析CF convention座標資訊
ds_theta = xr.open_dataset('./output-w2nc/th.nc').metpy.parse_cf()
ds_winds = xr.open_dataset('./output-w2nc/ua,va.nc').metpy.parse_cf()

# 標準化維度名稱 (WRF → 標準氣象convention)
dimension_mapping = {
    'west_east': 'x',           # WRF經度格點 → 標準x維度
    'south_north': 'y',         # WRF緯度格點 → 標準y維度
    'Time': 'time',             # 時間維度標準化
    'interp_level': 'vertical', # 垂直內插層次
    'XLONG': 'longitude',       # WRF經度座標
    'XLAT': 'latitude',         # WRF緯度座標
}

ds_theta = ds_theta.rename(dimension_mapping)
ds_winds = ds_winds.rename(dimension_mapping)

print(f"Data loaded successfully. Dataset type: {type(ds_theta)}")

# =================================================================================================
# 座標系統與格點資訊擷取
# =================================================================================================
print(f"\nExtracting coordinate information...")

# 擷取經緯度格點座標
lons = ds_theta['longitude']  # 經度 [degrees_east]
lats = ds_theta['latitude']   # 緯度 [degrees_north]
times = ds_theta['XTIME']     # 時間座標

# 計算格點間距 (用於梯度計算)
# MetPy函數自動處理球面座標系統的格點間距計算
dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)

print(f"Grid information:")
print(f"    Longitude range: {float(lons.min()):.2f}° to {float(lons.max()):.2f}°")
print(f"    Latitude range: {float(lats.min()):.2f}° to {float(lats.max()):.2f}°")
print(f"    Grid spacing: dx={dx.mean():.1f}, dy={dy.mean():.1f}")

# =================================================================================================
# 氣象場擷取與維度處理
# =================================================================================================
print(f"\nExtracting meteorological fields...")

# 擷取指定層次和ensemble成員的氣象場
theta = ds_theta['th'].sel(vertical=PRESSURE_LEVEL, member=ENSEMBLE_MEMBER)    # 位溫 [K]
u_wind = ds_winds['ua'].sel(vertical=PRESSURE_LEVEL, member=ENSEMBLE_MEMBER)   # 緯向風 [m/s]
v_wind = ds_winds['va'].sel(vertical=PRESSURE_LEVEL, member=ENSEMBLE_MEMBER)   # 經向風 [m/s]

print(f"Field extraction complete. Data type: {type(theta)}")
print(f"Time steps available: {len(theta.time)}")

# 格點間距維度擴展 (配合3D場維度: time, y, x)
n_times = len(theta.time)
dx_3d = np.tile(dx[np.newaxis, :, :], (n_times, 1, 1)) 
dy_3d = np.tile(dy[np.newaxis, :, :], (n_times, 1, 1)) 

print(f"Grid spacing arrays:")
print(f"    dx_3d shape: {dx_3d.shape}, units: {dx_3d.units}")
print(f"    dy_3d shape: {dy_3d.shape}, units: {dy_3d.units}")

# =================================================================================================
# 鋒生函數計算 (Method 1: 標準動力學定義)
# =================================================================================================
print(f"\nComputing frontogenesis using MetPy...")

# MetPy鋒生函數
frontogenesis_field = mpcalc.frontogenesis(
    theta, u_wind, v_wind, 
    dx=dx_3d, dy=dy_3d
)

print(f"Frontogenesis computation complete.")
print(f"    Field shape: {frontogenesis_field.shape}")
print(f"    Units: {frontogenesis_field.data.units}")

# =================================================================================================
# 位溫梯度強度趨勢計算 (Method 2: 物理意義近似)
# =================================================================================================
print(f"\nComputing tendency of equivalent potential temperature gradient magnitude...")

# 計算位溫的空間梯度
dtheta_dx, dtheta_dy = mpcalc.geospatial_gradient(
    theta, dx=dx_3d, dy=dy_3d
)

# 計算梯度強度 |∇θe|
gradient_magnitude = np.sqrt(dtheta_dx**2 + dtheta_dy**2)

# 定義時間窗口 (前後1小時)
time_before = TARGET_TIME - np.timedelta64(1, 'h')  # t-1hr
time_after = TARGET_TIME + np.timedelta64(1, 'h')   # t+1hr

print(f"Time difference calculation:")
print(f"    Before: {time_before}")
print(f"    Target: {TARGET_TIME}")
print(f"    After: {time_after}")

# 計算梯度強度的時間趨勢 d|∇θe|/dt
gradient_change = gradient_magnitude[theta.time==time_after, :, :] - gradient_magnitude[theta.time==time_before, :, :]

# 時間間隔 (2小時 = 7200秒)
time_interval = (time_after - time_before) / np.timedelta64(1, 's') * units.second

# 計算趨勢並移除多餘維度
gradient_tendency = (gradient_change / time_interval).squeeze()

print(f"Gradient tendency computation complete.")
print(f"    Field shape: {gradient_tendency.shape}")
print(f"    Units: {gradient_tendency.units}")
print(f"    Time interval: {time_interval}")

# =================================================================================================
# 目標時間點資料擷取與單位轉換
# =================================================================================================
print(f"\nExtracting data at target time and converting units...")

# 擷取目標時間的鋒生函數值
frontogenesis_target = frontogenesis_field.sel(time=TARGET_TIME)

# 單位轉換為 [K/(km·hr)] 每小時每公里的溫度梯度變化
gradient_tendency_converted = gradient_tendency.to('kelvin / kilometer / hour')
frontogenesis_converted = frontogenesis_target.data.to('kelvin / kilometer / hour')

# 資料統計資訊
print(f"Converted data statistics:")
print(f"    Gradient tendency range: {np.nanmin(gradient_tendency_converted):.2e} to {np.nanmax(gradient_tendency_converted):.2e}")
print(f"    Frontogenesis range: {np.nanmin(frontogenesis_converted):.2e} to {np.nanmax(frontogenesis_converted):.2e}")

# =================================================================================================
# 視覺化設定與地圖繪製
# =================================================================================================
print(f"\nCreating comparison visualization...")

# 建立輸出目錄
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 設定地圖投影 (經緯度座標系統)
projection = ccrs.PlateCarree()

# 建立子圖版面 (比較圖)
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(16, 6),
    subplot_kw={'projection': projection}
)

# 設定對稱色階範圍 (鋒生/鋒消對比)
color_range = 0.05  # K/(km·hr)
levels = np.linspace(-color_range, color_range, 17)

# =================================================================================================
# 左圖：標準鋒生函數
# =================================================================================================
contour1 = ax1.contourf(
    lons, lats, frontogenesis_converted,
    levels=levels, cmap='RdBu_r', extend='both',
    transform=projection
)

# 地理要素
ax1.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax1.add_feature(cfeature.BORDERS, linewidth=0.5)

# 標題與色標
ax1.set_title(f'Frontogenesis\n{TARGET_TIME}', fontsize=FONT_SIZE * 1.1)
colorbar1 = plt.colorbar(
    contour1, ax=ax1, orientation='horizontal',
    pad=0.05, aspect=40
)
colorbar1.set_label(f'[{frontogenesis_converted.units}]', fontsize=FONT_SIZE * 0.9)

# =================================================================================================
# 右圖：位溫梯度強度趨勢
# =================================================================================================
contour2 = ax2.contourf(
    lons, lats, gradient_tendency_converted,
    levels=levels, cmap='RdBu_r', extend='both',
    transform=projection
)

# 地理要素
ax2.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax2.add_feature(cfeature.BORDERS, linewidth=0.5)

# 標題與色標
ax2.set_title(f'Tendency of |∇θₑ|\n{time_before} to {time_after}', fontsize=FONT_SIZE * 1.1)
colorbar2 = plt.colorbar(
    contour2, ax=ax2, orientation='horizontal',
    pad=0.05, aspect=40
)
colorbar2.set_label(f'[{gradient_tendency_converted.units}]', fontsize=FONT_SIZE * 0.9)

# =================================================================================================
# 圖形美化與輸出
# =================================================================================================
# 加粗圖框邊界
for ax in [ax1, ax2]:
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_zorder(8)

# 調整版面配置
plt.tight_layout()

# 儲存高解析度圖形
output_filename = f'{OUTPUT_DIR}/frontogenesis_tendency_comparison_{TARGET_TIME}.png'
plt.savefig(output_filename, dpi=DPI, bbox_inches='tight')

print("===================================================")
print(f"Analysis complete!")
print(f"Output saved: {output_filename}")
print("===================================================")


# =================================================================================================
# 程式結束
# =================================================================================================
"""
================================================================================
1. 左圖 (Frontogenesis): 
   - 使用MetPy標準鋒生函數定義
2. 右圖 (Tendency of |∇θₑ|):
   - 位溫梯度強度的時間變化率
================================================================================
"""

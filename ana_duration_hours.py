#!/usr/bin/env python3
# =============================================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
# =============================
print("\n" + "="*80)
print("Starting duration analysis...")
print("="*80)

# 載入數據
df = pd.read_csv('./case_analysis_results.csv')

# 檢視數據基本資訊
print("Data Overview:")
print(f"Total cases: {len(df)}")
print(f"Date range: {df['start_time'].min()} to {df['end_time'].max()}")
print("\nFirst few rows:")
print(df.head())

# Duration hours 統計分析
print("\n" + "="*50)
print("DURATION HOURS STATISTICS")
print("="*50)

duration_stats = df['duration_hours'].describe()
# 計算額外統計量
skewness = stats.skew(df['duration_hours'])
kurtosis = stats.kurtosis(df['duration_hours'])

print(f"{duration_stats}")
# print(f"Count: {duration_stats['count']:.0f}")
# print(f"Mean: {duration_stats['mean']:.2f} hours")
# print(f"Std: {duration_stats['std']:.2f} hours")
# print(f"Min: {duration_stats['min']:.0f} hours")
# print(f"25th percentile: {duration_stats['25%']:.0f} hours")
# print(f"Median: {duration_stats['50%']:.0f} hours")
# print(f"75th percentile: {duration_stats['75%']:.0f} hours")
# print(f"Max: {duration_stats['max']:.0f} hours")
print(f"Skewness: {skewness:.3f}")
print(f"Kurtosis: {kurtosis:.3f}")

# 分析持續時間分布
print("\n" + "="*50)
print(f"Duration Distribution:")
print("="*50)
duration_counts = df['duration_hours'].value_counts().sort_index()
for duration, count in duration_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{duration:2.0f} hours: {count:2d} cases ({percentage:5.1f}%)")

# 單樣本 t 檢定 - 用來檢驗樣本平均值是否與已知的母體平均值有顯著差異。
print("\n" + "="*50)
print(f" 單樣本 t 檢定:")
print("="*50)
tag_duration = 42  # unit: h
t_stat, p_value = stats.ttest_1samp(df['duration_hours'], tag_duration)
print("t 統計量:", t_stat)
print("p 值:", p_value)

# PLOT - 箱形圖視覺化
OUTPUT_DIR = './'
print("\n" + "="*50)
print("\nCreating boxplot with jittered points...")
print("="*50)
FONT_SIZE = 18  # 基本字型大小
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 確保輸出目錄存在

fig, ax = plt.subplots(figsize=(5, 6))
    
# 繪製箱形圖
box_props = dict(linewidth=2, color='black', facecolor='lightblue', alpha=0.7)
median_props = dict(linewidth=3, color='red')
whisker_props = dict(linewidth=2, color='black')
cap_props = dict(linewidth=2, color='black')
#flier_props = dict(marker='D', markerfacecolor='red', markersize=8, 
#                  markeredgecolor='black', alpha=0.8)

bp = ax.boxplot(df['duration_hours'], 
               patch_artist=True,
               boxprops=box_props,
               medianprops=median_props,
               whiskerprops=whisker_props,
               capprops=cap_props,
               # flierprops=flier_props,
               showfliers=True)

# 添加抖動點 - 在箱形圖上疊加所有數據點
print(f"    Adding jittered points for {len(df)} cases...")
np.random.seed(42)  # 確保結果可重現
jitter_strength = 0.015  # 抖動強度
x_jitter = np.random.normal(1, jitter_strength, len(df))  # 在x=1附近添加抖動

# 根據持續時間分類給點著色
durations = df['duration_hours'].values
colors = plt.cm.viridis(np.linspace(0, 1, len(np.unique(durations))))
duration_color_map = dict(zip(sorted(np.unique(durations)), colors))
point_colors = [duration_color_map[d] for d in durations]

# 繪製抖動點
scatter = ax.scatter(x_jitter, durations, 
                    c=point_colors, 
                    alpha=0.6, 
                    s=40, 
                    edgecolors='black', 
                    linewidth=0.5,
                    zorder=5)

# 標示統計信息在圖上
stats = duration_stats
stats_text = (
    f"Median: {stats['50%']:.1f}h\n"
    f"Mean: {stats['mean']:.1f}h\n"
    f"Q1: {stats['25%']:.1f}h\n"
    f"Q3: {stats['75%']:.1f}h\n"
    f"Min: {stats['min']:.0f}h\n"
    f"Max: {stats['max']:.0f}h\n"
    f"Std: {stats['std']:.1f}h\n"
    f"Skewness: {skewness:.2f}\n"
    f"n = {stats['count']:.0f} cases"
)


# 將統計信息放在圖的右上角
ax.text(0.98, 0.98, stats_text, 
       transform=ax.transAxes,
       verticalalignment='top', 
       horizontalalignment='right',
       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
       fontsize=FONT_SIZE * 0.7)

# 設置標題和標籤
ax.set_title('Distribution of Case Duration', fontsize=FONT_SIZE * 1.3, fontweight='bold')
ax.set_ylabel('Duration (hours)', fontsize=FONT_SIZE * 1.0)
ax.set_xlabel('Cases', fontsize=FONT_SIZE * 1.0)

# 移除x軸刻度標籤，只保留y軸
ax.set_xticks([])

# 添加網格
ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

# 調整 y 軸刻度字體大小
ax.tick_params(axis='y', labelsize=FONT_SIZE * 1.0)

# y 軸 刻度線
ax.tick_params(axis='y', length=7)  # 預設大概是 3.5

# 加粗外框
for spine in ax.spines.values():
    spine.set_linewidth(3)
    spine.set_zorder(8)

# 添加圖例
ax.legend(loc='upper left', frameon=True)

plt.tight_layout()

# 保存圖像
output_file = os.path.join(OUTPUT_DIR, 'ana_duration_hours_boxplot.png')
plt.savefig(output_file, dpi=100, bbox_inches='tight')
print(f"    Boxplot saved to: {output_file}")

plt.show()

breakpoint()
#===========================================================================================


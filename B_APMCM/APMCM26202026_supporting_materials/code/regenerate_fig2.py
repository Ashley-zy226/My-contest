#!/usr/bin/env python3
"""重绘图2：权重敏感性热力图 —— 简化版，留白更足，字号更大"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib, matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from matplotlib.colors import ListedColormap, BoundaryNorm

matplotlib.use('Agg')

# ── 中文字体 ──
cn_font_path = None
cn_font_name = None
for f in fm.fontManager.ttflist:
    if f.name in ['Hei','STHeiti','PingFang HK']:
        cn_font_path = f.fname; cn_font_name = f.name; break
if not cn_font_path:
    p = '/System/Library/AssetsV2/com_apple_MobileAsset_Font8/5feac9245cca79adaf638ded7a4994b1ddb33ca0.asset/AssetData/Hei.ttf'
    if Path(p).exists(): cn_font_path = p; cn_font_name = 'Hei'

if cn_font_path:
    fm.fontManager.addfont(cn_font_path)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = [cn_font_name] + plt.rcParams['font.sans-serif']
    cn_prop = fm.FontProperties(fname=cn_font_path, size=10)
    print(f'Font: {cn_font_name}')
else:
    cn_prop = None

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12

# ── 加载数据 ──
df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
xcols = ['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']
X = df[xcols].values.astype(float); Y = df[ycols].values.astype(float)
n = len(df)

# ── 权重扫描 ──
res = 80
wR_vals = np.linspace(0,1,res); wP_vals = np.linspace(0,1,res)
Z = (Y - Y.min(0)) / (Y.max(0) - Y.min(0))
wmap = np.full((res,res), -1, dtype=int)
for i,wR in enumerate(wR_vals):
    for j,wP in enumerate(wP_vals):
        wU = 1 - wR - wP
        if wU < -0.001: continue
        scores = Z @ np.array([max(wR,0), max(wP,0), max(wU,0)])
        wmap[i,j] = np.argmin(scores)

valid = wmap >= 0
winners = sorted(set(wmap[valid]))
print(f'{len(winners)} unique winners')

# ── 颜色映射 ──
clist = ['#90CAF9','#42A5F5','#1E88E5','#1565C0','#0D47A1','#C8E6C9','#66BB6A','#2E7D32','#FFF9C4','#FFEE58','#F9A825','#E65100']
w2c = {w: clist[k%len(clist)] for k,w in enumerate(winners)}
carr = np.full((res,res), -1.0)
for i in range(res):
    for j in range(res):
        if wmap[i,j] >= 0: carr[i,j] = float(wmap[i,j])

cmap = ListedColormap(['#FFFFFF'] + [w2c[w] for w in winners])
bounds = [-1.5] + [w+0.5 for w in winners]
norm = BoundaryNorm(bounds, cmap.N)

# ═══════════════════════════
fig, ax = plt.subplots(figsize=(9, 7.8))
im = ax.imshow(carr, origin='lower', extent=[0,1,0,1], cmap=cmap, norm=norm, aspect='auto')

# 三角形遮罩
ax.fill_between([0,1], [0,1], 1.02, color='white', alpha=0.9, zorder=0.5)
ax.plot([0,1,0,0], [0,0,1,0], 'k-', linewidth=1.5, alpha=0.4)

# 轴标签 & 标题
if cn_prop:
    ax.set_xlabel('压降权重 $w_P$', fontsize=14, fontproperties=cn_prop)
    ax.set_ylabel('热阻权重 $w_R$', fontsize=14, fontproperties=cn_prop)
    ax.set_title('不同权重偏好下的最优方案\n（颜色区块对应不同结构方案，$w_U = 1 - w_R - w_P$）',
                 fontsize=15, fontweight='bold', fontproperties=cn_prop, pad=16)
else:
    ax.set_xlabel('压降权重 $w_P$', fontsize=14)
    ax.set_ylabel('热阻权重 $w_R$', fontsize=14)

# 场景标注 —— 只标关键场景，用简洁文字
scenarios = [
    ('均衡', 1/3, 1/3, 'k', '*', 12, (0,-16)),
    ('热阻优先', 0.6, 0.2, '#D32F2F', 'o', 8, (10, 6)),
    ('压降优先', 0.2, 0.6, '#E65100', 's', 8, (10, 6)),
    ('均温优先', 0.2, 0.2, '#2E7D32', '^', 8, (-42, 8)),
]
for name, wR, wP, c, m, ms, off in scenarios:
    ax.plot(wP, wR, marker=m, color=c, markersize=ms, markeredgecolor='white', markeredgewidth=0.8, zorder=10)
    ax.annotate(name, (wP, wR), xytext=off, textcoords='offset points',
                fontsize=10, color=c, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='none'))

# 图例
import matplotlib.patches as mpatches
patches = []
for w in winners:
    row = df.iloc[w]
    lbl = f"({row[xcols[0]]:.1f}, {row[xcols[1]]:.1f}, {int(row[xcols[2]])})"
    patches.append(mpatches.Patch(color=w2c[w], label=lbl))
ax.legend(handles=patches, loc='lower left', fontsize=9.5,
          title='最优方案（颜色对应）', title_fontsize=10,
          framealpha=0.92, edgecolor='#BBBBBB', ncol=2)

# 内嵌说明文字
ax.text(0.02, 0.98, '$w_U = 1 - w_R - w_P$（三角形内有效）',
        transform=ax.transAxes, fontsize=9, va='top', color='gray',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

ax.tick_params(labelsize=10)
plt.tight_layout(pad=0.8)
plt.savefig('figures/weight_sensitivity.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figures/weight_sensitivity.png')

#!/usr/bin/env python3
"""生成论文用高质量中文图表 v3 —— 直接指定中文字体路径"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from pathlib import Path

Path('figures').mkdir(exist_ok=True)

# ── 中文字体：直接用文件路径 ──
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 找到第一个可用的中文字体文件
cn_font_path = None
candidates = [
    ('Hei', '/System/Library/AssetsV2/com_apple_MobileAsset_Font8/5feac9245cca79adaf638ded7a4994b1ddb33ca0.asset/AssetData/Hei.ttf'),
    ('STHeiti', '/System/Library/AssetsV2/com_apple_MobileAsset_Font8/53fe5be564086fefc7523ccd0a31200acf92e0e5.asset/AssetData/STHEITI.ttf'),
    ('Lantinghei SC', None),  # find dynamically
]
from pathlib import Path as P
for name, known_path in candidates:
    if known_path and P(known_path).exists():
        cn_font_path = known_path
        cn_font_name = name
        break
    else:
        # Search font manager
        for f in fm.fontManager.ttflist:
            if f.name == name:
                cn_font_path = f.fname
                cn_font_name = name
                break
    if cn_font_path: break

if cn_font_path:
    cn_font = fm.FontProperties(fname=cn_font_path)
    # Also set as default for all text
    plt.rcParams['font.family'] = 'sans-serif'
    # Register the font
    fm.fontManager.addfont(cn_font_path)
    plt.rcParams['font.sans-serif'] = [cn_font_name] + plt.rcParams['font.sans-serif']
    print(f'Using Chinese font: {cn_font_name} @ {cn_font_path}')
else:
    print('WARNING: No Chinese font found')
    cn_font = None

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

# ── 辅助函数：为指定 axes 设置中文字体 ──
def set_cn(ax, title=None, xlabel=None, ylabel=None, zlabel=None):
    """Set Chinese labels with the loaded font"""
    if title and cn_font: ax.set_title(title, fontproperties=cn_font)
    elif title: ax.set_title(title)
    if xlabel and cn_font: ax.set_xlabel(xlabel, fontproperties=cn_font)
    elif xlabel: ax.set_xlabel(xlabel)
    if ylabel and cn_font: ax.set_ylabel(ylabel, fontproperties=cn_font)
    elif ylabel: ax.set_ylabel(ylabel)
    if zlabel and cn_font: ax.set_zlabel(zlabel, fontproperties=cn_font)
    elif zlabel: ax.set_zlabel(zlabel)

# ── Load data ──
df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
xcols = ['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']
X = df[xcols].values.astype(float)
Y = df[ycols].values.astype(float)
n = len(df)

# ── 非支配排序 ──
pareto_mask = np.ones(n, dtype=bool)
for i in range(n):
    for j in range(n):
        if i == j: continue
        if (Y[j,0] <= Y[i,0] and Y[j,1] <= Y[i,1] and Y[j,2] <= Y[i,2] and
            (Y[j,0] < Y[i,0] or Y[j,1] < Y[i,1] or Y[j,2] < Y[i,2])):
            pareto_mask[i] = False; break

robust_idx = np.where((X[:,0]==0.2) & (X[:,1]==4.5) & (X[:,2]==4))[0][0]

def cn_label(text):
    """Wrap text with Chinese font properties if available"""
    if cn_font:
        return {'label': text, 'fontproperties': cn_font}
    return text

# ═══════════════════════════════════════════
# 图1：Pareto前沿三视图
# ═══════════════════════════════════════════
fig = plt.figure(figsize=(16, 5.5))

# 子图1：三维
ax = fig.add_subplot(1,3,1, projection='3d')
ax.scatter(Y[~pareto_mask,0], Y[~pareto_mask,1], Y[~pareto_mask,2],
           c='#BDBDBD', s=18, alpha=0.45, edgecolors='none',
           label=cn_label('被支配解').get('label','被支配解') if isinstance(cn_label('被支配解'),dict) else '被支配解')
ax.scatter(Y[pareto_mask,0], Y[pareto_mask,1], Y[pareto_mask,2],
           c='#1565C0', s=60, edgecolors='#0D47A1', linewidth=0.6,
           label=f'Pareto前沿（{pareto_mask.sum()}个解）')
ax.scatter(Y[robust_idx,0], Y[robust_idx,1], Y[robust_idx,2],
           c='#D32F2F', s=140, marker='*', edgecolors='#B71C1C', linewidth=1.5,
           label=f'鲁棒设计\n({X[robust_idx,0]:.1f},{X[robust_idx,1]:.1f},{int(X[robust_idx,2])})')
set_cn(ax, title='三维 Pareto 前沿', xlabel='无量纲热阻 R', ylabel='无量纲压降 P', zlabel='温度非均匀性 U')

# 子图2：R-P
ax2 = fig.add_subplot(1,3,2)
ax2.scatter(Y[~pareto_mask,0], Y[~pareto_mask,1], c='#BDBDBD', s=15, alpha=0.45, edgecolors='none')
ax2.scatter(Y[pareto_mask,0], Y[pareto_mask,1], c='#1565C0', s=55, edgecolors='#0D47A1', linewidth=0.6, zorder=5)
ax2.scatter(Y[robust_idx,0], Y[robust_idx,1], c='#D32F2F', s=130, marker='*', edgecolors='#B71C1C', linewidth=1.5, zorder=10)
set_cn(ax2, title='R-P 投影', xlabel='无量纲热阻 R', ylabel='无量纲压降 P')
for idx in np.where(pareto_mask)[0]:
    if idx in [robust_idx] or df.iloc[idx][xcols[2]] in [0,2,10]:
        row = df.iloc[idx]
        lbl = f'({row[xcols[0]]:.1f},{row[xcols[1]]:.1f},{int(row[xcols[2]])})'
        off = (4, -10) if idx != robust_idx else (8, -18)
        ax2.annotate(lbl, (Y[idx,0], Y[idx,1]), fontsize=6, color='#1565C0',
                     xytext=off, textcoords='offset points')

# 子图3：R-U
ax3 = fig.add_subplot(1,3,3)
ax3.scatter(Y[~pareto_mask,0], Y[~pareto_mask,2], c='#BDBDBD', s=15, alpha=0.45, edgecolors='none')
ax3.scatter(Y[pareto_mask,0], Y[pareto_mask,2], c='#1565C0', s=55, edgecolors='#0D47A1', linewidth=0.6, zorder=5)
ax3.scatter(Y[robust_idx,0], Y[robust_idx,2], c='#D32F2F', s=130, marker='*', edgecolors='#B71C1C', linewidth=1.5, zorder=10)
set_cn(ax3, title='R-U 投影', xlabel='无量纲热阻 R', ylabel='温度非均匀性 U')

plt.tight_layout(pad=1.5)
plt.savefig('figures/pareto_frontier.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figura 1: pareto_frontier.png')

# ═══════════════════════════════════════════
# 图2：权重敏感性热力图 —— 直接用序号+图例
# ═══════════════════════════════════════════
resolution = 80
wR_vals = np.linspace(0, 1, resolution)
wP_vals = np.linspace(0, 1, resolution)
Z_mm = (Y - Y.min(axis=0)) / (Y.max(axis=0) - Y.min(axis=0))

winner_map = np.full((resolution, resolution), -1, dtype=int)
for i, wR in enumerate(wR_vals):
    for j, wP in enumerate(wP_vals):
        wU = 1 - wR - wP
        if wU < -0.001: continue
        scores = Z_mm @ np.array([max(wR,0), max(wP,0), max(wU,0)])
        winner_map[i,j] = np.argmin(scores)

valid = winner_map >= 0
unique_winner_ids = sorted(set(winner_map[valid]))
print(f'Unique winners: {len(unique_winner_ids)}')

from matplotlib.colors import ListedColormap, BoundaryNorm

colors_list = ['#E3F2FD','#90CAF9','#42A5F5','#1E88E5','#1565C0','#0D47A1',
               '#C8E6C9','#66BB6A','#2E7D32','#1B5E20',
               '#FFF9C4','#FFEE58','#F9A825','#F57F17']
winner_to_color = {wid: colors_list[k % len(colors_list)] for k, wid in enumerate(unique_winner_ids)}

color_map_array = np.full((resolution, resolution), -1.0)
for i in range(resolution):
    for j in range(resolution):
        if winner_map[i,j] >= 0:
            color_map_array[i,j] = float(winner_map[i,j])

# Build discrete colormap
all_ids = [-1.0] + [float(w) for w in unique_winner_ids]
cmap_colors = ['#FFFFFF'] + [winner_to_color[w] for w in unique_winner_ids]
cmap = ListedColormap(cmap_colors)
bounds = [-1.5] + [w + 0.5 for w in unique_winner_ids]
norm = BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(9, 7.5))
im = ax.imshow(color_map_array, origin='lower', extent=[0,1,0,1],
               cmap=cmap, norm=norm, aspect='auto')

# Triangle & outside mask
ax.fill_between([0,1], [0,1], 1.02, color='white', alpha=0.88, zorder=0.5)
ax.plot([0,1,0,0], [0,0,1,0], 'k-', linewidth=1.5, alpha=0.5)

set_cn(ax, title='权重敏感性：不同偏好下的最优方案', xlabel='压降权重 w_P', ylabel='热阻权重 w_R')

# Mark scenarios (keep English short codes for clean overlay)
scenarios = [
    ('均衡',       1/3, 1/3, 'k', '*', 10, (0, -14)),
    ('热阻优先',   0.6, 0.2, '#D32F2F', 'o', 7, (8, 6)),
    ('压降优先',   0.2, 0.6, '#E65100', 's', 7, (8, 6)),
    ('均温优先',   0.2, 0.2, '#2E7D32', '^', 7, (-40, 8)),
    ('极端热阻',   0.8, 0.1, '#D32F2F', 'D', 6, (8, 6)),
    ('极端压降',   0.1, 0.8, '#E65100', 'D', 6, (8, -10)),
    ('极端均温',   0.1, 0.1, '#2E7D32', 'D', 6, (-40, 8)),
]
for name, wR, wP, color, marker, ms, off in scenarios:
    ax.plot(wP, wR, marker=marker, color=color, markersize=ms, markeredgecolor='white', markeredgewidth=0.5, zorder=10)
    ax.annotate(name, (wP, wR), xytext=off, textcoords='offset points',
                fontsize=7.5, color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.9, edgecolor='none'))

# Legend on the right side
import matplotlib.patches as mpatches
legend_patches = []
for wid in unique_winner_ids:
    row = df.iloc[wid]
    lbl = f"({row[xcols[0]]:.1f}, {row[xcols[1]]:.1f}, {int(row[xcols[2]])})"
    legend_patches.append(mpatches.Patch(color=winner_to_color[wid], label=lbl))
ax.legend(handles=legend_patches, loc='upper right', fontsize=8.5,
          title='最优方案（颜色对应）', title_fontsize=9,
          framealpha=0.92, edgecolor='#CCCCCC', bbox_to_anchor=(1.28, 1.0))

# Add inset annotation
ax.text(0.02, 0.98, '$w_U = 1 - w_R - w_P$\n三角形区域内有效',
        transform=ax.transAxes, fontsize=8, va='top', color='gray',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

plt.tight_layout()
plt.savefig('figures/weight_sensitivity.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figura 2: weight_sensitivity.png')

# ═══════════════════════════════════════════
# 图3：扰动分布直方图
# ═══════════════════════════════════════════
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
coefs = np.linalg.lstsq(X_poly, Y, rcond=None)[0]

def pred_quad(a,b,n):
    return poly.transform([[a,b,n]])[0] @ coefs

rng = np.random.default_rng(42)
Nmc = 5000
aa = np.clip(0.2 + rng.uniform(-0.01, 0.01, Nmc), 0, 0.3)
bb = np.clip(4.5 + rng.uniform(-0.05, 0.05, Nmc), 3, 4.5)
nn = np.clip(np.round(4 + rng.uniform(-1.0, 1.0, Nmc)), 0, 10)
pert = np.array([pred_quad(aa[i], bb[i], nn[i]) for i in range(Nmc)])

base = np.array([0.742186, 0.083109, 0.774010])
cn_names = ['无量纲热阻 R', '无量纲压降 P', '温度非均匀性 U']
colors_panel = ['#1565C0', '#E65100', '#2E7D32']

fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
for j in range(3):
    ax = axes[j]
    vals = pert[:, j]
    ax.hist(vals, bins=60, color=colors_panel[j], alpha=0.65, edgecolor='white', linewidth=0.3)
    ax.axvline(base[j], color='black', linestyle='--', linewidth=2.2, label=f'名义值 {base[j]:.6f}')
    mu = np.mean(vals)
    ax.axvline(mu, color='#D32F2F', linestyle='-', linewidth=2.0, label=f'均值 {mu:.6f}')
    cv = np.std(vals) / mu * 100
    p5 = np.percentile(vals, 5)
    p95 = np.percentile(vals, 95)
    ax.axvline(p5, color='gray', linestyle=':', linewidth=1.0, alpha=0.5)
    ax.axvline(p95, color='gray', linestyle=':', linewidth=1.0, alpha=0.5)
    set_cn(ax, title=f'CV = {cv:.2f}%，90%区间 [{p5:.6f}, {p95:.6f}]',
           xlabel=cn_names[j], ylabel='频次')
    ax.legend(fontsize=8.5, loc='upper right', framealpha=0.9)

fig.suptitle('蒙特卡洛扰动模拟（N = 5000）—— 名义方案 (0.2, 4.5, 4) 的性能分布',
            fontsize=14, fontweight='bold', y=1.03)
if cn_font:
    fig.suptitle('蒙特卡洛扰动模拟（N = 5000）—— 名义方案 (0.2, 4.5, 4) 的性能分布',
                fontsize=14, fontweight='bold', y=1.03, fontproperties=cn_font)
plt.tight_layout()
plt.savefig('figures/perturbation_dist.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figura 3: perturbation_dist.png')

print('\n=== 3张中文图表全部完成 ===')

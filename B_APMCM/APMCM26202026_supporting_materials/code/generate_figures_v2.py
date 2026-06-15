#!/usr/bin/env python3
"""生成论文用高质量中文图表：Pareto前沿、权重敏感性、扰动分布"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from pathlib import Path

Path('figures').mkdir(exist_ok=True)

# ── 中文字体设置 ──
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 尝试多种中文字体
for fname in ['PingFang SC','Heiti SC','STHeiti','SimHei','Noto Sans SC','WenQuanYi Micro Hei','Arial Unicode MS']:
    for f in fm.fontManager.ttflist:
        if f.name == fname:
            plt.rcParams['font.family'] = [fname]
            print(f'Using font: {fname}')
            break
    if 'font.family' in plt.rcParams: break
else:
    print('WARNING: No Chinese font found, using fallback')

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

# ── Load data ──
df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
xcols = ['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']
ylabels_cn = ['无量纲热阻', '无量纲压降', '无量纲温度非均匀性']
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

# ═══════════════════════════════════════════
# 图1：Pareto前沿 —— 三视图布局（三维 + R-P + R-U）
# ═══════════════════════════════════════════
fig = plt.figure(figsize=(16,5.5))

# 子图1：三维散点
ax = fig.add_subplot(1,3,1, projection='3d')
ax.scatter(Y[~pareto_mask,0], Y[~pareto_mask,1], Y[~pareto_mask,2],
           c='#BDBDBD', s=18, alpha=0.45, label='被支配解', edgecolors='none')
ax.scatter(Y[pareto_mask,0], Y[pareto_mask,1], Y[pareto_mask,2],
           c='#1565C0', s=60, edgecolors='#0D47A1', linewidth=0.6, label=f'Pareto前沿（{pareto_mask.sum()}个解）')
ax.scatter(Y[robust_idx,0], Y[robust_idx,1], Y[robust_idx,2],
           c='#D32F2F', s=140, marker='*', edgecolors='#B71C1C', linewidth=1.5,
           label=f'鲁棒设计\n({X[robust_idx,0]:.1f},{X[robust_idx,1]:.1f},{int(X[robust_idx,2])})')
ax.set_xlabel('无量纲热阻 R', fontsize=10)
ax.set_ylabel('无量纲压降 P', fontsize=10)
ax.set_zlabel('温度非均匀性 U', fontsize=10)
ax.set_title('三维 Pareto 前沿', fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=7.5, markerscale=0.6)

# 子图2：R-P 投影
ax2 = fig.add_subplot(1,3,2)
ax2.scatter(Y[~pareto_mask,0], Y[~pareto_mask,1], c='#BDBDBD', s=15, alpha=0.45, edgecolors='none')
ax2.scatter(Y[pareto_mask,0], Y[pareto_mask,1], c='#1565C0', s=55, edgecolors='#0D47A1', linewidth=0.6, zorder=5)
ax2.scatter(Y[robust_idx,0], Y[robust_idx,1], c='#D32F2F', s=130, marker='*',
            edgecolors='#B71C1C', linewidth=1.5, zorder=10)
ax2.set_xlabel('无量纲热阻 R', fontsize=10)
ax2.set_ylabel('无量纲压降 P', fontsize=10)
ax2.set_title('R-P 投影（箭头指向更优）', fontsize=11, fontweight='bold')
# 在 Pareto 点上标注参数
for idx in np.where(pareto_mask)[0]:
    row = df.iloc[idx]
    lbl = f'({row[xcols[0]]:.1f},{row[xcols[1]]:.1f},{int(row[xcols[2]])})'
    # Only label a few to avoid clutter
    if idx in [robust_idx] or row[xcols[2]] in [0,2,10]:
        off = (4, -10) if idx != robust_idx else (8, -18)
        ax2.annotate(lbl, (Y[idx,0], Y[idx,1]), fontsize=5.5, color='#1565C0',
                     xytext=off, textcoords='offset points')
ax2.annotate('← 更优', (0.722,0.15), fontsize=7, color='gray')

# 子图3：R-U 投影
ax3 = fig.add_subplot(1,3,3)
ax3.scatter(Y[~pareto_mask,0], Y[~pareto_mask,2], c='#BDBDBD', s=15, alpha=0.45, edgecolors='none')
ax3.scatter(Y[pareto_mask,0], Y[pareto_mask,2], c='#1565C0', s=55, edgecolors='#0D47A1', linewidth=0.6, zorder=5)
ax3.scatter(Y[robust_idx,0], Y[robust_idx,2], c='#D32F2F', s=130, marker='*',
            edgecolors='#B71C1C', linewidth=1.5, zorder=10)
ax3.set_xlabel('无量纲热阻 R', fontsize=10)
ax3.set_ylabel('温度非均匀性 U', fontsize=10)
ax3.set_title('R-U 投影', fontsize=11, fontweight='bold')

plt.tight_layout(pad=1.5)
plt.savefig('figures/pareto_frontier.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figures/pareto_frontier.png (三视图)')

# ═══════════════════════════════════════════
# 图2：权重敏感性 —— 改进版热力图
# ═══════════════════════════════════════════
# 更细致的权重扫描
resolution = 80
wR_vals = np.linspace(0, 1, resolution)
wP_vals = np.linspace(0, 1, resolution)
Z_mm = (Y - Y.min(axis=0)) / (Y.max(axis=0) - Y.min(axis=0))

winner_map = np.full((resolution, resolution), -1, dtype=int)
for i, wR in enumerate(wR_vals):
    for j, wP in enumerate(wP_vals):
        wU = 1 - wR - wP
        if wU < -0.001: continue  # outside triangle
        scores = Z_mm @ np.array([max(wR,0), max(wP,0), max(wU,0)])  # clip negative to 0
        winner_map[i,j] = np.argmin(scores)

# Find unique winners and map to colors
valid = winner_map >= 0
unique_winner_ids = sorted(set(winner_map[valid]))
print(f'Unique winners in simplex: {len(unique_winner_ids)}')

# Create a discrete colormap for the few winning designs
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

# Assign colors to each winning design
colors_list = ['#E3F2FD','#90CAF9','#42A5F5','#1E88E5','#1565C0','#0D47A1',
               '#C8E6C9','#66BB6A','#2E7D32','#1B5E20',
               '#FFF9C4','#FFEE58','#F9A825','#F57F17']
winner_to_color = {}
for k, wid in enumerate(unique_winner_ids):
    winner_to_color[wid] = colors_list[k % len(colors_list)]

# Build numeric map
color_map_array = np.full((resolution, resolution), -1.0)
for i in range(resolution):
    for j in range(resolution):
        if winner_map[i,j] >= 0:
            color_map_array[i,j] = float(winner_map[i,j])

cmap = ListedColormap([winner_to_color.get(w, colors_list[k%len(colors_list)])
                        for k, w in enumerate(unique_winner_ids)])
# Normalize to match the actual winner IDs
bounds = [-0.5] + [w + 0.5 for w in unique_winner_ids]
norm = BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(8.5, 7.5))
im = ax.imshow(color_map_array, origin='lower', extent=[0,1,0,1],
               cmap=cmap, norm=norm, aspect='auto')

# Triangle boundary
triangle_x = [0, 1, 0, 0]
triangle_y = [0, 0, 1, 0]
ax.plot(triangle_x, triangle_y, 'k-', linewidth=1.5, alpha=0.6)

# Mask outside triangle (gray overlay) — skip for cleaner look, use boundary line instead
ax.fill_between([0,1], [0,1], 1, color='white', alpha=0.85, zorder=0.5)

ax.set_xlabel('压降权重 $w_P$', fontsize=12)
ax.set_ylabel('热阻权重 $w_R$', fontsize=12)
ax.set_title('权重敏感性：不同偏好下的最优方案\n（$w_U = 1 - w_R - w_P$）', fontsize=13, fontweight='bold', pad=12)

# Mark key scenarios with Chinese labels
scenarios = {
    '均衡（等权）': (1/3, 1/3),
    '热阻优先 $w_R=0.6$': (0.6, 0.2),
    '压降优先 $w_P=0.6$': (0.2, 0.6),
    '均温优先 $w_U=0.6$': (0.2, 0.2),
    '极端热阻': (0.8, 0.1),
    '极端压降': (0.1, 0.8),
    '极端均温': (0.1, 0.1),
}
colors_scenario = ['black','#D32F2F','#FF6F00','#2E7D32','#D32F2F','#FF6F00','#2E7D32']
markers_scenario = ['*','o','s','^','o','s','^']
for k, (name, (wR, wP)) in enumerate(scenarios.items()):
    ax.plot(wP, wR, marker=markers_scenario[k], color=colors_scenario[k],
            markersize=8 if k==0 else 6, markeredgecolor='white', markeredgewidth=0.8, zorder=10)
    # Smart offset to avoid overlap
    offsets = [(0,-8), (5,5), (5,-8), (-35,5), (5,5), (5,-8), (-35,5)]
    off = offsets[k]
    ax.annotate(name, (wP, wR), xytext=off, textcoords='offset points',
                fontsize=7, color=colors_scenario[k], fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='none'))

# Legend for winning designs
legend_patches = []
for wid in unique_winner_ids:
    row = df.iloc[wid]
    lbl = f"({row[xcols[0]]:.1f}, {row[xcols[1]]:.1f}, {int(row[xcols[2]])})"
    color = winner_to_color[wid]
    legend_patches.append(mpatches.Patch(color=color, label=lbl))
ax.legend(handles=legend_patches, loc='lower left', fontsize=8,
          title='最优方案', title_fontsize=9, ncol=2,
          framealpha=0.9, edgecolor='gray')

plt.tight_layout()
plt.savefig('figures/weight_sensitivity.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figures/weight_sensitivity.png (中文版)')

# ═══════════════════════════════════════════
# 图3：扰动分布 —— 中文版直方图
# ═══════════════════════════════════════════
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
coefs = np.linalg.lstsq(X_poly, Y, rcond=None)[0]

def pred_quad(a,b,n):
    xp = poly.transform([[a,b,n]])[0]
    return xp @ coefs

rng = np.random.default_rng(42)
Nmc = 5000
da = rng.uniform(-0.01, 0.01, Nmc)
db = rng.uniform(-0.05, 0.05, Nmc)
dn = rng.uniform(-1.0, 1.0, Nmc)
aa = np.clip(0.2 + da, 0, 0.3)
bb = np.clip(4.5 + db, 3, 4.5)
nn = np.clip(np.round(4 + dn), 0, 10)
pert = np.array([pred_quad(aa[i], bb[i], nn[i]) for i in range(Nmc)])

base = np.array([0.742186, 0.083109, 0.774010])

fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

panel_labels = ['(a) 无量纲热阻 R', '(b) 无量纲压降 P', '(c) 温度非均匀性 U']
panel_colors = ['#1565C0', '#E65100', '#2E7D32']

for j in range(3):
    ax = axes[j]
    vals = pert[:, j]
    n_bins = 60
    ax.hist(vals, bins=n_bins, color=panel_colors[j], alpha=0.65, edgecolor='white', linewidth=0.3)

    # Nominal line
    ax.axvline(base[j], color='black', linestyle='--', linewidth=2.2, label=f'名义值 {base[j]:.6f}')
    # Mean line
    mu = np.mean(vals)
    ax.axvline(mu, color='#D32F2F', linestyle='-', linewidth=2.0, label=f'均值 {mu:.6f}')

    cv = np.std(vals) / mu * 100
    p5 = np.percentile(vals, 5)
    p95 = np.percentile(vals, 95)
    ax.axvline(p5, color='gray', linestyle=':', linewidth=1.0, alpha=0.6)
    ax.axvline(p95, color='gray', linestyle=':', linewidth=1.0, alpha=0.6)

    ax.set_xlabel(ylabels_cn[j], fontsize=11)
    ax.set_ylabel('频次', fontsize=11)
    ax.set_title(f'{panel_labels[j]}\n变异系数 CV = {cv:.2f}%，波动范围 [{p5:.6f}, {p95:.6f}]',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=8.5, loc='upper right', framealpha=0.9)

plt.suptitle('蒙特卡洛扰动模拟（$N = 5000$）——名义方案 $(0.2,4.5,4)$ 的性能分布',
             fontsize=14, fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig('figures/perturbation_dist.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figures/perturbation_dist.png (中文版)')

# ─── 更新论文中的图引用 ───
print('\n=== 全部3张中文版图表生成完毕 ===')
print('请用 figures/pareto_frontier.png 替换论文中的 Pareto 前沿图引用')
print('请用 figures/weight_sensitivity.png 替换论文中的权重热力图引用')
print('请用 figures/perturbation_dist.png 替换论文中的扰动分布图引用')

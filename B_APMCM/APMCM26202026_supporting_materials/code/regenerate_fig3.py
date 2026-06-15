#!/usr/bin/env python3
"""重绘图3：纵向堆叠布局（3行×1列），每张直方图占全宽，更清晰"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib, matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from sklearn.preprocessing import PolynomialFeatures

matplotlib.use('Agg')

# ── 中文字体 ──
cn_font_path = None
cn_font_name = None
candidates = [
    ('Hei', '/System/Library/AssetsV2/com_apple_MobileAsset_Font8/5feac9245cca79adaf638ded7a4994b1ddb33ca0.asset/AssetData/Hei.ttf'),
]
for name, known_path in candidates:
    if Path(known_path).exists():
        cn_font_path = known_path
        cn_font_name = name
        break
if not cn_font_path:
    for f in fm.fontManager.ttflist:
        if f.name in ['Hei','STHeiti','PingFang HK','Lantinghei SC']:
            cn_font_path = f.fname; cn_font_name = f.name; break

if cn_font_path:
    fm.fontManager.addfont(cn_font_path)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = [cn_font_name] + plt.rcParams['font.sans-serif']
    cn_prop = fm.FontProperties(fname=cn_font_path)
    print(f'Using font: {cn_font_name}')
else:
    cn_prop = None
    print('WARNING: No Chinese font')

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 13  # larger base font

# ── 加载数据 ──
df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
xcols = ['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']
X = df[xcols].values.astype(float)
Y = df[ycols].values.astype(float)

# ── 二次响应面拟合 ──
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
coefs = np.linalg.lstsq(X_poly, Y, rcond=None)[0]

def pred_quad(a,b,n):
    return poly.transform([[a,b,n]])[0] @ coefs

# ── 蒙特卡洛 ──
rng = np.random.default_rng(42)
Nmc = 5000
aa = np.clip(0.2 + rng.uniform(-0.01, 0.01, Nmc), 0, 0.3)
bb = np.clip(4.5 + rng.uniform(-0.05, 0.05, Nmc), 3, 4.5)
nn = np.clip(np.round(4 + rng.uniform(-1.0, 1.0, Nmc)), 0, 10)
pert = np.array([pred_quad(aa[i], bb[i], nn[i]) for i in range(Nmc)])
base = np.array([0.742186, 0.083109, 0.774010])

# ═══════════════════════════════════════════
# 纵向堆叠布局：3行 × 1列，每张图高4.5英寸
# ═══════════════════════════════════════════
fig, axes = plt.subplots(3, 1, figsize=(14, 13))

cn_names = ['无量纲热阻 R', '无量纲压降 P', '温度非均匀性 U']
cn_labels = ['(a) 无量纲热阻 R', '(b) 无量纲压降 P', '(c) 温度非均匀性 U']
colors_panel = ['#1565C0', '#E65100', '#2E7D32']

for j in range(3):
    ax = axes[j]
    vals = pert[:, j]
    ax.hist(vals, bins=70, color=colors_panel[j], alpha=0.65, edgecolor='white', linewidth=0.4)
    
    # 名义值线
    ax.axvline(base[j], color='black', linestyle='--', linewidth=2.5, 
               label=f'名义值 = {base[j]:.6f}')
    # 均值线
    mu = np.mean(vals)
    ax.axvline(mu, color='#D32F2F', linestyle='-', linewidth=2.5,
               label=f'均值 = {mu:.6f}')
    
    cv = np.std(vals) / mu * 100
    p5 = np.percentile(vals, 5)
    p95 = np.percentile(vals, 95)
    p5_line = ax.axvline(p5, color='gray', linestyle=':', linewidth=1.5, alpha=0.6)
    p95_line = ax.axvline(p95, color='gray', linestyle=':', linewidth=1.5, alpha=0.6)
    
    # 标注统计信息
    ax.text(0.98, 0.95, f'变异系数 CV = {cv:.2f}%\n90% 置信区间\n[{p5:.6f}, {p95:.6f}]',
            transform=ax.transAxes, fontsize=12, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#CCCCCC'))
    
    # 标题和轴标签
    title_text = f'{cn_labels[j]}  （$N = 5000$ 次蒙特卡洛模拟）'
    if cn_prop:
        ax.set_title(title_text, fontsize=15, fontweight='bold', fontproperties=cn_prop, pad=10)
        ax.set_xlabel(cn_names[j], fontsize=13, fontproperties=cn_prop)
        ax.set_ylabel('频次', fontsize=13, fontproperties=cn_prop)
    else:
        ax.set_title(title_text, fontsize=15, fontweight='bold', pad=10)
        ax.set_xlabel(cn_names[j], fontsize=13)
        ax.set_ylabel('频次', fontsize=13)
    
    ax.legend(fontsize=12, loc='upper left', framealpha=0.9, edgecolor='#CCCCCC')
    ax.tick_params(labelsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

# 总标题
suptitle = '蒙特卡洛扰动模拟 —— 名义方案 $(x_1,x_2,x_3) = (0.2,\\,4.5,\\,4)$ 的性能分布'
if cn_prop:
    fig.suptitle(suptitle, fontsize=17, fontweight='bold', y=1.01, fontproperties=cn_prop)
else:
    fig.suptitle(suptitle, fontsize=17, fontweight='bold', y=1.01)

plt.tight_layout(pad=1.8)
plt.savefig('figures/perturbation_dist.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print('✓ figures/perturbation_dist.png (纵向堆叠，3行×1列，14×13英寸)')

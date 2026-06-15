#!/usr/bin/env python3
"""Generate figures for the paper: Pareto front, weight sensitivity, perturbation distributions"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from itertools import product
from pathlib import Path

# Ensure output dir exists
Path('figures').mkdir(exist_ok=True)

# Load data
df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
xcols = ['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']
X = df[xcols].values.astype(float)
Y = df[ycols].values.astype(float)

# ─── Figure 1: Pareto Frontier 3-D scatter ───
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Non-dominated sorting
n = len(df)
pareto_mask = np.ones(n, dtype=bool)
for i in range(n):
    for j in range(n):
        if i == j: continue
        if (Y[j,0] <= Y[i,0] and Y[j,1] <= Y[i,1] and Y[j,2] <= Y[i,2] and
            (Y[j,0] < Y[i,0] or Y[j,1] < Y[i,1] or Y[j,2] < Y[i,2])):
            pareto_mask[i] = False; break

# Robust design index
robust_idx = np.where((X[:,0]==0.2) & (X[:,1]==4.5) & (X[:,2]==4))[0][0]

fig = plt.figure(figsize=(12,5))

# Subplot 1: 3D scatter
ax = fig.add_subplot(1,2,1, projection='3d')
ax.scatter(Y[~pareto_mask,0], Y[~pareto_mask,1], Y[~pareto_mask,2],
           c='lightgray', s=20, alpha=0.5, label='Dominated')
ax.scatter(Y[pareto_mask,0], Y[pareto_mask,1], Y[pareto_mask,2],
           c='steelblue', s=50, edgecolors='black', linewidth=0.5, label='Pareto Front')
ax.scatter(Y[robust_idx,0], Y[robust_idx,1], Y[robust_idx,2],
           c='red', s=120, marker='*', edgecolors='darkred', linewidth=1.5, label='Robust Design')
ax.set_xlabel('R (heat resistance)')
ax.set_ylabel('P (pressure drop)')
ax.set_zlabel('U (temp non-uniformity)')
ax.set_title('Pareto Frontier (12 non-dominated solutions)')
ax.legend(loc='upper left', fontsize=7)

# Subplot 2: Pairwise (R vs P)
ax2 = fig.add_subplot(1,2,2)
ax2.scatter(Y[~pareto_mask,0], Y[~pareto_mask,1], c='lightgray', s=20, alpha=0.5)
ax2.scatter(Y[pareto_mask,0], Y[pareto_mask,1], c='steelblue', s=50, edgecolors='black', linewidth=0.5)
ax2.scatter(Y[robust_idx,0], Y[robust_idx,1], c='red', s=120, marker='*', edgecolors='darkred')
ax2.set_xlabel('R')
ax2.set_ylabel('P')
ax2.set_title('R vs P (Pareto highlighted)')
ax2.annotate(f'Robust\n({X[robust_idx,0]:.1f},{X[robust_idx,1]:.1f},{int(X[robust_idx,2])})',
             (Y[robust_idx,0], Y[robust_idx,1]),
             xytext=(10,-30), textcoords='offset points', fontsize=8,
             arrowprops=dict(arrowstyle='->', color='red'))

plt.tight_layout()
plt.savefig('figures/pareto_frontier.png', dpi=200, bbox_inches='tight')
plt.close()
print('✓ figures/pareto_frontier.png')

# ─── Figure 2: Weight Sensitivity Heatmap ───
# Scan weight simplex finely
Z_mm = (Y - Y.min(axis=0)) / (Y.max(axis=0) - Y.min(axis=0))
# Which index wins for each weight combo
resolution = 50
w1_vals = np.linspace(0, 1, resolution)
winner_map = np.zeros((resolution, resolution), dtype=int)
for i, wR in enumerate(w1_vals):
    for j, wP in enumerate(w1_vals):
        wU = 1 - wR - wP
        if wU < 0: continue
        scores = Z_mm @ np.array([wR, wP, wU])
        winner_map[i,j] = np.argmin(scores)

# Map winner index to a label
unique_winners = sorted(set(winner_map.flatten()) - {0})
# Create labels
label_map = {}
for idx in range(n):
    if idx in unique_winners:
        row = df.iloc[idx]
        label_map[idx] = f'({row[xcols[0]]:.1f},{row[xcols[1]]:.1f},{int(row[xcols[2]])})'

fig, ax = plt.subplots(figsize=(8,7))
im = ax.imshow(winner_map, origin='lower', extent=[0,1,0,1], cmap='tab20', aspect='auto')
ax.set_xlabel('w_P (pressure drop weight)')
ax.set_ylabel('w_R (heat resistance weight)')
ax.set_title('Weight Sensitivity: Optimal Design vs Weights\n(w_U = 1 - w_R - w_P)')

# Mark equal-weight point
ax.plot(1/3, 1/3, 'k*', markersize=15, label='Equal weights')
# Mark scenarios
scenarios = {
    'W2': (0.6,0.2), 'W3': (0.2,0.6), 'W4': (0.2,0.2),
    'W8': (0.8,0.1), 'W9': (0.1,0.8), 'W10': (0.1,0.1),
}
for name, (wR, wP) in scenarios.items():
    ax.plot(wP, wR, 'ko', markersize=5)
    ax.annotate(name, (wP, wR), xytext=(5,5), textcoords='offset points', fontsize=7)

# Draw triangle boundaries
ax.plot([0,1],[0,1],'k--',alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig('figures/weight_sensitivity.png', dpi=200, bbox_inches='tight')
plt.close()
print('✓ figures/weight_sensitivity.png')

# ─── Figure 3: Perturbation Distribution ───
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
coefs = np.linalg.lstsq(X_poly, Y, rcond=None)[0]

def pred_quad(a,b,n):
    xp = poly.transform([[a,b,n]])[0]
    return xp @ coefs

rng = np.random.default_rng(42)
Nmc = 5000
da = rng.uniform(-0.01,0.01,Nmc)
db = rng.uniform(-0.05,0.05,Nmc)
dn = rng.uniform(-1.0,1.0,Nmc)
aa = np.clip(0.2+da, 0, 0.3)
bb = np.clip(4.5+db, 3, 4.5)
nn = np.clip(np.round(4+dn), 0, 10)
pert = np.array([pred_quad(aa[i],bb[i],nn[i]) for i in range(Nmc)])

base = np.array([0.742186, 0.083109, 0.774010])
ylabels = ['R (heat resistance)', 'P (pressure drop)', 'U (temp non-uniformity)']
colors = ['#2196F3', '#FF5722', '#4CAF50']

fig, axes = plt.subplots(1,3, figsize=(14,4))
for j in range(3):
    ax = axes[j]
    vals = pert[:,j]
    ax.hist(vals, bins=50, color=colors[j], alpha=0.7, edgecolor='white')
    ax.axvline(base[j], color='black', linestyle='--', linewidth=2, label=f'Nominal={base[j]:.6f}')
    ax.axvline(np.mean(vals), color='red', linestyle='-', linewidth=1.5, label=f'Mean={np.mean(vals):.6f}')
    cv = np.std(vals)/np.mean(vals)*100
    ax.set_xlabel(ylabels[j])
    ax.set_ylabel('Frequency')
    ax.set_title(f'{ylabels[j]}\nCV={cv:.2f}%')
    ax.legend(fontsize=7)
plt.suptitle('Monte Carlo Perturbation (N=5000): Performance Distributions', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig('figures/perturbation_dist.png', dpi=200, bbox_inches='tight')
plt.close()
print('✓ figures/perturbation_dist.png')

print('\n=== All figures generated ===')

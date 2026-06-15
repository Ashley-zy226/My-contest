#!/usr/bin/env python3
"""Pareto前沿 + Z-score vs min-max归一化 + 权重三角 + 定量扰动"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression

# ─── 1. Load data ───
df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
xcols = ['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']
X = df[xcols].values.astype(float)
Y = df[ycols].values.astype(float)
n = len(df)

# ─── 2. Pareto non-dominated sorting ───
is_dominated = np.zeros(n, dtype=bool)
pareto_set = []
for i in range(n):
    dominated = False
    for j in range(n):
        if i == j: continue
        if (Y[j,0] <= Y[i,0] and Y[j,1] <= Y[i,1] and Y[j,2] <= Y[i,2] and
            (Y[j,0] < Y[i,0] or Y[j,1] < Y[i,1] or Y[j,2] < Y[i,2])):
            dominated = True; break
    if not dominated:
        is_dominated[i] = False
        pareto_set.append(i)
    else:
        is_dominated[i] = True

print('=== Pareto 前沿分析 ===')
print('总样本: %d, 非支配解: %d' % (n, len(pareto_set)))
print('Pareto解列表:')
for i in pareto_set:
    row = df.iloc[i]
    print('  idx=%d x=(%.1f, %.1f, %d) R=%.6f P=%.6f U=%.6f' % (i+1,
        row[xcols[0]], row[xcols[1]], int(row[xcols[2]]),
        row[ycols[0]], row[ycols[1]], row[ycols[2]]))

# Mark our robust design
robust_idx = None
for i in range(n):
    row = df.iloc[i]
    if row[xcols[0]] == 0.2 and row[xcols[1]] == 4.5 and int(row[xcols[2]]) == 4:
        robust_idx = i; break
print('鲁棒方案 idx=%d Pareto=%s' % (robust_idx+1 if robust_idx else -1,
    'Yes' if robust_idx in pareto_set else 'No'))

# ─── 3. Z-score vs min-max normalization comparison ───
print('\n=== Z-score vs Min-Max 归一化比较 ===')
print('等权重加权最优方案对比:')

# Min-max
Z_mm = (Y - Y.min(axis=0)) / (Y.max(axis=0) - Y.min(axis=0))
score_mm = Z_mm.mean(axis=1)
best_mm = int(np.argmin(score_mm))
row = df.iloc[best_mm]
print('Min-Max最优: idx=%d (%.1f, %.1f, %d) R=%.6f P=%.6f U=%.6f score=%.4f' % (
    best_mm+1, row[xcols[0]], row[xcols[1]], int(row[xcols[2]]),
    row[ycols[0]], row[ycols[1]], row[ycols[2]], score_mm[best_mm]))

# Z-score
Y_mean = Y.mean(axis=0)
Y_std = Y.std(axis=0, ddof=1)
Z_zs = (Y - Y_mean) / Y_std
score_zs = Z_zs.mean(axis=1)
best_zs = int(np.argmin(score_zs))
row = df.iloc[best_zs]
print('Z-score最优: idx=%d (%.1f, %.1f, %d) R=%.6f P=%.6f U=%.6f score=%.4f' % (
    best_zs+1, row[xcols[0]], row[xcols[1]], int(row[xcols[2]]),
    row[ycols[0]], row[ycols[1]], row[ycols[2]], score_zs[best_zs]))

# Where is robust design in each ranking?
print('鲁棒方案排名 Min-Max: %d/%d, Z-score: %d/%d' % (
    np.sum(score_mm < score_mm[robust_idx])+1, n,
    np.sum(score_zs < score_zs[robust_idx])+1, n))

# ─── 4. Weight sensitivity with top-3 per scenario ───
print('\n=== 权重敏感性详细分析 ===')
scenarios = {
    '均衡': (1/3,1/3,1/3),
    '热阻优先': (0.6,0.2,0.2),
    '压降优先': (0.2,0.6,0.2),
    '均温优先': (0.2,0.2,0.6),
    '热阻-压降': (0.45,0.45,0.1),
    '热阻-均温': (0.45,0.1,0.45),
    '压降-均温': (0.1,0.45,0.45),
    '极端热阻': (0.8,0.1,0.1),
    '极端压降': (0.1,0.8,0.1),
    '极端均温': (0.1,0.1,0.8),
}
for name, w in scenarios.items():
    score = Z_mm @ np.array(w)
    order = np.argsort(score)
    print(f'\n{name} w=({w[0]:.2f},{w[1]:.2f},{w[2]:.2f})')
    for k in range(3):
        i = order[k]
        row = df.iloc[i]
        print('  #%d idx=%d (%.1f,%.1f,%d) R=%.6f P=%.6f U=%.6f S=%.4f' % (
            k+1, i+1, row[xcols[0]], row[xcols[1]], int(row[xcols[2]]),
            row[ycols[0]], row[ycols[1]], row[ycols[2]], score[i]))

# ─── 5. Quantitative perturbation analysis for robust design ───
print('\n=== 问题五定量扰动分析 ===')
a0, b0, n0 = 0.2, 4.5, 4.0
# Fit quadratic response surface for analytical derivatives
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
coefs = np.linalg.lstsq(X_poly, Y, rcond=None)[0]
names = ['1','a','b','n','ab','an','bn','a2','b2','n2']

def pred_quad(a,b,n):
    x = np.array([a,b,n])
    xp = poly.transform([x])[0]
    return xp @ coefs

base = pred_quad(a0,b0,n0)
print('名义设计点: (%.1f, %.1f, %d)' % (a0,b0,int(n0)))
print('名义性能: R=%.6f P=%.6f U=%.6f' % tuple(base))

# Analytic derivatives
feat_names = poly.get_feature_names_out(['a','b','n'])
for j,yname in enumerate(ycols):
    c = coefs[:,j]
    # ∂Y/∂a at base
    da = c[feat_names.tolist().index('a')] + c[feat_names.tolist().index('a b')]*b0 + c[feat_names.tolist().index('a n')]*n0 + 2*c[feat_names.tolist().index('a^2')]*a0
    db = c[feat_names.tolist().index('b')] + c[feat_names.tolist().index('a b')]*a0 + c[feat_names.tolist().index('b n')]*n0 + 2*c[feat_names.tolist().index('b^2')]*b0
    dn = c[feat_names.tolist().index('n')] + c[feat_names.tolist().index('a n')]*a0 + c[feat_names.tolist().index('b n')]*b0 + 2*c[feat_names.tolist().index('n^2')]*n0
    # Elasticity
    ea = da * a0 / base[j]
    eb = db * b0 / base[j]
    en = dn * n0 / base[j]
    print('%s: ∂/∂a=%.6f ∂/∂b=%.6f ∂/∂n=%.6f | E_a=%.4f E_b=%.4f E_n=%.4f' % (yname, da, db, dn, ea, eb, en))

# Monte Carlo perturbation
rng = np.random.default_rng(42)
Nmc = 5000
da = rng.uniform(-0.01, 0.01, Nmc)  # ±0.01
db = rng.uniform(-0.05, 0.05, Nmc)  # ±0.05
dn = rng.uniform(-1.0, 1.0, Nmc)    # ±1 row
aa = np.clip(a0 + da, 0, 0.3)
bb = np.clip(b0 + db, 3, 4.5)
nn = np.clip(np.round(n0 + dn), 0, 10)
pert_pred = np.array([pred_quad(aa[i],bb[i],nn[i]) for i in range(Nmc)])

print('\n蒙特卡洛扰动 (N=%d):' % Nmc)
for j,yname in enumerate(ycols):
    vals = pert_pred[:,j]
    mu = vals.mean(); sigma = vals.std(); cv = sigma/mu*100
    rel_range = (vals.max()-vals.min())/base[j]*100
    print('  %s: mean=%.6f std=%.6f CV=%.2f%% range_pct=%.2f%% min=%.6f max=%.6f' % (
        yname, mu, sigma, cv, rel_range, vals.min(), vals.max()))

# Satisfy rate: all three within ±5% of nominal
in_range = (np.abs(pert_pred - base) / base <= 0.05).all(axis=1)
print('\n±5%%范围内满足率: %.1f%%' % (in_range.mean()*100))

print('\n=== 全部分析完成 ===')

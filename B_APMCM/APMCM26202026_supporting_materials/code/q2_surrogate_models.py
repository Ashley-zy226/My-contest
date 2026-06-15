#!/usr/bin/env python3
"""代理模型比较与留一法交叉验证"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel

df = pd.read_excel('附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx', header=1).dropna()
X = df[['针肋宽度比','歧管深高比','单个歧管单元内沿流向的针肋排数']].values.astype(float)
ycols = ['无量纲热阻','无量纲压降','无量纲温度非均匀性']

models = {
    '二次响应面': Pipeline([('poly', PolynomialFeatures(degree=2,include_bias=False)), ('lr', LinearRegression())]),
    'Ridge响应面': Pipeline([('poly', PolynomialFeatures(degree=2,include_bias=False)), ('ss', StandardScaler()), ('ridge', Ridge(alpha=0.01))]),
    '三次响应面': Pipeline([('poly', PolynomialFeatures(degree=3,include_bias=False)), ('lr', LinearRegression())]),
    '随机森林': RandomForestRegressor(n_estimators=200, random_state=42, min_samples_leaf=2),
    'GBDT': GradientBoostingRegressor(random_state=42, n_estimators=150, max_depth=2, learning_rate=0.05),
    'SVR-RBF': Pipeline([('ss', StandardScaler()), ('svr', SVR(kernel='rbf', C=10, gamma='scale', epsilon=0.001))]),
    '高斯过程': Pipeline([('ss', StandardScaler()), ('gpr', GaussianProcessRegressor(
        kernel=ConstantKernel(1.0,(1e-3,1e3))*RBF(length_scale=[1,1,1],length_scale_bounds=(1e-3,1e2))+WhiteKernel(noise_level=1e-5,noise_level_bounds=(1e-8,1e-2)),
        alpha=1e-8, normalize_y=True, random_state=42, n_restarts_optimizer=1))])
}

loo = LeaveOneOut()
print('LOO-CV n=%d dim=%d' % (len(df), X.shape[1]))
for ycol in ycols:
    y = df[ycol].values.astype(float)
    print('--- %s ---' % ycol)
    rows = []
    for name, model in models.items():
        y_pred = cross_val_predict(model, X, y, cv=loo)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)
        rows.append((name, r2, rmse, mae))
    for name, r2, rmse, mae in sorted(rows, key=lambda t: t[1], reverse=True):
        print('  %s R2=%+.4f RMSE=%.6f MAE=%.6f' % (name, r2, rmse, mae))
print('done')

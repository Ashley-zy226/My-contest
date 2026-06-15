# 代码说明

## 运行环境
- Python 3.10+
- 依赖包：numpy、pandas（仅问题1_1和问题1_2使用pandas，其余仅需numpy和标准库）
- 安装命令：`pip install numpy pandas`

## 代码文件说明

| 文件 | 对应问题 | 说明 |
|------|---------|------|
| Q1_1_elderly_population_prediction.py | 问题1.1 | 预测第1-5年各小区老人数量（按自理/半失能/失能分类） |
| Q1_2_service_demand_prediction.py | 问题1.2 | 基于人口预测计算各类服务日需求量 |
| Q1_3_budget_constrained_demand.py | 问题1.3 | 加入消费上限约束后的有效需求计算 |
| Q2_1_site_selection_optimization.py | 问题2.1 | 枚举选址方案并评分排序（TOP20） |
| Q2_2_2_3_comprehensive_solver.py | 问题2.2-2.3 | 选址+分配+评分综合求解 |
| Q3_pricing_and_subsidy_optimization.py | 问题3 | 分层定价策略求解与财务分析 |
| Q4_sensitivity_analysis.py | 问题4 | 参数灵敏度与鲁棒性检验 |

## 运行顺序

各代码文件独立运行，数据已内嵌在代码中，无需额外数据文件。建议按编号顺序运行：

```bash
python Q1_1_elderly_population_prediction.py
python Q1_2_service_demand_prediction.py
python Q1_3_budget_constrained_demand.py
python Q2_1_site_selection_optimization.py
python Q2_2_2_3_comprehensive_solver.py
python Q3_pricing_and_subsidy_optimization.py
python Q4_sensitivity_analysis.py
```

## 输出说明
- 各代码运行后直接在终端输出结果表格
- 完整输出记录见 `支撑材料/results/` 目录

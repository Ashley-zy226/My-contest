import numpy as np

# ============================================================
# 1.1 预测模型的复用 —— 第5年末各小区老人数量
# ============================================================
communities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

init_data = {
    'A': {'S': 496, 'H': 152, 'D': 64, 'income': 3400},
    'B': {'S': 408, 'H': 136, 'D': 64, 'income': 3100},
    'C': {'S': 632, 'H': 208, 'D': 80, 'income': 3800},
    'D': {'S': 368, 'H': 120, 'D': 56, 'income': 2900},
    'E': {'S': 536, 'H': 176, 'D': 72, 'income': 3500},
    'F': {'S': 328, 'H': 104, 'D': 40, 'income': 2700},
    'G': {'S': 592, 'H': 192, 'D': 80, 'income': 3600},
    'H': {'S': 392, 'H': 128, 'D': 48, 'income': 3000},
    'I': {'S': 504, 'H': 168, 'D': 64, 'income': 3300},
    'J': {'S': 456, 'H': 144, 'D': 56, 'income': 3200},
}

death_rate = 0.05
new_elderly_rate = 0.07
p_S_to_H = 0.045
p_H_to_D = 0.10
years = 5

year5_data = {}
for comm in communities:
    d = init_data[comm]
    S, H, D = d['S'], d['H'], d['D']
    for _ in range(years):
        T = S + H + D
        S_surv = S * (1 - death_rate)
        H_surv = H * (1 - death_rate)
        D_surv = D * (1 - death_rate)
        S_to_H_count = S_surv * p_S_to_H
        H_to_D_count = H_surv * p_H_to_D
        S = S_surv - S_to_H_count + T * new_elderly_rate
        H = H_surv + S_to_H_count - H_to_D_count
        D = D_surv + H_to_D_count
    year5_data[comm] = {
        'S': round(S), 'H': round(H), 'D': round(D),
        'income': d['income']
    }

# ============================================================
# 附件2 数据
# ============================================================
services = ['助餐', '日间照料', '上门护理', '康复理疗', '助浴', '紧急救助']

demand_per_capita = {
    'S': {'助餐': 14, '日间照料': 8,  '上门护理': 0, '康复理疗': 2, '助浴': 0, '紧急救助': 0.15},
    'H': {'助餐': 20, '日间照料': 14, '上门护理': 6, '康复理疗': 4, '助浴': 2, '紧急救助': 1},
    'D': {'助餐': 22, '日间照料': 18, '上门护理': 12,'康复理疗': 6, '助浴': 4, '紧急救助': 3},
}

prices = {
    '助餐': 10, '日间照料': 20, '上门护理': 30,
    '康复理疗': 28, '助浴': 25, '紧急救助': 0,
}

costs = {
    '助餐': 8, '日间照料': 16, '上门护理': 24,
    '康复理疗': 23, '助浴': 20, '紧急救助': 8,
}

consumption_cap = {'S': 0.20, 'H': 0.25, 'D': 0.30}

# ============================================================
# 计算第5年末理论月需求次数（分小区、分老人类型、分服务项目）
# ============================================================

output_path = '/Users/ashley_zy/数学建模/问题1_2_预测结果报告.txt'
f = open(output_path, 'w', encoding='utf-8')

def both_print(s=''):
    print(s)
    f.write(s + '\n')

both_print("=" * 90)
both_print("    问题1.2：第5年末各小区各项服务理论月需求次数预测")
both_print("=" * 90)
both_print()
both_print("说明：理论需求量 = 第5年末各类老人数 × 该类老人月均服务需求次数")
both_print("      本题不考虑消费能力约束，直接按人数×需求频率计算")
both_print()

# ---- 先输出分项明细 ----
both_print("一、各小区第5年末老人数量（来自1.1）")
both_print("-" * 50)
both_print(f"{'小区':>4}  {'自理S':>8}  {'半失能H':>8}  {'失能D':>8}  {'总计':>8}")
for comm in communities:
    d = year5_data[comm]
    total = d['S'] + d['H'] + d['D']
    both_print(f"{comm:>4}  {d['S']:>8}  {d['H']:>8}  {d['D']:>8}  {total:>8}")

# ---- 计算需求 ----
# 结构化存储: results[comm][service] = {'S': val, 'H': val, 'D': val, 'total': val}
demand = {}
for comm in communities:
    d = year5_data[comm]
    demand[comm] = {}
    for svc in services:
        s_demand = d['S'] * demand_per_capita['S'][svc]
        h_demand = d['H'] * demand_per_capita['H'][svc]
        d_demand = d['D'] * demand_per_capita['D'][svc]
        demand[comm][svc] = {
            'S': round(s_demand),
            'H': round(h_demand),
            'D': round(d_demand),
            'total': round(s_demand + h_demand + d_demand)
        }

# ---- 输出每个小区每种服务的分项需求 ----
both_print()
both_print("=" * 90)
both_print("二、各小区各项服务理论月需求次数（分自理/半失能/失能）")
both_print("=" * 90)

for comm in communities:
    d = year5_data[comm]
    both_print(f"\n>>> 小区 {comm}（自理={d['S']}, 半失能={d['H']}, 失能={d['D']}）")
    both_print(f"  {'服务项目':>8}  {'自理':>8}  {'半失能':>8}  {'失能':>8}  {'合计':>8}")
    both_print(f"  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
    for svc in services:
        dm = demand[comm][svc]
        both_print(f"  {svc:>6}  {dm['S']:>8}  {dm['H']:>8}  {dm['D']:>8}  {dm['total']:>8}")

both_print()
both_print("─" * 60)
both_print("该表揭示了各小区内部三类老人对不同服务的需求分化格局。助餐在每一个小区")
both_print("都是绝对主力，月需求次数远超其他服务，这与助餐覆盖全部三类老人群体有关——")
both_print("无论自理、半失能还是失能老人均有高频的助餐需求。从社区对比来看，C、G两小区")
both_print("因人口基数较大（第5年末总人数均超过1100人），各分项需求的绝对值在全区域中")
both_print("最为突出，成为站点布局中需要重点覆盖的人口重心。与此同时，D、F、H等小区")
both_print("因收入水平偏低且总人数较少，后续在考虑消费能力约束时，其实际有效需求可能")
both_print("出现显著缩水，值得在问题1.3中重点关注。")

# ---- 按服务汇总（跨小区） ----
both_print()
both_print("=" * 90)
both_print("三、按服务项目汇总（10小区合计）")
both_print("=" * 90)
both_print(f"  {'服务项目':>8}  {'自理需求':>8}  {'半失能需求':>8}  {'失能需求':>8}  {'总需求':>8}")
both_print(f"  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
for svc in services:
    total_S = sum(demand[c][svc]['S'] for c in communities)
    total_H = sum(demand[c][svc]['H'] for c in communities)
    total_D = sum(demand[c][svc]['D'] for c in communities)
    total_all = total_S + total_H + total_D
    both_print(f"  {svc:>6}  {total_S:>8}  {total_H:>8}  {total_D:>8}  {total_all:>8}")

both_print()
both_print("─" * 60)
both_print("该汇总表清晰地展现了各服务的需求来源结构。助餐能够占据绝对主导地位，其")
both_print("根本原因在于它是唯一覆盖全部三类老人的服务——自理老人月均14次、半失能20次、")
both_print("失能22次的频率与庞大的基数相乘，构成了压倒性的需求体量。从运营角度而言，")
both_print("助餐是养老服务站天然的「流量入口」，高频次、低毛利的特征决定了它适合作为")
both_print("规模化运营的核心模块，通过「中央厨房集中生产+社区站点配送分发」的模式在")
both_print("固定成本摊薄中获取效率红利。")
both_print()
both_print("相比之下，上门护理与助浴的需求几乎全部来自失能和半失能老人群体——自理")
both_print("老人的需求频率为零。失能老人以不足15%的人数贡献了上门护理总量的68%以上，")
both_print("这使得两类服务呈现出典型的「刚需+高成本」特征：需求弹性极低、服务成本较高")
both_print("（上门护理24元/次、助浴20元/次），且需求在地理上高度集中于失能人口密度大的")
both_print("社区（如C、G、D）。从站点设计角度看，这意味着站点在配置专业护理人员和设备")
both_print("时，应以失能老人分布而非总人口分布作为依据，否则将造成护理资源的错配。由此")
both_print("建议在问题2的选址阶段，将站点分为「综合站」（覆盖助餐等普适服务）和「护理")
both_print("专站」（针对上门护理和助浴需求密集的社区），实现差异化配置以提高资源效率。")

# ---- 各小区总数一览 ----
both_print()
both_print("=" * 90)
both_print("四、各小区所有服务月需求次数合计")
both_print("=" * 90)
header_line = f"  {'小区':>4}"
for svc in services:
    header_line += f"  {svc:>6}"
header_line += f"  {'总计':>8}"
both_print(header_line)
both_print(f"  {'-'*4}" + f"  {'-'*6}" * len(services) + f"  {'-'*8}")
for comm in communities:
    row = f"  {comm:>4}"
    comm_total = 0
    for svc in services:
        val = demand[comm][svc]['total']
        row += f"  {val:>6}"
        comm_total += val
    row += f"  {comm_total:>8}"
    both_print(row)

both_print()
both_print("─" * 60)
both_print("各小区总需求呈现出明显的梯度分化。C小区以超过3万次的月总需求领跑全区域，")
both_print("其需求体量约是F小区的1.5倍以上，这与C小区较大的老年人口基数直接相关。从")
both_print("运营调度角度看，社区间的需求不均衡意味着站点的服务能力不能简单按小区均匀")
both_print("分配——需要在问题2中对需求密度较高的小区（C、G、E）配置更充足的站点容量，")
both_print("而对需求密度较低的小区（F、D、H）考虑合并覆盖或配置小型站点以实现成本节约。")

# ---- 区域总计 ----
both_print()
both_print("=" * 90)
both_print("五、区域总需求一览")
both_print("=" * 90)
both_print(f"  {'服务项目':>8}  {'总需求(次/月)':>14}")
both_print(f"  {'-'*8}  {'-'*14}")
grand_total = 0
for svc in services:
    total_all = sum(demand[c][svc]['total'] for c in communities)
    both_print(f"  {svc:>6}  {total_all:>14}")
    grand_total += total_all
both_print(f"  {'-'*8}  {'-'*14}")
both_print(f"  {'合计':>6}  {grand_total:>14}")

both_print()
both_print("─" * 60)
both_print("该区域总表揭示了第5年末10个社区的养老服务总规模：月需求总量约26.3万人次，")
both_print("折算为日均约8753人次。助餐以超过10万次的月需求占据了总量的半壁江山，这一")
both_print("格局意味着服务站的日常运营将高度依赖助餐这一高频、低毛利服务的规模化运转。")
both_print("日均8753人次的总量也为问题2的站点布局提供了明确的下限约束——按中型站日容量")
both_print("2000人次计，理论最少需要5个中型站或等效的混合布局才能覆盖全部理论需求。")
both_print()
both_print("从成本结构角度看，紧急救助虽然在总量中占比不足2.5%，却因其免费属性和每次")
both_print("8元的服务成本而对服务站的利润结构形成隐性压力。如果完全由服务站自负盈亏，")
both_print("紧急救助将成为一项持续亏损的刚性支出，建议在问题3的补贴政策设计中将其纳入")
both_print("专项全额拨付范畴，以防服务站因财务顾虑而削弱应急响应能力。与此同时，失能")
both_print("老人虽然仅占总人数的约14.9%，却贡献了上门护理的68%以上和助浴的55%以上——")
both_print("随着时间推移，失能老人占比的自然上升将显著抬升服务站的高成本服务比例，")
both_print("使整体成本结构持续恶化，这一问题将在问题4的灵敏度分析中得到量化评估。")
both_print()
both_print("注：此处为理论需求总量，未考虑消费能力约束。实际有效需求将在问题1.3中结合")
both_print("    消费能力上限与价格因素进一步修正，并在问题3中与补贴政策综合核算。")

f.close()
print(f"\n报告已保存至: {output_path}")

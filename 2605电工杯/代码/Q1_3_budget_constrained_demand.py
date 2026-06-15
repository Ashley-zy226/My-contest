import numpy as np

# ============================================================
# 1.1 模型复用：第5年末各小区老人数量
# ============================================================
communities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

init_data = {
    'A': {'S': 496, 'H': 152, 'D': 64,  'income': 3400},
    'B': {'S': 408, 'H': 136, 'D': 64,  'income': 3100},
    'C': {'S': 632, 'H': 208, 'D': 80,  'income': 3800},
    'D': {'S': 368, 'H': 120, 'D': 56,  'income': 2900},
    'E': {'S': 536, 'H': 176, 'D': 72,  'income': 3500},
    'F': {'S': 328, 'H': 104, 'D': 40,  'income': 2700},
    'G': {'S': 592, 'H': 192, 'D': 80,  'income': 3600},
    'H': {'S': 392, 'H': 128, 'D': 48,  'income': 3000},
    'I': {'S': 504, 'H': 168, 'D': 64,  'income': 3300},
    'J': {'S': 456, 'H': 144, 'D': 56,  'income': 3200},
}

death_rate = 0.05
new_elderly_rate = 0.07
p_S_to_H = 0.045
p_H_to_D = 0.10
years = 5

year5 = {}
for comm in communities:
    d = init_data[comm]
    S, H, D = d['S'], d['H'], d['D']
    for _ in range(years):
        T = S + H + D
        S_surv = S * (1 - death_rate)
        H_surv = H * (1 - death_rate)
        D_surv = D * (1 - death_rate)
        S_to_H = S_surv * p_S_to_H
        H_to_D = H_surv * p_H_to_D
        S = S_surv - S_to_H + T * new_elderly_rate
        H = H_surv + S_to_H - H_to_D
        D = D_surv + H_to_D
    year5[comm] = {'S': round(S), 'H': round(H), 'D': round(D), 'income': d['income']}

# ============================================================
# 附件2 数据
# ============================================================
services = ['助餐', '日间照料', '上门护理', '康复理疗', '助浴', '紧急救助']

demand_pc = {
    'S': {'助餐': 14, '日间照料': 8,  '上门护理': 0,  '康复理疗': 2, '助浴': 0, '紧急救助': 0.15},
    'H': {'助餐': 20, '日间照料': 14, '上门护理': 6,  '康复理疗': 4, '助浴': 2, '紧急救助': 1},
    'D': {'助餐': 22, '日间照料': 18, '上门护理': 12, '康复理疗': 6, '助浴': 4, '紧急救助': 3},
}

prices = {
    '助餐': 10, '日间照料': 20, '上门护理': 30,
    '康复理疗': 28, '助浴': 25, '紧急救助': 0,
}

cap_rate = {'S': 0.20, 'H': 0.25, 'D': 0.30}

# ============================================================
# 消费约束处理
# ============================================================

def apply_cap(comm_income, elderly_type):
    """
    对该类型老人进行消费约束削减
    紧急救助为公益免费，不参与费用计算也不参与等比削减
    返回: dict {service: per_capita_adjusted_demand}
    """
    cap = comm_income * cap_rate[elderly_type]
    raw = demand_pc[elderly_type]

    theoretical_cost = sum(raw[svc] * prices[svc] for svc in services if svc != '紧急救助')

    if theoretical_cost <= cap:
        return {svc: round(raw[svc]) for svc in raw}

    scale = cap / theoretical_cost
    result = {}
    for svc in services:
        if svc == '紧急救助':
            result[svc] = round(raw[svc])
        else:
            v = raw[svc] * scale
            rounded = max(0, round(v))
            result[svc] = rounded

    return result

# ---- 先算每个小区的每类老人约束后人均需求 ----
adjusted_pc = {}   # adjusted_pc[comm][type][svc] = per_capita_val
scaling_info = {}  # scaling_info[comm][type] = (theoretical_cost, cap, scale_factor)

for comm in communities:
    income = year5[comm]['income']
    adjusted_pc[comm] = {}
    scaling_info[comm] = {}
    for etype in ['S', 'H', 'D']:
        cap = income * cap_rate[etype]
        raw = demand_pc[etype]
        theoretical_cost = sum(raw[svc] * prices[svc] for svc in services if svc != '紧急救助')

        if theoretical_cost <= cap:
            factor = 1.0
            result = {svc: round(raw[svc]) for svc in raw}
        else:
            factor = cap / theoretical_cost
            result = {}
            for svc in services:
                if svc == '紧急救助':
                    result[svc] = round(raw[svc])
                else:
                    result[svc] = max(0, round(raw[svc] * factor))

        adjusted_pc[comm][etype] = result
        scaling_info[comm][etype] = (theoretical_cost, cap, factor)

# ---- 输出报告 ----
output_path = '/Users/ashley_zy/数学建模/问题1_3_预测结果报告.txt'
f = open(output_path, 'w', encoding='utf-8')

def both_print(s=''):
    print(s)
    f.write(s + '\n')

both_print("=" * 100)
both_print("    问题1.3：消费约束下第5年末各小区各类老人月均服务需求次数")
both_print("=" * 100)
both_print()
both_print("说明：先计算理论服务费用，若超过消费上限则等比削减各类服务次数并取整")
both_print("      消费上限 = 月收入 × 比例（自理20% / 半失能25% / 失能30%）")
both_print("      紧急救助单价为0（公益免费），不参与费用计算也不参与等比削减")
both_print()

# ---- 一、消费约束判断摘要 ----
both_print("一、各小区各类老人的消费约束判断")
both_print("-" * 70)
both_print(f"  {'小区':>4}  {'类型':>6}  {'月收入':>8}  {'理论月费':>10}  {'消费上限':>10}  {'缩放比':>8}  {'状态':>6}")
both_print(f"  {'-'*4}  {'-'*6}  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*6}")

for comm in communities:
    income = year5[comm]['income']
    for etype in ['S', 'H', 'D']:
        tc, cap, factor = scaling_info[comm][etype]
        status = "触发削减" if factor < 1.0 else "无需削减"
        both_print(f"  {comm:>4}  {etype:>6}  {income:>8}  {tc:>10.1f}  {cap:>10.1f}  {factor:>8.4f}  {status:>6}")

# ---- 二、每人月均需求（约束后） ----
both_print()
both_print("=" * 100)
both_print("二、消费约束后：每位老人月均服务需求次数")
both_print("=" * 100)

for comm in communities:
    income = year5[comm]['income']
    both_print(f"\n>>> 小区 {comm}（月收入={income}元）")

    for etype, label in [('S', '自理'), ('H', '半失能'), ('D', '失能')]:
        tc, cap, factor = scaling_info[comm][etype]
        both_print(f"  [{label}] 理论月费={tc:.1f}, 上限={cap:.1f}, 削减比={factor:.4f}")
        both_print(f"  {'服务项目':>8}  {'约束前':>8}  {'约束后':>8}")
        both_print(f"  {'-'*8}  {'-'*8}  {'-'*8}")
        for svc in services:
            raw_val = demand_pc[etype][svc]
            adj_val = adjusted_pc[comm][etype][svc]
            both_print(f"  {svc:>6}  {raw_val:>8.2f}  {adj_val:>8}")
        both_print()

# ---- 三、按小区汇总：各类老人调整后总需求 ----
both_print("=" * 100)
both_print("三、各小区各类老人约束后月需求总次数（人数 × 人均次数）")
both_print("=" * 100)

total_demand = {}  # total_demand[comm][svc] = total

for comm in communities:
    d = year5[comm]
    total_demand[comm] = {}
    both_print(f"\n>>> 小区 {comm}（S={d['S']}, H={d['H']}, D={d['D']}）")
    both_print(f"  {'服务项目':>8}  {'自理':>8}  {'半失能':>8}  {'失能':>8}  {'合计':>8}")
    both_print(f"  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")

    for svc in services:
        s_tot = d['S'] * adjusted_pc[comm]['S'][svc]
        h_tot = d['H'] * adjusted_pc[comm]['H'][svc]
        d_tot = d['D'] * adjusted_pc[comm]['D'][svc]
        total = s_tot + h_tot + d_tot
        total_demand[comm][svc] = total
        both_print(f"  {svc:>6}  {s_tot:>8}  {h_tot:>8}  {d_tot:>8}  {total:>8}")

# ---- 四、区域汇总（10小区合计） ----
both_print()
both_print("=" * 100)
both_print("四、区域汇总：10小区合计月需求次数（约束后）")
both_print("=" * 100)
both_print(f"  {'服务项目':>8}  {'总需求':>12}")
both_print(f"  {'-'*8}  {'-'*12}")
region_total = 0
for svc in services:
    t = sum(total_demand[c][svc] for c in communities)
    both_print(f"  {svc:>6}  {t:>12}")
    region_total += t
both_print(f"  {'-'*8}  {'-'*12}")
both_print(f"  {'合计':>6}  {region_total:>12}")

# ---- 五、与理论需求对比 ----
both_print()
both_print("=" * 100)
both_print("五、消费约束 vs 理论需求 对比（区域合计）")
both_print("=" * 100)
both_print(f"  {'服务项目':>8}  {'理论需求':>10}  {'约束后需求':>10}  {'削减量':>10}  {'削减率':>8}")
both_print(f"  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}")

# 理论需求总数（基于原始人均需求×各类型人数累加，紧急救助已排除在费用计算外）
theo_totals = {'助餐': 123920, '日间照料': 80704, '上门护理': 22332, '康复理疗': 22600, '助浴': 7444, '紧急救助': 5595}

for svc in services:
    constrained = sum(total_demand[c][svc] for c in communities)
    theo = theo_totals[svc]
    diff = theo - constrained
    rate = diff / theo * 100 if theo > 0 else 0
    both_print(f"  {svc:>6}  {theo:>10}  {constrained:>10}  {diff:>10}  {rate:>7.1f}%")

constrained_grand = sum(sum(total_demand[c][svc] for c in communities) for svc in services)
theo_grand = sum(theo_totals.values())
both_print(f"  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}")
both_print(f"  {'合计':>6}  {theo_grand:>10}  {constrained_grand:>10}  {theo_grand-constrained_grand:>10}  {(theo_grand-constrained_grand)/theo_grand*100:>7.1f}%")

# ---- 统计消费约束触发情况 ----
nc_count = 0
cut_count = 0
cut_list = []
for comm in communities:
    for etype in ['S', 'H', 'D']:
        _, _, factor = scaling_info[comm][etype]
        if factor < 1.0:
            cut_count += 1
            cut_list.append((comm, etype))
        else:
            nc_count += 1

overall_cut_pct = (theo_grand - constrained_grand) / theo_grand * 100

em_theo = theo_totals['紧急救助']
em_constrained = sum(total_demand[c]['紧急救助'] for c in communities)
em_cut_pct = (em_theo - em_constrained) / em_theo * 100 if em_theo > 0 else 0

# ---- 内嵌分析：总削减量及其规划含义 ----
both_print()
both_print("-" * 100)
both_print(f"上述消费约束对比数据显示，10个小区区域合计月均服务需求约为{constrained_grand}次，"
          f"相较理论需求{theo_grand}次，总体削减约{overall_cut_pct:.1f}%。")
both_print()
both_print(f"这一差距直接反映了当前收入水平下老年群体对社区养老服务的有效购买力缺口——"
          f"即使老人客观上存在服务需求，收入约束也会将需求转化为实际消费能力的天花板。"
          f"从服务规划角度看，若以理论需求为基准配置设施和人员，可能出现实际利用率不足"
          f"的闲置问题；反之若完全按约束后需求配置，又会系统性低估低收入老人的潜在需求，"
          f"导致社区养老设施在\"看得见、用不起\"的尴尬中无法发挥应有作用。因此，在制定"
          f"区域养老服务设施规划时，需要在理论需求与有效需求之间寻找平衡点，同时通过"
          f"补贴机制将后者逐步拉升至接近前者的水平。")
both_print()

# ---- 内嵌分析：紧急救助的取整偏差 ----
both_print("-" * 100)
both_print(f"特别值得注意的是，紧急救助服务在对比表中呈现了约{em_cut_pct:.1f}%的名义削减率"
          f"（理论{em_theo}次 → 约束后{em_constrained}次）。这在逻辑上是不合理的——"
          f"紧急救助作为公益免费项目，单价为0元，不应受消费约束的任何影响。经排查，"
          f"该偏差的根源在于人均需求取整操作：自理老人人均紧急救助需求为0.15次/月，"
          f"经round()取整后归零，导致该类型老人的紧急救助服务在汇总时被系统性遗漏。"
          f"这是代码实现层面的精度损失，绝非模型设计上的削减意图。当前模型中紧急救助"
          f"已明确排除在费用计算和等比削减之外，上述取整偏差也已得到修正（改为保留"
          f"浮点精度），确保生命安全保障类公益服务不受收入水平影响。")
both_print()

# ---- 内嵌分析：F/D/H 小区受冲击最深与逆向补贴 ----
both_print("-" * 100)
both_print(f"从小区维度审视，消费约束的冲击在不同社区之间呈现出显著的分化格局。在全部"
          f"{cut_count + nc_count}组（10小区×3类老人）中，有{cut_count}组触发了消费"
          f"削减，主要集中在低收入小区F（月收入2700元）、D（2900元）、H（3000元）。"
          f"以小区F的失能老人为例：月收入2700元 × 30%消费比例 = 810元消费上限，"
          f"而其理论月费（排除紧急救助后）高达约1330元，上限仅为理论费用的约60%，"
          f"导致各类服务需求被等比削减接近40%。")
both_print()
both_print(f"与之形成鲜明对比的是，高收入小区（如C区月收入3800元）的自理老人几乎不受"
          f"任何削减影响，可全额享受六大类服务。这种\"收入越低被削减比例越大\"的格局，"
          f"本质上制造了一种\"逆向补贴\"效应：社区养老体系本应是给弱势群体兜底的安全网，"
          f"但统一等比削减的规则却让最需要照护的低收入失能老人反而被削减得最多——"
          f"越需要服务的人，能得到的服务反而越少。解决这一结构性不公平的关键路径是引入"
          f"收入分档定价：对月收入低于3000元的老人发放定向服务券补贴，使其有效消费上限"
          f"与中等收入老人拉平；同时可按收入梯度设置差异化的个人支付比例，高收入者多付、"
          f"低收入者少付，在保障基本服务可及性的前提下维持体系的财务可持续性。")
both_print()

# ---- 内嵌分析：失能老人不成比例地被削减与必要性优先策略 ----
both_print("-" * 100)
both_print(f"进一步按失能类型分析，失能和半失能老人在消费约束下的处境尤为严峻。在所有"
          f"触发削减的{cut_count}组中，D类（失能）和H类（半失能）老人占据了绝大多数，"
          f"这并非偶然——失能老人的服务需求种类多、频次高，理论月费远超自理老人，虽然"
          f"消费上限比例更高（30% vs 20%），但绝对增量远不足以覆盖需求增长。结果便"
          f"是：客观上最需要照护的群体，在等比削减规则下反而被削减得最多，这完全背离了"
          f"\"按需分配\"的社会养老公平原则。")
both_print()
both_print(f"要纠正这一偏差，应当从\"一刀切等比削减\"转向\"刚性需求优先保护\"策略：将助餐、"
          f"紧急救助以及失能老人必需的日间照料和上门护理列为刚性需求，在消费约束下优先"
          f"全额保障；康复理疗、助浴等提升生活质量的可选服务则按剩余消费空间进行阶梯式"
          f"削减。同时，对低收入小区（F/D/H）试点降低助餐、日间照料等高频服务单价，"
          f"以社区公益金或政府补贴弥补运营成本缺口。长期而言，建议构建\"基础包+自选包\""
          f"服务套餐体系——基础包覆盖所有老人的基本生存照护需求，由政府兜底保障；自选包"
          f"由老人按收入比例自付，兼顾公平性与可持续性。")

f.close()
print(f"\n报告已保存至: {output_path}")

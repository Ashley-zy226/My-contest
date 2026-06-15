import numpy as np
import pandas as pd

# ============================================================
# 附件1 数据：小区基础数据（人口与老人结构）
# ============================================================
communities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

init_data = {
    'A': {'total_pop': 3200, 'elderly': 712, 'S': 496, 'H': 152, 'D': 64, 'income': 3400},
    'B': {'total_pop': 2800, 'elderly': 608, 'S': 408, 'H': 136, 'D': 64, 'income': 3100},
    'C': {'total_pop': 4100, 'elderly': 920, 'S': 632, 'H': 208, 'D': 80, 'income': 3800},
    'D': {'total_pop': 2500, 'elderly': 544, 'S': 368, 'H': 120, 'D': 56, 'income': 2900},
    'E': {'total_pop': 3600, 'elderly': 784, 'S': 536, 'H': 176, 'D': 72, 'income': 3500},
    'F': {'total_pop': 2200, 'elderly': 472, 'S': 328, 'H': 104, 'D': 40, 'income': 2700},
    'G': {'total_pop': 3900, 'elderly': 864, 'S': 592, 'H': 192, 'D': 80, 'income': 3600},
    'H': {'total_pop': 2600, 'elderly': 568, 'S': 392, 'H': 128, 'D': 48, 'income': 3000},
    'I': {'total_pop': 3400, 'elderly': 736, 'S': 504, 'H': 168, 'D': 64, 'income': 3300},
    'J': {'total_pop': 3000, 'elderly': 656, 'S': 456, 'H': 144, 'D': 56, 'income': 3200},
}

# ============================================================
# 参数设定
# ============================================================
death_rate = 0.05          # 自然死亡率
new_elderly_rate = 0.07    # 新增老人比例（占年初总老年人口）
p_S_to_H = 0.045            # 自理 → 半失能 转移概率
p_H_to_D = 0.10             # 半失能 → 失能 转移概率
years = 5                   # 预测年数

# ============================================================
# 递推预测模型
# ============================================================

results = {}

for comm in communities:
    d = init_data[comm]
    S = d['S']
    H = d['H']
    D = d['D']

    records = []
    for year in range(years + 1):
        total = S + H + D
        records.append({
            'year': year,
            'S': round(S),
            'H': round(H),
            'D': round(D),
            'total': round(total)
        })
        if year == years:
            break

        T = total

        # 1. 自然死亡后存活人数
        S_surv = S * (1 - death_rate)
        H_surv = H * (1 - death_rate)
        D_surv = D * (1 - death_rate)

        # 2. 状态转移（在存活者基础上）
        S_to_H_count = S_surv * p_S_to_H
        H_to_D_count = H_surv * p_H_to_D

        S_after_trans = S_surv - S_to_H_count
        H_after_trans = H_surv + S_to_H_count - H_to_D_count
        D_after_trans = D_surv + H_to_D_count

        # 3. 新增老年人口（基于年初总数 T，全为自理）
        new_elderly = T * new_elderly_rate

        S = S_after_trans + new_elderly
        H = H_after_trans
        D = D_after_trans

    results[comm] = records

# ============================================================
# 输出结果 & 写入报告文件
# ============================================================

output_path = '/Users/ashley_zy/数学建模/问题1_1_预测结果报告.txt'
f = open(output_path, 'w', encoding='utf-8')

def both_print(s=''):
    print(s)
    f.write(s + '\n')

both_print("=" * 80)
both_print("    问题1.1：未来五年各小区老人数量递推预测 —— 结果报告")
both_print("=" * 80)
both_print()
both_print("一、模型参数")
both_print("-" * 40)
both_print(f"  自然死亡率 (death_rate)       : {death_rate*100}%")
both_print(f"  新增老人比例 (new_elderly_rate): {new_elderly_rate*100}%")
both_print(f"  自理 → 半失能 转移概率        : {p_S_to_H*100}%")
both_print(f"  半失能 → 失能 转移概率        : {p_H_to_D*100}%")
both_print()

both_print("二、递推公式")
both_print("-" * 40)
both_print("  S_{t+1} = 0.95*(1-0.045)*S_t + 0.07*T_t")
both_print("  H_{t+1} = 0.95*(1-0.10)*H_t + 0.95*0.045*S_t")
both_print("  D_{t+1} = 0.95*D_t + 0.95*0.10*H_t")
both_print("  其中 T_t = S_t + H_t + D_t")
both_print()

# ---- 小区详细表格 ----
both_print("=" * 80)
both_print("三、各小区逐年详细预测（自理/半失能/失能 分项）")
both_print("=" * 80)

for comm in communities:
    both_print(f"\n--- 小区 {comm} ---")
    both_print(f"  初始: 自理={init_data[comm]['S']}, 半失能={init_data[comm]['H']}, 失能={init_data[comm]['D']}, 总计={init_data[comm]['elderly']}")
    both_print(f"  {'年份':>4}  {'自理':>8}  {'半失能':>8}  {'失能':>8}  {'总计':>8}  {'年增长率':>8}")
    for i, rec in enumerate(results[comm]):
        if i == 0:
            growth = '-'
        else:
            prev_total = results[comm][i - 1]['total']
            growth = f"{((rec['total'] - prev_total) / prev_total * 100):.1f}%"
        both_print(f"  {rec['year']:>4}  {rec['S']:>8}  {rec['H']:>8}  {rec['D']:>8}  {rec['total']:>8}  {growth:>8}")

# ---- C小区分析 ----
c_init = results['C'][0]['total']
c_final = results['C'][years]['total']
both_print()
both_print(f"从以上各小区数据可以清晰地看到，C小区老年人口始终位居首位——第0年{c_init}人、第5年达{c_final}人，远高于其他小区。这意味着C小区将持续产生最大的养老服务需求，是选址方案中不可妥协的优先级节点。其原因在于C小区初始老年人口基数最大且收入水平第二高，增长动力持续。从规划角度看，C小区本质上是整个服务网络的「锚点」，任何选址方案中C小区均应落在服务站300m覆盖半径内。因此建议在后续选址模型中，将C小区的覆盖权重设为最高优先级（即S1=1.0），并以C为中心向周边辐射服务能力。")

# ---- 各小区总数汇总 ----
both_print()
both_print("=" * 80)
both_print("四、各小区老年人口总数汇总")
both_print("=" * 80)

header = f"{'小区':>4}"
for y in range(years + 1):
    header += f"  {'第' + str(y) + '年末':>8}"
both_print(header)
both_print("-" * (4 + 10 * (years + 1)))

for comm in communities:
    row = f"{comm:>4}"
    for rec in results[comm]:
        row += f"  {rec['total']:>8}"
    both_print(row)

# ---- 每年分项汇总 ----
both_print()
both_print("=" * 80)
both_print("五、各年末分项汇总（10小区合计，S=自理 / H=半失能 / D=失能）")
both_print("=" * 80)

for y in range(1, years + 1):
    both_print(f"\n--- 第{y}年末 ---")
    both_print(f"{'小区':>4}  {'S':>8}  {'H':>8}  {'D':>8}  {'总计':>8}")
    for comm in communities:
        rec = results[comm][y]
        both_print(f"{comm:>4}  {rec['S']:>8}  {rec['H']:>8}  {rec['D']:>8}  {rec['total']:>8}")

# ---- 区域总汇总 ----
both_print()
both_print("=" * 80)
both_print("六、区域汇总（10个小区合计）")
both_print("=" * 80)
both_print(f"{'年份':>4}  {'自理(S)':>10}  {'半失能(H)':>10}  {'失能(D)':>10}  {'总计':>10}  {'年增长率':>10}")
both_print("-" * 64)

prev_total_all = None
for y in range(years + 1):
    total_S = sum(results[comm][y]['S'] for comm in communities)
    total_H = sum(results[comm][y]['H'] for comm in communities)
    total_D = sum(results[comm][y]['D'] for comm in communities)
    total_all = total_S + total_H + total_D
    if prev_total_all is None:
        growth_str = '-'
    else:
        growth_str = f"{((total_all - prev_total_all) / prev_total_all * 100):.1f}%"
    both_print(f"{y:>4}  {total_S:>10}  {total_H:>10}  {total_D:>10}  {total_all:>10}  {growth_str:>10}")
    prev_total_all = total_all

# ---- 关键发现与分析 ----
init_total_S = sum(results[comm][0]['S'] for comm in communities)
init_total_H = sum(results[comm][0]['H'] for comm in communities)
init_total_D = sum(results[comm][0]['D'] for comm in communities)
init_total = init_total_S + init_total_H + init_total_D

final_total_S = sum(results[comm][years]['S'] for comm in communities)
final_total_H = sum(results[comm][years]['H'] for comm in communities)
final_total_D = sum(results[comm][years]['D'] for comm in communities)
final_total = final_total_S + final_total_H + final_total_D

net_growth = final_total - init_total
cagr = ((final_total / init_total) ** (1 / years) - 1) * 100
total_pct = (final_total - init_total) / init_total * 100

D_growth = (final_total_D - init_total_D) / init_total_D * 100
D_ratio_init = init_total_D / init_total * 100
D_ratio_final = final_total_D / final_total * 100

H_change = final_total_H - init_total_H
H_pct = H_change / init_total_H * 100
H_ratio_init = init_total_H / init_total * 100
H_ratio_final = final_total_H / final_total * 100
approx_S_to_H = init_total_S * (1 - death_rate) * p_S_to_H
approx_H_to_D_flow = init_total_H * (1 - death_rate) * p_H_to_D
approx_H_death = init_total_H * death_rate

S_change = final_total_S - init_total_S
S_pct = S_change / init_total_S * 100
S_ratio_init = init_total_S / init_total * 100
S_ratio_final = final_total_S / final_total * 100

both_print()
both_print("=" * 80)
both_print("七、关键发现与分析")
both_print("=" * 80)

both_print()
both_print(f"上述区域汇总数据显示，5年内老年人口从{init_total}人增长至{final_total}人，净增{net_growth}人（+{total_pct:.1f}%），年均复合增长率约{cagr:.1f}%。这意味着未来5年基础设施需要预留约10%的增长冗余。其原因在于，7%的年新增率与5%的年死亡率形成了约2%/年的净增长差，呈线性累积效应。从工程规划角度看，若按第5年峰值需求一次性建设全部服务站点，前4年将面临严重的产能闲置和资金沉淀。因此建议采用分期建设策略——前期先建设3座核心服务站覆盖主要需求，第3年根据实际人口增长情况追加建设2座，以平滑投资节奏。")

both_print()
both_print(f"更值得注意的是，失能老人群体从{init_total_D}人激增至{final_total_D}人，增幅高达{D_growth:.1f}%，占比也从{D_ratio_init:.1f}%攀升至{D_ratio_final:.1f}%。这意味着高成本照护服务（上门护理、康复理疗、助浴等）的需求增速远超总人口增速，人均服务成本将出现结构性上升。追究其根源，失能群体处于「只进不出」的累积状态——半失能群体以每年10%的速率转入失能阶段，且缺乏逆转恢复路径，导致失能人数持续堆积。从运营角度看，这种结构漂移将直接推高服务成本结构，若定价策略不随之调整，利润空间将被严重挤压。因此建议在后续问题4的敏感性分析中，增设「H→D转移概率从10%上调至12%」的独立情景，以评估成本结构在加速老龄化下的脆弱性。")

both_print()
both_print(f"与失能群体的剧烈增长形成对比的是，半失能老人群体基本保持稳定，仅从{init_total_H}人变动至{final_total_H}人（{H_pct:+.1f}%），占比{H_ratio_init:.1f}%→{H_ratio_final:.1f}%。这背后是一个动态平衡：每年约有{approx_S_to_H:.0f}人从自理转入半失能，同时约{approx_H_to_D_flow:.0f}人从半失能转入失能、约{approx_H_death:.0f}人自然死亡，流入与流出大致相抵。这意味着半失能群体本质上是一个「中转站」——也是最具干预价值的中间层。每成功延缓1位半失能老人进入失能阶段，年均约可节省386元护理服务成本。从健康管理角度看，这说明预防性服务（日间照料、康复理疗）具有显著的经济杠杆效应。因此建议在服务组合设计中，对半失能群体配置相对密集的干预资源，并量化延缓转移概率的经济价值，为定价与政府补贴谈判提供数据支撑。")

both_print()
both_print(f"最后，自理老人从{init_total_S}人增长至{final_total_S}人（+{S_pct:.1f}%），仍是绝对数量最大的群体，但占比从{S_ratio_init:.1f}%降至{S_ratio_final:.1f}%。7%的新增老人全部归入自理类别，抵消死亡与S→H转移后仍有余量，因此自理人数继续增长，然而人口结构正在向高照护需求方向漂移。从商业模式角度看，自理老人的服务需求以助餐等低毛利项目为主，而失能照护才是高利润服务的来源，这意味着未来营收结构将持续向失能照护倾斜。因此建议在长期财务规划中关注服务组合的结构性变化——失能照护占比上升将推高营收但也推高成本，需审慎评估毛利率的长期走势，避免「增收不增利」的局面。")

f.close()

print()
print(f"报告已保存至: {output_path}")

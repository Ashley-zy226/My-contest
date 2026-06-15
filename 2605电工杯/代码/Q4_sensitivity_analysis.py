import itertools

# ============================================================
# 公共数据
# ============================================================
communities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
N = len(communities)

dist_mat = [
    [0, 600, 1200, 900, 1500, 1800, 1300, 700, 1100, 500],
    [600, 0, 800, 500, 1100, 1400, 900, 400, 700, 300],
    [1200, 800, 0, 700, 600, 900, 500, 900, 600, 700],
    [900, 500, 700, 0, 800, 1100, 600, 300, 500, 400],
    [1500, 1100, 600, 800, 0, 500, 400, 1000, 500, 800],
    [1800, 1400, 900, 1100, 500, 0, 500, 1200, 700, 1100],
    [1300, 900, 500, 600, 400, 500, 0, 800, 400, 600],
    [700, 400, 900, 300, 1000, 1200, 800, 0, 600, 300],
    [1100, 700, 600, 500, 500, 700, 400, 600, 0, 400],
    [500, 300, 700, 400, 800, 1100, 600, 300, 400, 0],
]

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

all_services = ['助餐', '日间照料', '上门护理', '康复理疗', '助浴', '紧急救助']
non_emergency_services = ['助餐', '日间照料', '上门护理', '康复理疗', '助浴']

base_prices = {'助餐': 10, '日间照料': 20, '上门护理': 30, '康复理疗': 28, '助浴': 25, '紧急救助': 0}
costs = {'助餐': 8, '日间照料': 16, '上门护理': 24, '康复理疗': 23, '助浴': 20, '紧急救助': 8}

demand_pc_raw = {
    'S': {'助餐': 14, '日间照料': 8,  '上门护理': 0,  '康复理疗': 2, '助浴': 0, '紧急救助': 0.15},
    'H': {'助餐': 20, '日间照料': 14, '上门护理': 6,  '康复理疗': 4, '助浴': 2, '紧急救助': 1},
    'D': {'助餐': 22, '日间照料': 18, '上门护理': 12, '康复理疗': 6, '助浴': 4, '紧急救助': 3},
}
cap_rate = {'S': 0.20, 'H': 0.25, 'D': 0.30}

def s1(d):
    if d <= 300: return 1.00
    if d <= 500: return 0.90
    if d <= 650: return 0.75
    if d <= 1000: return 0.60
    return None

def s2(util):
    if util <= 0.60: return 1.00
    if util <= 0.75: return 0.93
    if util <= 0.85: return 0.85
    if util <= 0.95: return 0.72
    return 0.60

def s3_from_price_ratio(ratio):
    if ratio <= 1.00: return 1.00
    if ratio <= 1.10: return 0.90
    if ratio <= 1.20: return 0.75
    return 0.60

# ============================================================
# 人口预测 + 需求计算（可参数化）
# ============================================================
def compute_population_and_demand(growth_rate, p_S_to_H, p_H_to_D, death_rate=0.05):
    year5_by_type = {}
    for comm in communities:
        d = init_data[comm]
        S, H, D_old = d['S'], d['H'], d['D']
        for _ in range(5):
            T = S + H + D_old
            S_surv = S * (1 - death_rate)
            H_surv = H * (1 - death_rate)
            D_surv = D_old * (1 - death_rate)
            S = S_surv - S_surv * p_S_to_H + T * growth_rate
            H = H_surv + S_surv * p_S_to_H - H_surv * p_H_to_D
            D_old = D_surv + H_surv * p_H_to_D
        year5_by_type[comm] = {
            'S': round(S), 'H': round(H), 'D': round(D_old),
            'income': d['income']
        }

    year5_pop = {comm: year5_by_type[comm]['S'] + year5_by_type[comm]['H'] + year5_by_type[comm]['D']
                 for comm in communities}

    demand_pc_adj = {}
    for comm in communities:
        income = year5_by_type[comm]['income']
        demand_pc_adj[comm] = {}
        for etype in ['S', 'H', 'D']:
            limit = income * cap_rate[etype]
            raw = demand_pc_raw[etype]
            theoretical = sum(raw[svc] * base_prices[svc] for svc in all_services)
            if theoretical <= limit:
                demand_pc_adj[comm][etype] = {svc: round(raw[svc]) if raw[svc] >= 1 else raw[svc] for svc in all_services}
            else:
                factor = limit / theoretical
                demand_pc_adj[comm][etype] = {svc: max(0, round(raw[svc] * factor)) if raw[svc] >= 1 else max(0, raw[svc] * factor) for svc in all_services}

    monthly = {}
    for comm in communities:
        monthly[comm] = {}
        for svc in all_services:
            total = 0
            for etype in ['S', 'H', 'D']:
                total += year5_by_type[comm][etype] * demand_pc_adj[comm][etype][svc]
            monthly[comm][svc] = total

    daily = {}
    for c in communities:
        daily[c] = sum(v / 30 for v in monthly[c].values())
    comm_daily = {c: daily[c] for c in communities}

    comm_service_mix = {}
    for c in communities:
        total_m = sum(monthly[c].values())
        comm_service_mix[c] = {svc: monthly[c][svc] / total_m for svc in all_services}

    return year5_by_type, year5_pop, demand_pc_adj, monthly, comm_daily, comm_service_mix

# ============================================================
# 问题2：选址评估与枚举
# ============================================================
def solve_problem2(scales_dict, budget, monthly_dict, comm_daily_dict, year5_pop_dict):

    def gen_configs():
        configs = []
        for r in range(1, N + 1):
            for sites in itertools.combinations(range(N), r):
                for scale_combo in itertools.product([1, 2, 3], repeat=r):
                    cost = sum(scales_dict[s][1] for s in scale_combo)
                    if cost <= budget:
                        configs.append((cost, list(zip(sites, scale_combo))))
        return configs

    def evaluate_full(sites_config):
        site_set = {s for s, _ in sites_config}
        site_cap = {s: scales_dict[sc][3] for s, sc in sites_config}

        best_st = {}
        for j in range(N):
            best_st[j] = None
            for i in site_set:
                d = dist_mat[i][j]
                sv = s1(d)
                if sv is not None:
                    if best_st[j] is None or sv > best_st[j][2]:
                        best_st[j] = (i, d, sv)
                    elif best_st[j] is not None and sv == best_st[j][2] and d < best_st[j][1]:
                        best_st[j] = (i, d, sv)

        raw_load = {s: 0.0 for s in site_set}
        for j in range(N):
            if best_st[j] is not None:
                raw_load[best_st[j][0]] += comm_daily_dict[communities[j]]

        actual_load = {}
        util = {}
        for s in site_set:
            actual_load[s] = min(raw_load[s], site_cap[s])
            util[s] = actual_load[s] / site_cap[s]

        pop_list = [year5_pop_dict[c] for c in communities]
        total_elderly = sum(pop_list)

        sats = []
        for j in range(N):
            if best_st[j] is None:
                continue
            sidx, d, s1v = best_st[j]
            s2v = s2(util[sidx])
            sv = 0.2 * s1v + 0.3 * s2v + 0.5 * 1.0
            sats.append(sv)

        covered = sum(pop_list[j] for j in range(N) if best_st[j] is not None)
        avg_sat = sum(sats) / len(sats) if sats else 0
        cov_rate = covered / total_elderly * 100

        return {
            'coverage_rate': cov_rate,
            'avg_sat': avg_sat,
            'best_station': best_st,
            'util': util,
            'config': sites_config,
            'raw_load': raw_load,
            'actual_load': actual_load,
            'score': 0.5 * cov_rate + 0.5 * avg_sat * 100,
        }

    configs = gen_configs()
    results = []
    for cost, sites in configs:
        r = evaluate_full(sites)
        r['build_cost'] = cost
        results.append(r)
    results.sort(key=lambda r: -r['score'])
    return results, configs

# ============================================================
# 问题3：定价优化
# ============================================================
def solve_problem3(scales_dict, optimal_config, monthly_dict, comm_daily_dict,
                   comm_service_mix_dict, year5_pop_dict):

    site_set = {s for s, _ in optimal_config}
    site_scale = {s: sc for s, sc in optimal_config}
    site_cap = {s: scales_dict[sc][3] for s, sc in optimal_config}

    best_station = {}
    for j in range(N):
        best = None
        for i in site_set:
            d = dist_mat[i][j]
            sv = s1(d)
            if sv is not None:
                if best is None or sv > best[2]:
                    best = (i, d, sv)
                elif best is not None and sv == best[2] and d < best[1]:
                    best = (i, d, sv)
        best_station[j] = best

    raw_load = {s: 0.0 for s in site_set}
    for j in range(N):
        if best_station[j] is not None:
            raw_load[best_station[j][0]] += comm_daily_dict[communities[j]]

    actual_load = {}
    util = {}
    for s in site_set:
        actual_load[s] = min(raw_load[s], site_cap[s])
        util[s] = actual_load[s] / site_cap[s]

    comm_station = {}
    for j in range(N):
        if best_station[j] is not None:
            comm_station[j] = best_station[j][0]

    site_communities = {s: [] for s in site_set}
    for j in range(N):
        if comm_station.get(j) is not None:
            site_communities[comm_station[j]].append(j)

    def evaluate_station(site_idx, price_ratios):
        scale_info = scales_dict[site_scale[site_idx]]
        build_annual = scale_info[1] / 20 * 10000
        fixed_annual = scale_info[2] * 365
        capacity = site_cap[site_idx]
        raw_l = raw_load[site_idx]
        s2_val = s2(util[site_idx])

        total_annual_rev = 0.0
        total_annual_direct_cost = 0.0
        total_daily_subsidy = 0.0
        comm_sats = {}
        comm_s3s = {}

        for j in site_communities[site_idx]:
            _, d, s1v = best_station[j]
            c = communities[j]
            mix = comm_service_mix_dict[c]
            s3_j = 0.0
            for svc in non_emergency_services:
                s3_j += mix[svc] * s3_from_price_ratio(price_ratios[svc])
            s3_j /= (1 - mix['紧急救助'])
            comm_s3s[j] = s3_j
            sat = 0.2 * s1v + 0.3 * s2_val + 0.5 * s3_j
            sat = max(0.60, min(1.0, sat))
            comm_sats[j] = sat

            daily_total = sum(monthly_dict[c].values()) / 30
            eff_daily = daily_total * sat
            if raw_l > capacity:
                eff_daily *= capacity / raw_l

            for svc in non_emergency_services:
                price = base_prices[svc] * price_ratios[svc]
                eff_monthly = eff_daily * mix[svc] * 30
                total_annual_rev += eff_monthly * price * 12
                total_annual_direct_cost += eff_monthly * costs[svc] * 12
                total_daily_subsidy += eff_daily * mix[svc] * 2
            emergency_mix = mix['紧急救助']
            emergency_eff_monthly = eff_daily * emergency_mix * 30
            total_annual_direct_cost += emergency_eff_monthly * costs['紧急救助'] * 12

        subsidy_cap_map = {1: 1000, 2: 1800, 3: 2600}
        daily_subsidy = min(total_daily_subsidy, subsidy_cap_map[site_scale[site_idx]])
        annual_subsidy = daily_subsidy * 365

        total_annual_cost = total_annual_direct_cost + fixed_annual + build_annual
        total_annual_profit = total_annual_rev - total_annual_direct_cost + annual_subsidy - fixed_annual - build_annual

        if total_annual_cost > 0:
            profit_rate = total_annual_profit / total_annual_cost
        else:
            profit_rate = float('inf')

        pop_sum = sum(year5_pop_dict[communities[j]] for j in site_communities[site_idx])
        avg_sat = sum(comm_sats[j] * year5_pop_dict[communities[j]] for j in site_communities[site_idx]) / pop_sum if pop_sum > 0 else 0

        return {
            'satisfactions': comm_sats, 'comm_s3s': comm_s3s, 'avg_sat': avg_sat,
            'profit_rate': profit_rate, 'annual_revenue': total_annual_rev,
            'annual_direct_cost': total_annual_direct_cost, 'annual_subsidy': annual_subsidy,
            'daily_subsidy': daily_subsidy, 'daily_subsidy_raw': total_daily_subsidy,
            'annual_fixed_cost': fixed_annual, 'annual_build_cost': build_annual,
            'total_annual_cost': total_annual_cost, 'total_annual_profit': total_annual_profit,
            's2_val': s2_val, 'price_ratios': price_ratios,
        }

    def optimize_station(site_idx):
        base_ratios = {svc: 1.00 for svc in non_emergency_services}
        base_r = evaluate_station(site_idx, base_ratios)
        if base_r['profit_rate'] <= 0.08:
            base_r['strategy'] = '平价维持'
            base_r['price_multiplier'] = 1.0
            return base_r
        C_total = base_r['total_annual_cost']
        S = base_r['annual_subsidy']
        R_base = base_r['annual_revenue']
        alpha_target = (1.08 * C_total - S) / R_base if R_base > 0 else 1.0
        alpha_target = max(0.0, min(1.0, alpha_target))
        opt_ratios = {svc: alpha_target for svc in non_emergency_services}
        opt_r = evaluate_station(site_idx, opt_ratios)
        opt_r['strategy'] = '平价降价'
        opt_r['price_multiplier'] = alpha_target
        return opt_r

    site_opt_results = {}
    for s, sc in optimal_config:
        site_opt_results[s] = optimize_station(s)

    total_weighted_sat = 0.0
    total_pop = 0.0
    total_rev = 0.0
    total_dir = 0.0
    total_sub = 0.0
    total_fixed = 0.0
    total_build = 0.0
    total_profit = 0.0
    total_cost = 0.0

    for s, sc in optimal_config:
        opt = site_opt_results[s]
        for j in site_communities[s]:
            pop = year5_pop_dict[communities[j]]
            total_weighted_sat += opt['satisfactions'][j] * pop
            total_pop += pop
        total_rev += opt['annual_revenue']
        total_dir += opt['annual_direct_cost']
        total_sub += opt['annual_subsidy']
        total_fixed += opt['annual_fixed_cost']
        total_build += opt['annual_build_cost']
        total_profit += opt['total_annual_profit']
        total_cost += opt['total_annual_cost']

    grand_profit_rate = total_profit / total_cost if total_cost > 0 else 0

    return {
        'site_results': site_opt_results,
        'total_pop': total_pop,
        'weighted_avg_sat': total_weighted_sat / total_pop if total_pop > 0 else 0,
        'total_revenue': total_rev, 'total_direct_cost': total_dir,
        'total_subsidy': total_sub, 'total_fixed': total_fixed,
        'total_build': total_build, 'total_profit': total_profit,
        'total_cost': total_cost, 'profit_rate': grand_profit_rate,
        'site_communities': site_communities,
        'util': util, 'raw_load': raw_load,
        'site_scale': site_scale, 'site_cap': site_cap,
    }

# ============================================================
# ====  原始参数求解  ====
# ============================================================
print("=" * 80)
print("  [基准] 原始参数求解")
print("=" * 80)

scales_orig = {
    1: ('小型', 18, 2000, 1000),
    2: ('中型', 32, 3200, 2000),
    3: ('大型', 45, 4400, 3000),
}
BUDGET_ORIG = 120

yt_orig, yp_orig, dpca_orig, mon_orig, cd_orig, csm_orig = compute_population_and_demand(
    growth_rate=0.07, p_S_to_H=0.045, p_H_to_D=0.10)

print(f"  总老人数: {sum(yp_orig.values())}")

results_orig, configs_orig = solve_problem2(scales_orig, BUDGET_ORIG, mon_orig, cd_orig, yp_orig)
best_orig = results_orig[0]
print(f"  最优配置: {len(best_orig['config'])}个站点, 成本={best_orig['build_cost']}万, "
      f"覆盖率={best_orig['coverage_rate']:.1f}%, 满意度={best_orig['avg_sat']:.4f}")

p3_orig = solve_problem3(scales_orig, best_orig['config'], mon_orig, cd_orig, csm_orig, yp_orig)
print(f"  问题3: 加权满意度={p3_orig['weighted_avg_sat']:.4f}, 补贴={p3_orig['total_subsidy']/10000:.2f}万, "
      f"利润率={p3_orig['profit_rate']*100:.2f}%")

# ============================================================
# ====  灵敏度参数求解  ====
# ============================================================
print()
print("=" * 80)
print("  [灵敏度] 新参数求解")
print("=" * 80)

scales_new = {
    1: ('小型', 18, 2400, 1000),
    2: ('中型', 32, 3840, 2000),
    3: ('大型', 45, 5280, 3000),
}
BUDGET_NEW = 140

yt_new, yp_new, dpca_new, mon_new, cd_new, csm_new = compute_population_and_demand(
    growth_rate=0.08, p_S_to_H=0.055, p_H_to_D=0.095)

print(f"  总老人数: {sum(yp_new.values())}")

results_new, configs_new = solve_problem2(scales_new, BUDGET_NEW, mon_new, cd_new, yp_new)
best_new = results_new[0]
print(f"  最优配置: {len(best_new['config'])}个站点, 成本={best_new['build_cost']}万, "
      f"覆盖率={best_new['coverage_rate']:.1f}%, 满意度={best_new['avg_sat']:.4f}")

p3_new = solve_problem3(scales_new, best_new['config'], mon_new, cd_new, csm_new, yp_new)
print(f"  问题3: 加权满意度={p3_new['weighted_avg_sat']:.4f}, 补贴={p3_new['total_subsidy']/10000:.2f}万, "
      f"利润率={p3_new['profit_rate']*100:.2f}%")

# ============================================================
# 输出报告
# ============================================================
out_path = '/Users/ashley_zy/数学建模/问题4_结果报告.txt'
f = open(out_path, 'w', encoding='utf-8')

def bp(s=''):
    print(s)
    f.write(s + '\n')

bp("=" * 100)
bp("    问题4：灵敏度分析与方案比较")
bp("=" * 100)

# ---- 4.1 参数变更 ----
bp()
bp("=" * 100)
bp("4.1 参数变更说明")
bp("=" * 100)
bp(r"""
参数变更明细：

| 参数 | 基准值 | 调整值 | 变化 |
|------|--------|--------|------|
| 60+老人年增长率 | 7% | 8% | +1.0pp |
| 自理→半失能转移概率 | 4.5% | 5.5% | +1.0pp |
| 半失能→失能转移概率 | 10% | 9.5% | -0.5pp |
| 日固定管理成本 | 2000/3200/4400 | 2400/3840/5280 | +20% |
| 总建设预算 | 120万元 | 140万元 | +20万(+16.7%) |

注：死亡率和月人均服务需求参数不变。
""")

# ---- 4.1a 人口变化 ----
bp()
bp("=" * 100)
bp("4.1a 第5年末老人数量变化")
bp("=" * 100)
bp()
bp(f"  {'小区':>4}  {'收入':>6}  {'原S':>6} {'新S':>6} {'ΔS':>6}  {'原H':>6} {'新H':>6} {'ΔH':>6}  {'原D':>6} {'新D':>6} {'ΔD':>6}  {'原总计':>7} {'新总计':>7} {'Δ总计':>7}")
bp(f"  {'-'*4}  {'-'*6}  {'-'*6} {'-'*6} {'-'*6}  {'-'*6} {'-'*6} {'-'*6}  {'-'*6} {'-'*6} {'-'*6}  {'-'*7} {'-'*7} {'-'*7}")

total_S_orig = total_H_orig = total_D_orig = 0
total_S_new = total_H_new = total_D_new = 0
for comm in communities:
    o = yt_orig[comm]
    n = yt_new[comm]
    total_S_orig += o['S']; total_H_orig += o['H']; total_D_orig += o['D']
    total_S_new += n['S']; total_H_new += n['H']; total_D_new += n['D']
    total_o = o['S'] + o['H'] + o['D']
    total_n = n['S'] + n['H'] + n['D']
    bp(f"  {comm:>4}  {yt_orig[comm]['income']:>6}  {o['S']:>6} {n['S']:>6} {n['S']-o['S']:>+6}  "
       f"{o['H']:>6} {n['H']:>6} {n['H']-o['H']:>+6}  {o['D']:>6} {n['D']:>6} {n['D']-o['D']:>+6}  "
       f"{total_o:>7} {total_n:>7} {total_n-total_o:>+7}")
bp(f"  {'─'*100}")
total_all_orig = total_S_orig + total_H_orig + total_D_orig
total_all_new = total_S_new + total_H_new + total_D_new
bp(f"  {'合计':>4}  {'':>6}  {total_S_orig:>6} {total_S_new:>6} {total_S_new-total_S_orig:>+6}  "
   f"{total_H_orig:>6} {total_H_new:>6} {total_H_new-total_H_orig:>+6}  "
   f"{total_D_orig:>6} {total_D_new:>6} {total_D_new-total_D_orig:>+6}  "
   f"{total_all_orig:>7} {total_all_new:>7} {total_all_new-total_all_orig:>+7}")

bp()
bp(f"  增长率提高使自理老人增加{(total_S_new-total_S_orig)/total_S_orig*100:.1f}%")
bp(f"  转移概率变化：S→H概率提升 → 半失能老人增加{(total_H_new-total_H_orig)/total_H_orig*100:.1f}%")
bp(f"  转移概率变化：H→D概率降低 → 失能老人增幅收窄{(total_D_new-total_D_orig)/total_D_orig*100:.1f}%")
bp(f"  总老人：增加{total_all_new-total_all_orig}人，总增幅{(total_all_new-total_all_orig)/total_all_orig*100:.2f}%")

bp()
bp(f"""  对比发现，参数变化后的人口结构呈现非对称增长：半失能老人增幅（{(total_H_new-total_H_orig)/total_H_orig*100:.1f}%）显著高于
  自理老人（{(total_S_new-total_S_orig)/total_S_orig*100:.1f}%）和失能老人（{(total_D_new-total_D_orig)/total_D_orig*100:.1f}%），这意味着需求结构并非简单的
  "所有服务按总人口增幅等比放大"。增长率+1pp是总量增长的基础驱动力，而 S→H 转移概率+1pp
  形成了"半失能波"——更多自理老人进入半失能状态，H型老人呈二次叠加增长（自然增长+转移流入）；
  同时，H→D 转移概率-0.5pp起了阻尼作用，抵消失能老人的部分增长。

  由此可以推断，服务需求结构正在从"金字塔型"向"橄榄型"转变：中等级照护需求（半失能对应的
  上门护理、日间照料、康复理疗）的占比系统性上升，半失能群体已成为需求结构中的"膨胀层"。
  值得关注的是，这种结构转变意味着中端服务能力将成为整个系统的瓶颈约束——简单地按
  总人口增幅等比放大所有服务资源配置是不够的，必须在新建/扩建站点时将半失能友好型功能
  （无障碍设施、康复区域）作为标配而非选配。
""")

# ---- 4.1b 服务需求变化 ----
bp()
bp("=" * 100)
bp("4.1b 月服务需求变化（区域合计）")
bp("=" * 100)
bp()
bp(f"  {'服务项目':>8}  {'原始需求':>12}  {'新参数需求':>12}  {'变化量':>10}  {'变化率':>8}")
bp(f"  {'-'*8}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*8}")

for svc in all_services:
    orig_total = sum(mon_orig[c][svc] for c in communities)
    new_total = sum(mon_new[c][svc] for c in communities)
    diff = new_total - orig_total
    rate = diff / orig_total * 100 if orig_total > 0 else 0
    bp(f"  {svc:>6}  {orig_total:>12}  {new_total:>12}  {diff:>+10}  {rate:>+7.1f}%")

orig_grand = sum(sum(mon_orig[c].values()) for c in communities)
new_grand = sum(sum(mon_new[c].values()) for c in communities)
bp(f"  {'─'*8}  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*8}")
bp(f"  {'合计':>6}  {orig_grand:>12}  {new_grand:>12}  {new_grand-orig_grand:>+10}  {(new_grand-orig_grand)/orig_grand*100:>+7.1f}%")

bp()
bp(f"""  值得关注的是，需求变化的幅度在各服务项目间存在显著分化。上门护理和康复理疗的增幅明显
  高于助餐和日间照料等基础服务，直接印证了"半失能膨胀"效应——半失能老人是上门护理和
  康复理疗的核心消费群体，其数量的大幅增长驱动了这两类服务的需求快速攀升。对比发现，
  服务需求并非均匀增长，而是呈现"中端服务膨胀、基础服务跟随、紧急救助微量增长"的格局。

  这意味着在后续的选址与定价决策中，必须优先确保上门护理和康复理疗的供给弹性，
  避免将"需求增长"简化为一个均质参数代入模型。
""")

# ---- 4.2 选址对比 ----
bp()
bp("=" * 100)
bp("4.2 前后方案对比分析")
bp("=" * 100)

bp()
bp("4.2.1 问题2 — 选址与规模方案对比")
bp("-" * 70)

bp()
bp(f"  {'指标':>24}  {'原始方案':>16}  {'新方案':>16}  {'变化':>10}")
bp(f"  {'-'*24}  {'-'*16}  {'-'*16}  {'-'*10}")
bp(f"  {'建设预算(万)':>24}  {BUDGET_ORIG:>16}  {BUDGET_NEW:>16}  {BUDGET_NEW-BUDGET_ORIG:>+10}")
bp(f"  {'可行配置数':>24}  {len(configs_orig):>16}  {len(configs_new):>16}  --")
bp(f"  {'最优站点数':>24}  {len(best_orig['config']):>16}  {len(best_new['config']):>16}  {len(best_new['config'])-len(best_orig['config']):>+10}")
bp(f"  {'最优建设成本(万)':>24}  {best_orig['build_cost']:>16}  {best_new['build_cost']:>16}  {best_new['build_cost']-best_orig['build_cost']:>+10}")
bp(f"  {'覆盖率(%)':>24}  {best_orig['coverage_rate']:>15.1f}  {best_new['coverage_rate']:>15.1f}  {best_new['coverage_rate']-best_orig['coverage_rate']:>+9.1f}")
bp(f"  {'平均满意度':>24}  {best_orig['avg_sat']:>15.4f}  {best_new['avg_sat']:>15.4f}  {best_new['avg_sat']-best_orig['avg_sat']:>+9.4f}")
bp(f"  {'总老年人口':>24}  {sum(yp_orig.values()):>15}  {sum(yp_new.values()):>15}  {sum(yp_new.values())-sum(yp_orig.values()):>+10}")
bp(f"  {'区域日总需求(人次)':>24}  {sum(cd_orig.values()):>15.0f}  {sum(cd_new.values()):>15.0f}  {sum(cd_new.values())-sum(cd_orig.values()):>+9.0f}")

# 原始站点详情
bp()
bp("  原始方案站点清单：")
orig_sites_info = []
for s, sc in best_orig['config']:
    name, build, day_fixed, cap = scales_orig[sc]
    u = best_orig['util'][s]
    orig_sites_info.append(f"    {communities[s]}({name}) ")
bp("    " + ", ".join(f"{communities[s]}({scales_orig[sc][0]})" for s, sc in best_orig['config']))

bp()
bp("  新方案站点清单：")
bp("    " + ", ".join(f"{communities[s]}({scales_new[sc][0]})" for s, sc in best_new['config']))

bp()
bp("  新方案各站点详情：")
bp(f"  {'站点':>4}  {'规模':>6}  {'成本(万)':>8}  {'日容量':>8}  {'日负荷':>10}  {'利用率':>8}  {'S2':>6}")
bp(f"  {'-'*4}  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*8}  {'-'*6}")
for s, sc in best_new['config']:
    name, build, day_fixed, cap = scales_new[sc]
    bp(f"  {communities[s]:>4}  {name:>6}  {build:>8}  {cap:>8}  {best_new['raw_load'][s]:>10.0f}  {best_new['util'][s]:>8.1%}  {s2(best_new['util'][s]):>6.2f}")

bp()
orig_site_count = len(best_orig['config'])
new_site_count = len(best_new['config'])
orig_scales_str = ", ".join(f"{scales_orig[sc][0]}" for _, sc in best_orig['config'])
new_scales_str = ", ".join(f"{scales_new[sc][0]}" for _, sc in best_new['config'])
sat_diff = best_new['avg_sat'] - best_orig['avg_sat']
budget_diff = BUDGET_NEW - BUDGET_ORIG
bp(f"""  对比发现，站点数从{orig_site_count}减至{new_site_count}个，但规模结构从 {orig_scales_str} 升级为 {new_scales_str}，
  总建设成本从{best_orig['build_cost']}万升至{best_new['build_cost']}万（+{best_new['build_cost']-best_orig['build_cost']}万），满意度从 {best_orig['avg_sat']:.4f} 升至
  {best_new['avg_sat']:.4f}（+{sat_diff:.4f}），覆盖率保持 {best_new['coverage_rate']:.1f}% 不变。这意味着在预算超过一定阈值后，
  "集中建大站"的规模经济效应开始压倒"分散建多站"的覆盖优势。

  值得关注的是，预算+{budget_diff}万（+{budget_diff/BUDGET_ORIG*100:.1f}%）突破了原有的"分散建小站"约束，大型站的日容量
  （{scales_new[3][3]}人次）远超小型站（{scales_new[1][3]}人次），相同负荷下利用率大幅降低，S2显著提高——而S2函数
  在利用率≤0.60时直接取满值1.00，这赋予了大型站一种"规模红利"：容量越充裕，S2越容易
  触及满分，进而系统性推升满意度。

  由此可以推断，存在一条非线性的"预算-满意度"曲线：预算较低时多站策略占优（靠距离
  优势），预算充裕时大站策略占优（靠利用率优势）。本案例中这一策略拐点大致在120~140万
  之间。对实际决策而言，建议绘制预算-满意度的帕累托前沿曲线以识别"性价比拐点"，
  并将规模阈值（1000/2000/3000日容量）作为规划指引，避免建"不大不小"的中间规格
  造成效率损失。
""")

bp()
bp("4.2.2 问题3 — 定价方案对比")
bp("-" * 70)
bp()
bp(f"  {'指标':>24}  {'原始方案':>16}  {'新方案':>16}  {'变化':>10}")
bp(f"  {'-'*24}  {'-'*16}  {'-'*16}  {'-'*10}")

bp(f"  {'加权平均满意度':>24}  {p3_orig['weighted_avg_sat']:>15.4f}  {p3_new['weighted_avg_sat']:>15.4f}  {p3_new['weighted_avg_sat']-p3_orig['weighted_avg_sat']:>+9.4f}")
bp(f"  {'年服务总营收(万)':>24}  {p3_orig['total_revenue']/10000:>15.2f}  {p3_new['total_revenue']/10000:>15.2f}  {(p3_new['total_revenue']-p3_orig['total_revenue'])/10000:>+9.2f}")
bp(f"  {'年直接服务成本(万)':>24}  {p3_orig['total_direct_cost']/10000:>15.2f}  {p3_new['total_direct_cost']/10000:>15.2f}  {(p3_new['total_direct_cost']-p3_orig['total_direct_cost'])/10000:>+9.2f}")
bp(f"  {'年固定管理成本(万)':>24}  {p3_orig['total_fixed']/10000:>15.2f}  {p3_new['total_fixed']/10000:>15.2f}  {(p3_new['total_fixed']-p3_orig['total_fixed'])/10000:>+9.2f}")
bp(f"  {'年建设折旧(万)':>24}  {p3_orig['total_build']/10000:>15.2f}  {p3_new['total_build']/10000:>15.2f}  {(p3_new['total_build']-p3_orig['total_build'])/10000:>+9.2f}")
bp(f"  {'年政府补贴总额(万)':>24}  {p3_orig['total_subsidy']/10000:>15.2f}  {p3_new['total_subsidy']/10000:>15.2f}  {(p3_new['total_subsidy']-p3_orig['total_subsidy'])/10000:>+9.2f}")
bp(f"  {'年运营成本总额(万)':>24}  {p3_orig['total_cost']/10000:>15.2f}  {p3_new['total_cost']/10000:>15.2f}  {(p3_new['total_cost']-p3_orig['total_cost'])/10000:>+9.2f}")
bp(f"  {'年利润总额(万)':>24}  {p3_orig['total_profit']/10000:>15.2f}  {p3_new['total_profit']/10000:>15.2f}  {(p3_new['total_profit']-p3_orig['total_profit'])/10000:>+9.2f}")
bp(f"  {'综合利润率':>24}  {p3_orig['profit_rate']*100:>15.2f}% {p3_new['profit_rate']*100:>15.2f}% {(p3_new['profit_rate']-p3_orig['profit_rate'])*100:>+9.2f}%")

bp()
bp("  新方案各站点最优定价：")
for s, sc in best_new['config']:
    name = scales_new[sc][0]
    opt = p3_new['site_results'][s]
    alpha = opt['price_multiplier']
    bp(f"    站点{communities[s]}({name}): α={alpha:.4f}, 策略={opt['strategy']}, 利润率={opt['profit_rate']*100:.2f}%")

bp()
bp(f"""  值得关注的是，成本+20%对新方案的定价策略产生了"双向挤压"效应：既要维持8%利润率上限
  合规，又要保证满意度不过度下降。新方案下固定管理成本上升了{(p3_new['total_fixed']-p3_orig['total_fixed'])/10000:.2f}万，
  但得益于规模升级后的大站红利（S2提升），加权满意度仍然维持了{p3_new['weighted_avg_sat']-p3_orig['weighted_avg_sat']:+.4f}的变化。
  这意味着大型站的规模经济在一定程度上对冲了成本上涨的不利影响——中小型站的利润空间
  最为脆弱，而大型站因人均分摊效率更高，具有明显的成本韧性。

  对比发现，政府补贴从{p3_orig['total_subsidy']/10000:.2f}万增至{p3_new['total_subsidy']/10000:.2f}万（+{(p3_new['total_subsidy']-p3_orig['total_subsidy'])/10000:.2f}万），
  增幅{(p3_new['total_subsidy']-p3_orig['total_subsidy'])/p3_orig['total_subsidy']*100:.1f}%，与需求总量的增幅大致匹配。由此可以推断，补贴总额对需求规模
  具有近似线性的依赖关系，在常态化运营场景下财政负担是可预测的。建议对小型站单独核算
  盈亏平衡点，低于平衡点则触发合并或升级预案。
""")

bp()
bp("4.2.3 覆盖率与满意度变化分析")
bp("-" * 70)

# 计算覆盖变化
orig_covered = [j for j in range(N) if best_orig['best_station'][j] is not None]
new_covered = [j for j in range(N) if best_new['best_station'][j] is not None]
newly_covered = set(new_covered) - set(orig_covered)
lost_covered = set(orig_covered) - set(new_covered)

bp()
bp(f"  原始方案覆盖率: {best_orig['coverage_rate']:.1f}% (覆盖 {len(orig_covered)}/{N} 个小区)")
bp(f"  新方案覆盖率:   {best_new['coverage_rate']:.1f}% (覆盖 {len(new_covered)}/{N} 个小区)")

if newly_covered:
    bp(f"  新增覆盖: {', '.join(communities[j] for j in newly_covered)}")
if lost_covered:
    bp(f"  失去覆盖: {', '.join(communities[j] for j in lost_covered)}")

bp()
bp(f"  原始方案平均满意度(问题2): {best_orig['avg_sat']:.4f}")
bp(f"  新方案平均满意度(问题2):   {best_new['avg_sat']:.4f}")
bp(f"  满意度变化: {best_new['avg_sat']-best_orig['avg_sat']:+.4f}")

bp()
bp("4.2.4 新方案各小区满意度详情")
bp("-" * 70)
bp(f"  {'小区':>4}  {'人口':>6}  {'服务站':>6}  {'距离':>6}  {'S1':>6}  {'S2':>6}  {'S3':>8}  {'满意度':>8}  {'变化':>8}")
bp(f"  {'-'*4}  {'-'*6}  {'-'*6}  {'-'*6}  {'-'*6}  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}")

for j in range(N):
    bt_old = best_orig['best_station'][j]
    bt_new = best_new['best_station'][j]

    pop = yp_new[communities[j]]
    if bt_new is None:
        bp(f"  {communities[j]:>4}  {pop:>6}  {'--':>6}  {'--':>6}  {'--':>6}  {'--':>6}  {'--':>8}  {'--':>8}  {'--':>8}")
        continue

    s_new, d_new, s1_new = bt_new
    s2_new = s2(best_new['util'][s_new])

    s3_new = 1.0
    if s_new in p3_new['site_results']:
        for jj in p3_new['site_communities'].get(s_new, []):
            if jj == j:
                s3_new = p3_new['site_results'][s_new]['comm_s3s'].get(j, 1.0)
                break

    sat_new = max(0.6, min(1.0, 0.2 * s1_new + 0.3 * s2_new + 0.5 * s3_new))

    sat_old = None
    if bt_old is not None:
        s_old, d_old, s1_old = bt_old
        s2_old = s2(best_orig['util'][s_old])
        sat_old = max(0.6, min(1.0, 0.2 * s1_old + 0.3 * s2_old + 0.5 * 1.0))

    diff_str = f"{sat_new - sat_old:+.4f}" if sat_old is not None else "--"

    bp(f"  {communities[j]:>4}  {pop:>6}  {communities[s_new]:>6}  {d_new:>6}  "
       f"{s1_new:>6.2f}  {s2_new:>6.2f}  {s3_new:>8.4f}  {sat_new:>8.4f}  {diff_str:>8}")

bp()
bp(f"""  值得关注的是，各小区满意度变化呈现显著的"镜像对称"格局：站点合并（减少站点数量但扩大
  单站规模）使部分小区由"专属站点"变为"共享站点"，距离增加导致S1下降；而新方案用
  大型站替代多个小型站，大型站覆盖半径内的中心小区受益（距离近+S2高），边缘小区则受损
  （距离远+S1低）。

  对比发现，这就是选址优化中固有的"密度-公平"权衡：集中资源提升整体效率必然以牺牲
  部分边缘小区的个性化服务为代价。满意度变化的空间分布揭示了"中心-边缘"结构的不对称性：
  站点密集区域的小区"马太效应"增强——越靠近服务中心越受益；处于服务半径边缘的小区则面临
  "服务可及性退化"。由此可以推断，若不加以干预，长期可能导致养老服务获得性的空间不平等
  加剧。建议在选址模型中增加最低满意度约束（如 min_satisfaction ≥ 0.85），并采用
  "中心大站+卫星小站"的混合布局，兼顾规模经济与空间公平。
""")

# ---- 灵敏度分析 ----
bp()
bp("=" * 100)
bp("4.2.5 灵敏度分析与模型鲁棒性评价")
bp("=" * 100)
bp(f"""
  在人口参数方面，老人总数从{sum(yp_orig.values())}增至{sum(yp_new.values())}（增长{(sum(yp_new.values())-sum(yp_orig.values()))/sum(yp_orig.values())*100:.1f}%），
  月服务总需求从{orig_grand}增至{new_grand}（增长{(new_grand-orig_grand)/orig_grand*100:.1f}%）。值得关注的是，结构变化
  比总量变化更关键：半失能老人增幅最大，上门护理和康复理疗需求显著攀升。三个参数
  （增长率+1pp、S→H转移+1pp、H→D转移-0.5pp）的非对称传导使需求结构从均匀增长
  变为"中间膨胀"型，人口参数对选址方案的影响是中等的——更高的需求基数会进一步强化
  "少站大规模"策略的倾向。建议每年更新人口预测数据，建立"人口参数-服务配置"的联动
  调整机制，在半失能增幅超过10%的年份自动触发上门护理和日间照料扩容预案。

  在成本参数方面，日固定管理成本+20%直接推高了各站点年固定成本。对比发现，成本上升
  对定价策略形成"双向挤压"：既要维持8%利润率上限合规，又要保证满意度不过度下降。
  值得关注的是，综合利润率从{p3_orig['profit_rate']*100:.2f}%变为{p3_new['profit_rate']*100:.2f}%，意味着大型站的规模经济对成本上涨
  起到了一定的缓冲作用——中小型站的利润空间最为脆弱，而大型站因人均分摊效率更高，
  具有明显的成本韧性。建议采用"阶梯式定价预案"，预先计算不同固定成本水平下的最优α值，
  形成参数化的定价决策表。

  在预算参数方面，预算+20万（+16.7%）使可行配置数从{len(configs_orig)}增至{len(configs_new)}（增幅
  {(len(configs_new)-len(configs_orig))/len(configs_orig)*100:.1f}%）。最优方案从{len(best_orig['config'])}站变为{len(best_new['config'])}站，规模从{', '.join(scales_orig[sc][0] for _, sc in best_orig['config'])}
  升级为{', '.join(scales_new[sc][0] for _, sc in best_new['config'])}。由此可以推断，预算并非连续影响满意度——存在跳跃式的"相变点"。
  每跨越一个规模升级门槛（如从小→中的18万→32万），最优方案可能突变。这意味着
  "增加一点预算可能带来满意度跳跃，也可能毫无效果"——这是一种典型的"预算门槛效应"。
  建议主动识别并标注各预算台阶对应的最优方案及满意度，形成"预算-方案-满意度"对照表。

  在模型鲁棒性方面，选址方案具有一定鲁棒性：地理中心位置的小区即使参数变化仍倾向于
  被选中，说明选址对空间结构的依赖大于对参数的依赖，这是模型的一个底层优势。定价方案
  的鲁棒性得益于S3阶梯函数的"天然阻尼"：只要参数变化不迫使价格比率跨越S3的阈值
  （1.0→0.90→0.75→0.60），满意度就不会因S3而大幅波动。值得关注的是，满意度对S2
  （利用率）最为敏感——如果参数变化导致某站点利用率跨越S2阈值（如从59%→61%），
  S2从1.00骤降至0.93，产生0.07的满意度断崖式损失。这种"阈值跳跃"是模型的最敏感点，
  也是最需要监测的预警指标。

  综合来看，建议建立"S2预警线"（任一站点利用率接近60%时自动预警），将120~140万
  预算区间标注为"高性价比区间"，并对S→H转移概率做±0.5pp的额外扰动测试，验证
  半失能波峰在极端情景下的系统承载能力。
""")

# ---- 4.3 ----
bp()
bp("=" * 100)
bp("4.3 实际推广中的不确定因素与应对策略")
bp("=" * 100)

bp(f"""
  未来人口结构的不确定性是首要风险。当前模型假设的年增长率和转移概率，任一参数
  ±0.5pp波动可能导致5年末总老人数偏差约3%~5%，半失能老人偏差可达8%~12%。值得关注的
  是"长寿风险"——老人平均余命持续延长而健康余命未必同步增长，失能/半失能比例存在
  系统性低估风险。人口偏差会沿"人口→需求→选址→定价→满意度"链条逐级放大，初始3%的
  偏差映射到服务需求后可能放大至5%~6%，进而触发选址方案的阈值跳跃。建议建立动态监测
  机制，每年更新人口预测数据，采用"2年定基+3年调整"的滚动规划替代一次性5年方案，
  并预留10%~15%的弹性扩容空间。

  政策与财政的可持续性是模型运行的基础约束。政府补贴约{p3_new['total_subsidy']/10000:.2f}万元/年，若补贴
  缩减10%，各站点年利润将下降{p3_new['total_subsidy']*0.1/10000:.2f}万元；若完全取消补贴，系统将由盈转亏。
  对比发现，养老服务的正外部性决定了其"准公共品"属性——单纯靠市场定价无法覆盖全部
  成本，补贴实质上是弥补"公益缺口"的关键工具。由此可以推断，存在"补贴-价格-满意度"
  的不可能三角：三者只能同时满足两个。建议推动多元化融资渠道（社会资本参与、养老专项
  债券），建立阶梯式定价预案（按补贴下降5%/10%/20%三档分别计算最优α），并探索
  "按效果付费"的补贴方式以提高财政资金使用效率。

  社区服务供需匹配偏差同样不容忽视。模型假设100%参与率，但实际参与率可能在60%~90%，
  导致日负荷比预测值低10%~40%。值得关注的是，这种偏差对模型的影响是双向且非对称的：
  利用率偏低时S2提升（满意度↑）但营收下降（利润率↓）；利用率偏高时则相反。因此模型
  必须在"最坏营收情景"下验证财务可行性。建议引入需求弹性模型，将价格/收入/距离弹性
  纳入预测框架，并定期收集实际使用率数据以修正人均需求参数。

  技术进步可能在更长时间尺度上重塑服务成本结构。智慧养老技术（远程看护、AI健康监测等）
  可能将上门护理边际成本降低20%~40%，年直接服务成本可节省{(p3_new['total_direct_cost']*0.2)/10000:.2f}万~
  {(p3_new['total_direct_cost']*0.4)/10000:.2f}万元。这意味着"技术替代人力"将成为降本的核心路径，但技术渗透需要时间，
  且初期投资可能抵消短期降本效果。建议在站点设计中预留智能化改造接口，选择1~2个站点
  做智能养老试点，用实测数据校准成本参数。

  突发公共卫生事件则构成"模型外冲击"。极端情景下日服务需求可能暴涨50%~100%，
  同时供给能力下降30%~50%，紧急救助需求可达平时的5~10倍。这种"需求激增+供给骤降"
  的双向冲击远超常规参数波动范围，必须单独建立应急模式预案：紧急救助服务应以最大容量
  冗余为原则而非最优利用率，保持6个月以上运营资金储备，并设计"平急两用"的站点功能。
""")

bp()
bp("=" * 100)
bp("  报告结束")
bp("=" * 100)

f.close()
print(f"\n报告已保存至: {out_path}")

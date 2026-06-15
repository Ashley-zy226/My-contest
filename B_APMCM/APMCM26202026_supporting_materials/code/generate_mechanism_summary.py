#!/usr/bin/env python3
"""生成问题一用的小型机理影响方向示意图"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

# 中文字体
font_path = None
for f in fm.fontManager.ttflist:
    if f.name in ['Hei', 'STHeiti', 'PingFang HK', 'Lantinghei SC']:
        font_path = f.fname
        break
if not font_path:
    p = '/System/Library/AssetsV2/com_apple_MobileAsset_Font8/5feac9245cca79adaf638ded7a4994b1ddb33ca0.asset/AssetData/Hei.ttf'
    if Path(p).exists():
        font_path = p
if font_path:
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
else:
    prop = None
plt.rcParams['axes.unicode_minus'] = False

Path('figures').mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(11.5, 4.0))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# 标题
ax.text(0.5, 0.94, '结构参数对热管理性能的机理影响方向', ha='center', va='center',
        fontsize=16, fontweight='bold', fontproperties=prop)

# 左侧参数框
params = [
    ('针肋宽度比 $x_1$', '换热面积↑\n扰流增强\n流通截面↓'),
    ('歧管深高比 $x_2$', '歧管空间↑\n配流阻力↓\n局部流速↓'),
    ('针肋排数 $x_3$', '换热面积↑\n扰动次数↑\n流动路径↑'),
]
# 右侧指标框
metrics = [
    ('热阻 $R$', '越小越好', '#1565C0'),
    ('压降 $P$', '越小越好', '#E65100'),
    ('温度非均匀性 $U$', '越小越好', '#2E7D32'),
]

left_x = 0.08
right_x = 0.74
ys = [0.72, 0.50, 0.28]

for (title, desc), y in zip(params, ys):
    box = FancyBboxPatch((left_x, y-0.08), 0.22, 0.15, boxstyle='round,pad=0.018',
                         facecolor='#F5F7FA', edgecolor='#607D8B', linewidth=1.2)
    ax.add_patch(box)
    ax.text(left_x+0.11, y+0.035, title, ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(left_x+0.11, y-0.035, desc, ha='center', va='center', fontsize=9.5, linespacing=1.25)

for (title, desc, color), y in zip(metrics, ys):
    box = FancyBboxPatch((right_x, y-0.07), 0.18, 0.13, boxstyle='round,pad=0.018',
                         facecolor=color+'20', edgecolor=color, linewidth=1.4)
    ax.add_patch(box)
    ax.text(right_x+0.09, y+0.02, title, ha='center', va='center', fontsize=12, fontweight='bold', color=color)
    ax.text(right_x+0.09, y-0.035, desc, ha='center', va='center', fontsize=9.5, color=color)

# 中间机制说明
ax.text(0.50, 0.78, '传热强化', ha='center', fontsize=11, fontweight='bold', color='#1565C0')
ax.text(0.50, 0.56, '流动损失', ha='center', fontsize=11, fontweight='bold', color='#E65100')
ax.text(0.50, 0.34, '温度分布', ha='center', fontsize=11, fontweight='bold', color='#2E7D32')

# 箭头与影响文字
arrows = [
    (0.30,0.72,0.73,0.72,'$R$ 先降后升', '#1565C0'),
    (0.30,0.72,0.73,0.50,'$P$ 增大', '#E65100'),
    (0.30,0.72,0.73,0.28,'$U$ 先降后升', '#2E7D32'),
    (0.30,0.50,0.73,0.72,'$R$ 略升', '#1565C0'),
    (0.30,0.50,0.73,0.50,'$P$ 降低', '#E65100'),
    (0.30,0.50,0.73,0.28,'$U$ 先降后稳', '#2E7D32'),
    (0.30,0.28,0.73,0.72,'$R$ 降低', '#1565C0'),
    (0.30,0.28,0.73,0.50,'$P$ 增大', '#E65100'),
    (0.30,0.28,0.73,0.28,'$U$ 先降后升', '#2E7D32'),
]
for x1,y1,x2,y2,label,color in arrows:
    con = 'arc3,rad=0' if abs(y1-y2)<0.01 else ('arc3,rad=0.10' if y1>y2 else 'arc3,rad=-0.10')
    arr = FancyArrowPatch((x1,y1), (x2,y2), arrowstyle='->', mutation_scale=10,
                          linewidth=1.0, color=color, alpha=0.65, connectionstyle=con)
    ax.add_patch(arr)
    mx, my = (x1+x2)/2, (y1+y2)/2
    if abs(y1-y2)<0.01:
        my += 0.025
    ax.text(mx, my, label, fontsize=8.5, color=color, ha='center', va='center',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.72, pad=0.6))

# 注释
ax.text(0.5, 0.06, '注：箭头表示参数增大时的主要影响方向；非单调关系源于换热强化与流动阻塞之间的竞争。',
        ha='center', va='center', fontsize=9.5, color='#555555', fontproperties=prop)

plt.tight_layout(pad=0.3)
plt.savefig('figures/mechanism_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
print('✓ figures/mechanism_summary.png')

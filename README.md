# 🐱 猫咪家庭满意度指数分析器

全方位量化分析猫咪居家幸福感的 Python 工具。通过 **6 大一级维度、22 个二级量化指标** 打分，
加权计算综合满意度指数（0-100 分），自动生成专业 TXT 分析报告与 PNG 可视化图表，
精准定位短板并输出一对一落地改进方案。

## 功能亮点

- **网页版交互体验**：滑杆打分、实时计算、动态雷达图，像 App 一样使用（推荐）
- **维度极致全面**：22 个细分指标覆盖饮食、环境、安全、情感互动、丰容娱乐、健康护理六大需求
- **数据绝对量化**：全部采用 0-10 分统一标准，算法计算，杜绝主观偏差
- **报告专业化**：宠物行为学 / 饲养学标准话术，含 5 大核心板块
- **方案落地化**：每个短板对应「操作频次 / 操作方法 / 优化周期 / 预期效果」四要素
- **可迭代拓展**：四层解耦架构，可自由新增维度、调整权重、修改评分标准

## 目录结构

```
cat_satisfaction_analyzer/
├── webapp.py        # 网页版后端（Flask，推荐入口）
├── templates/
│   └── index.html   # 网页版交互前端（滑杆+实时图表）
├── main.py          # 终端版主入口（交互、调度全流程）
├── score_rule.py    # 打分规则、权重配置、评级规则
├── data_model.py    # 数据结构、维度定义、计算算法
├── report_gen.py    # 报告生成、文本排版、数据分析
├── visual_plot.py   # 可视化雷达图、柱状图生成（终端版）
├── user_data.json   # 用户猫咪数据缓存（可手动修改）
├── start_web.command # 网页版双击启动入口（macOS）
├── run_web.sh       # 网页版终端启动脚本
├── start.command    # 终端版双击启动入口（macOS）
├── run.sh           # 终端版启动脚本
├── requirements.txt # 依赖清单
└── output/          # 自动生成的报告+图表输出文件夹
    ├── report.txt
    ├── radar_chart.png
    ├── score_chart.png
    └── indicator_chart.png
```

## 快速开始

### 1. 安装依赖

```bash
cd cat_satisfaction_analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行（网页版，推荐）

```bash
# 终端启动，自动在浏览器打开交互界面
./run_web.sh

# 或直接运行
.venv/bin/python webapp.py
```

**macOS 双击启动**：直接双击 `start_web.command`，自动打开浏览器。

网页版提供：22 个滑杆实时打分、综合指数环形进度条、实时雷达图/柱状图、
短板诊断卡片（含改进频次/方法/周期/预期）、一键下载 TXT 报告。

### 3. 运行（终端版）

```bash
# 交互式逐项录入（默认）
python main.py

# 直接读取 user_data.json
python main.py --json

# 使用内置演示数据
python main.py --demo
```

运行后自动在 `output/` 生成 `report.txt` 及三张可视化图表。

## 四大运行模式

| 命令 | 说明 |
|------|------|
| `python main.py` | 终端交互式录入 22 项指标（回车用默认值 7，输入 q 退出） |
| `python main.py --json` | 读取 `user_data.json` 批量分析 |
| `python main.py --demo` | 使用内置演示数据快速体验完整报告 |
| `python main.py -o 自定义目录` | 指定输出目录 |

## 评分体系

### 六大维度权重

| 维度 | 权重 |
|------|------|
| 主人互动情感满意度 | 20% |
| 饮食满意度 | 18% |
| 居住环境满意度 | 18% |
| 安全保障满意度 | 15% |
| 健康护理满意度 | 15% |
| 娱乐与丰容满意度 | 14% |

### 打分标准（0-10 分）

| 分数 | 等级 | 含义 |
|------|------|------|
| 9-10 | 极致满意 | 状态优秀，无任何短板 |
| 7-8 | 良好满意 | 状态正常，轻微可优化 |
| 5-6 | 基本达标 | 勉强适应，存在明显不足 |
| 3-4 | 不满意 | 体验较差，猫咪出现负面行为 |
| 0-2 | 极度不满 | 猫咪应激、抵触、抗拒家庭/主人 |

### 满意度评级（0-100 分）

| 区间 | 评级 |
|------|------|
| 90-100 | S级 极致幸福家庭 |
| 80-89 | A级 优质幸福家庭 |
| 70-79 | B级 合格舒适家庭 |
| 60-69 | C级 临界达标家庭 |
| 40-59 | D级 不满意家庭 |
| 0-39 | E级 极差体验家庭 |

## 核心算法

- **维度得分** = 该维度下所有二级指标平均分（0-10）
- **综合满意度指数** = Σ(维度平均分 × 维度权重) / 10，区间 0-100

## 打包为可执行文件（可选）

```bash
pip install pyinstaller
pyinstaller -F main.py --name cat_satisfaction_analyzer
```

## 二次开发

- 修改网页前端 → 编辑 `templates/index.html` 与 `webapp.py`
- 新增/修改维度、指标、权重 → 编辑 `score_rule.py`
- 修改计算逻辑 → 编辑 `data_model.py`
- 修改报告话术与排版 → 编辑 `report_gen.py`
- 修改图表样式 → 编辑 `visual_plot.py`

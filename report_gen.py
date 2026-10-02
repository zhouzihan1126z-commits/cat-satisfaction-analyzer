# -*- coding: utf-8 -*-
"""
report_gen.py —— 报告生成层
负责：文本排版、维度深度分析、短板诊断、落地改进方案、优化预期预测，
并输出专业 TXT 报告。
"""
import os
from datetime import datetime

import score_rule as rules
from data_model import AnalysisResult

# 短板分类 -> 问题类型标签
DIMENSION_CATEGORY = {
    "diet": "饮食问题",
    "env": "环境问题",
    "safe": "安全问题",
    "inter": "主人互动问题",
    "play": "丰容娱乐问题",
    "health": "护理健康问题",
}


def _bar(value: float, width: int = 20) -> str:
    """将 0-10 分渲染为文本进度条。"""
    filled = int(round(value / 10 * width))
    return "█" * filled + "░" * (width - filled)


def _section(title: str) -> str:
    line = "=" * 66
    return f"\n{line}\n{title}\n{line}\n"


def build_report(result: AnalysisResult) -> str:
    """生成完整专业分析报告文本。"""
    parts: list = []
    parts.append(_header(result))
    parts.append(_basic_summary(result))
    parts.append(_dimension_analysis(result))
    parts.append(_problem_diagnosis(result))
    parts.append(_improvement_plan(result))
    parts.append(_prediction(result))
    parts.append(_footer())
    return "\n".join(parts)


# ------------------------------------------------------------
def _header(result: AnalysisResult) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return "\n".join([
        "╔══════════════════════════════════════════════════════════════╗",
        "║         🐱 猫咪家庭满意度指数分析报告 🐱                    ║",
        "║              全方位量化 · 专业化评估 · 落地化方案           ║",
        "╚══════════════════════════════════════════════════════════════╝",
        f"报告生成时间：{now}",
        f"综合满意度指数：{result.total} 分",
        f"满意度评级：{result.grade_level}",
    ])


# ------------------------------------------------------------
def _basic_summary(result: AnalysisResult) -> str:
    lines = [_section("一、基础数据汇总")]

    lines.append(f"综合满意度指数：{result.total} / 100")
    lines.append(f"满意度评级：{result.grade_level}")
    lines.append(f"评级解读：{result.grade_desc}")
    lines.append("")

    lines.append("【六大维度得分】")
    lines.append(f"{'维度':<10}{'权重':<8}{'平均分':<8}{'贡献':<8}评分")
    for d in result.dimensions:
        lines.append(
            f"{d.name:<10}{str(d.weight) + '%':<8}{d.average:<8.2f}"
            f"{d.weighted:<8.2f}{_bar(d.average)}"
        )
    lines.append("")

    lines.append("【22 项二级指标原始得分】")
    for d in result.dimensions:
        lines.append(f"\n· {d.name}（权重 {d.weight}%）")
        for ind in d.indicators:
            lines.append(
                f"    {ind.name:<12}{ind.score:<6.2f}{_bar(ind.score, 16)}  [{ind.band}]"
            )
    return "\n".join(lines)


# ------------------------------------------------------------
def _dimension_analysis(result: AnalysisResult) -> str:
    lines = [_section("二、维度深度分析")]

    # 优势维度与短板维度
    dims_sorted = sorted(result.dimensions, key=lambda d: d.average, reverse=True)
    best = dims_sorted[0]
    worst = dims_sorted[-1]

    for d in result.dimensions:
        dim = rules.dimension_map()[d.key]
        band, band_desc = rules.score_band(d.average)
        lines.append(f"▶ {d.name}（平均 {d.average:.2f} 分 / {band}）")
        lines.append(f"  {dim['summary']}")
        lines.append(f"  当前解读：{band_desc}。")

        # 针对低分维度的行为学解读
        if d.average < 6.0:
            lines.append(f"  专业视角：该维度得分偏低，{_low_dimension_read(d.key)}")
        elif d.average >= 8.0:
            lines.append(f"  专业视角：该维度表现优秀，已成为猫咪满意度的有力支撑。")
        lines.append("")

    lines.append(f"■ 优势维度：{best.name}（{best.average:.2f} 分），继续保持。")
    lines.append(f"■ 短板维度：{worst.name}（{worst.average:.2f} 分），需重点优化。")
    return "\n".join(lines)


def _low_dimension_read(key: str) -> str:
    reads = {
        "diet": "基础生存需求未充分满足，可能影响猫咪对家庭的基础认可度。",
        "env": "居家舒适感与安全感不足，归属感建立受阻。",
        "safe": "安全感缺失，猫咪难以真正信任家庭与主人。",
        "inter": "情感归属感不足，猫咪主动黏人意愿弱、依赖感低。",
        "play": "精神需求未被满足，易出现无聊、抑郁、拆家等行为问题。",
        "health": "身体状态欠佳，长期影响情绪稳定与幸福感。",
    }
    return reads.get(key, "存在明显可优化空间。")


# ------------------------------------------------------------
def _problem_diagnosis(result: AnalysisResult) -> str:
    lines = [_section("三、核心问题诊断")]

    weak = result.weak_indicators
    if not weak:
        lines.append("🎉 未发现低于 7 分的短板指标，猫咪满意度表现全面良好！")
        return "\n".join(lines)

    lines.append(f"共筛查出 {len(weak)} 项核心短板指标（按严重程度排序）：")
    lines.append("")
    for i, ind in enumerate(weak, 1):
        cat = DIMENSION_CATEGORY.get(ind.dimension_key, "其他问题")
        lines.append(f"{i}. [{cat}] {ind.dimension_name} → {ind.name}")
        lines.append(f"   当前得分：{ind.score:.2f} 分（{ind.band}）")
        lines.append(f"   问题解读：{ind.band_desc}")
        lines.append("")

    # 分类汇总
    by_cat: dict = {}
    for ind in weak:
        cat = DIMENSION_CATEGORY.get(ind.dimension_key, "其他问题")
        by_cat.setdefault(cat, []).append(ind.name)
    lines.append("【问题分类汇总】")
    for cat, names in by_cat.items():
        lines.append(f"· {cat}：{'、'.join(names)}")
    return "\n".join(lines)


# ------------------------------------------------------------
def _improvement_plan(result: AnalysisResult) -> str:
    lines = [_section("四、个性化落地改进方案")]

    weak = result.weak_indicators
    if not weak:
        lines.append("当前无需专项改进，保持现状即可，建议定期复评。")
        return "\n".join(lines)

    imap = rules.indicator_map()
    for i, ind in enumerate(weak, 1):
        dim, ind_cfg = imap[ind.key]
        tips = ind_cfg["tips"]
        lines.append(f"◆ 方案 {i}：改善「{ind.name}」（当前 {ind.score:.2f} 分）")
        lines.append(f"   【操作频次】{tips['freq']}")
        lines.append(f"   【操作方法】{tips['method']}")
        lines.append(f"   【优化周期】{tips['period']}")
        lines.append(f"   【预期改善】{tips['effect']}")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------
def _prediction(result: AnalysisResult) -> str:
    lines = [_section("五、优化预期预测")]

    if not result.weak_indicators:
        lines.append("当前已处于满意状态，综合指数预计保持稳定。")
        return "\n".join(lines)

    lines.append(f"当前综合满意度指数：{result.total} 分")
    lines.append(f"优化后预计综合指数：{result.projected_total} 分")
    lines.append(f"预计提升空间：+{result.projected_delta} 分")
    lines.append("")

    lines.append("【各维度提升空间预测】")
    for d in result.dimensions:
        projected = result.projected_dimensions.get(d.key, d.average)
        delta = projected - d.average
        arrow = "↑" if delta > 0.05 else "→"
        lines.append(
            f"· {d.name}：{d.average:.2f} {arrow} {projected:.2f}（{'+' if delta >= 0 else ''}{delta:.2f}）"
        )
    lines.append("")

    lines.append("【预期行为改善】")
    for d in result.dimensions:
        if d.key in result.projected_dimensions and result.projected_dimensions[d.key] - d.average > 0.05:
            lines.append(f"· {rules.BEHAVIOR_EFFECTS.get(d.key, '综合表现提升')}")
    lines.append("")
    lines.append("提示：以上预测基于「落实全部改进方案」的前提，实际效果因猫咪个体差异而异。")
    return "\n".join(lines)


# ------------------------------------------------------------
def _footer() -> str:
    return "\n".join([
        "",
        "=" * 66,
        "报告结束 · 用数据定义猫咪对家庭的满意程度 🐾",
        "=" * 66,
    ])


# ============================================================
# 输出报告
# ============================================================
def write_report(result: AnalysisResult, output_dir: str) -> str:
    """将报告写入 output_dir/report.txt，返回文件路径。"""
    os.makedirs(output_dir, exist_ok=True)
    report_text = build_report(result)
    path = os.path.join(output_dir, "report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return path

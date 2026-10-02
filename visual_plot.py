# -*- coding: utf-8 -*-
"""
visual_plot.py —— 可视化图表生成层
负责：生成维度雷达图、维度评分柱状图、二级指标横向柱状图。
输出 PNG 文件到 output 目录，自动适配中文字体。
"""
import logging
import os

import matplotlib
matplotlib.use("Agg")  # 非交互式后端，支持无界面运行/打包

import matplotlib.pyplot as plt
import numpy as np

# 中文字体在部分平台会触发字重回退告警（无害），此处静默化避免干扰输出
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

from data_model import AnalysisResult

# ============================================================
# 中文字体适配（跨平台）
# ============================================================
_FONT_CANDIDATES = [
    "PingFang SC", "Hiragino Sans GB", "Heiti SC", "STHeiti",
    "Arial Unicode MS", "Noto Sans CJK SC", "Source Han Sans SC",
    "Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei",
]


def _setup_font():
    from matplotlib import font_manager
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in _FONT_CANDIDATES:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            break
    plt.rcParams["axes.unicode_minus"] = False


def _score_color(score: float):
    """根据 0-10 分返回颜色：>=8 绿、>=6 黄、<6 红。"""
    if score >= 8.0:
        return "#2e9e5b"
    if score >= 6.0:
        return "#e0a800"
    return "#d64541"


# ============================================================
# 雷达图：六大维度
# ============================================================
def plot_radar(result: AnalysisResult, output_dir: str) -> str:
    _setup_font()
    names = [d.name for d in result.dimensions]
    values = [d.average for d in result.dimensions]

    N = len(names)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_closed = values + values[:1]
    angles_closed = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(7.2, 7.2), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#ffffff")

    # 绘制网格
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color="#888888")
    ax.set_xticks(angles)
    ax.set_xticklabels(names, fontsize=12, fontweight="bold")
    ax.spines["polar"].set_color("#cccccc")

    # 主数据
    ax.plot(angles_closed, values_closed, color="#3b7dd8", linewidth=2.5)
    ax.fill(angles_closed, values_closed, color="#3b7dd8", alpha=0.25)

    # 标注数值
    for angle, val in zip(angles, values):
        ax.text(angle, val + 0.6, f"{val:.1f}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="#1f4e8c")

    ax.set_title(f"猫咪家庭满意度六维雷达图\n综合指数 {result.total} 分 · {result.grade_level}",
                 fontsize=14, fontweight="bold", pad=28)
    fig.tight_layout()

    path = os.path.join(output_dir, "radar_chart.png")
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ============================================================
# 柱状图：六大维度平均分
# ============================================================
def plot_dimension_bar(result: AnalysisResult, output_dir: str) -> str:
    _setup_font()
    names = [d.name for d in result.dimensions]
    values = [d.average for d in result.dimensions]
    colors = [_score_color(v) for v in values]

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    fig.patch.set_facecolor("#ffffff")
    bars = ax.bar(names, values, color=colors, width=0.55, edgecolor="#ffffff", linewidth=1.2)

    ax.axhline(7.0, color="#2e9e5b", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(len(names) - 0.45, 7.15, "良好线 7.0", fontsize=9, color="#2e9e5b")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.15, f"{val:.1f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylim(0, 10.5)
    ax.set_ylabel("维度平均分（0-10）", fontsize=10)
    ax.set_title(f"六大维度评分柱状图 · 综合指数 {result.total} 分（{result.grade_level}）",
                 fontsize=13, fontweight="bold", pad=16)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=10)
    fig.tight_layout()

    path = os.path.join(output_dir, "score_chart.png")
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ============================================================
# 横向柱状图：22 项二级指标（按得分排序，短板置顶）
# ============================================================
def plot_indicator_bar(result: AnalysisResult, output_dir: str) -> str:
    _setup_font()
    inds = sorted(result.indicators, key=lambda r: r.score)
    labels = [f"{i.dimension_name}·{i.name}" for i in inds]
    values = [i.score for i in inds]
    colors = [_score_color(v) for v in values]

    fig, ax = plt.subplots(figsize=(10, 9.5))
    fig.patch.set_facecolor("#ffffff")
    y = np.arange(len(inds))
    ax.barh(y, values, color=colors, height=0.62, edgecolor="#ffffff")

    for yi, val in zip(y, values):
        ax.text(val + 0.1, yi, f"{val:.1f}", va="center", fontsize=9, fontweight="bold")

    ax.axvline(7.0, color="#2e9e5b", linestyle="--", linewidth=1.1, alpha=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0, 10.5)
    ax.set_xlabel("得分（0-10）", fontsize=10)
    ax.set_title("22 项二级指标得分一览（短板置顶）", fontsize=13, fontweight="bold", pad=16)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    path = os.path.join(output_dir, "indicator_chart.png")
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ============================================================
# 一键生成全部图表
# ============================================================
def generate_all_charts(result: AnalysisResult, output_dir: str) -> list:
    os.makedirs(output_dir, exist_ok=True)
    paths = [
        plot_radar(result, output_dir),
        plot_dimension_bar(result, output_dir),
        plot_indicator_bar(result, output_dir),
    ]
    return paths

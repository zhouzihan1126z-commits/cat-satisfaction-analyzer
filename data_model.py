# -*- coding: utf-8 -*-
"""
data_model.py —— 数据模型与算法计算层
负责：数据结构定义、维度得分计算、综合满意度指数、评级、短板诊断、优化预期预测。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import score_rule as rules


# ============================================================
# 一、数据结构
# ============================================================
@dataclass
class IndicatorResult:
    """单个二级指标的评分结果。"""
    key: str
    name: str
    dimension_key: str
    dimension_name: str
    score: float

    @property
    def band(self) -> str:
        return rules.score_band(self.score)[0]

    @property
    def band_desc(self) -> str:
        return rules.score_band(self.score)[1]


@dataclass
class DimensionResult:
    """单个一级维度的计算结果。"""
    key: str
    name: str
    weight: float              # 权重（百分比，如 18）
    indicators: List[IndicatorResult]
    average: float             # 该维度指标平均分（0-10）
    weighted: float            # 该维度对综合指数的贡献（0-100 区间内）

    @property
    def band(self) -> str:
        return rules.score_band(self.average)[0]


@dataclass
class AnalysisResult:
    """完整分析结果。"""
    scores: Dict[str, float]               # {指标key: 得分}
    indicators: List[IndicatorResult]
    dimensions: List[DimensionResult]
    total: float                           # 综合满意度指数（0-100）
    grade_level: str                       # 评级（如 "B级 合格舒适家庭"）
    grade_desc: str                        # 评级解读

    # 短板与优化预测（延迟计算）
    weak_indicators: List[IndicatorResult] = field(default_factory=list)
    projected_total: float = 0.0
    projected_delta: float = 0.0
    projected_dimensions: Dict[str, float] = field(default_factory=dict)


# ============================================================
# 二、核心计算
# ============================================================
def analyze(scores: Dict[str, float]) -> AnalysisResult:
    """
    输入 {指标key: 0-10 得分}，输出完整分析结果。
    综合满意度指数 = Σ(维度平均分 × 维度权重) / 10，区间 0-100。
    """
    indicator_map = rules.indicator_map()

    # 1) 构建指标结果
    indicator_results: List[IndicatorResult] = []
    for dim, ind in rules.all_indicators():
        key = ind["key"]
        score = float(scores.get(key, 0.0))
        score = max(0.0, min(10.0, score))
        indicator_results.append(
            IndicatorResult(
                key=key,
                name=ind["name"],
                dimension_key=dim["key"],
                dimension_name=dim["name"],
                score=score,
            )
        )

    # 2) 计算维度得分与综合指数
    dimension_results: List[DimensionResult] = []
    total = 0.0
    for dim in rules.DIMENSIONS:
        dim_inds = [r for r in indicator_results if r.dimension_key == dim["key"]]
        avg = sum(r.score for r in dim_inds) / len(dim_inds)
        weighted = avg * dim["weight"] / 10.0  # 0-10 平均分 × 权重 → 归一化到 0-100 区间
        total += weighted
        dimension_results.append(
            DimensionResult(
                key=dim["key"],
                name=dim["name"],
                weight=dim["weight"],
                indicators=dim_inds,
                average=avg,
                weighted=weighted,
            )
        )

    total = round(total, 2)
    grade_level, grade_desc = rules.grade_level(total)

    result = AnalysisResult(
        scores=dict(scores),
        indicators=indicator_results,
        dimensions=dimension_results,
        total=total,
        grade_level=grade_level,
        grade_desc=grade_desc,
    )

    # 3) 短板诊断 + 优化预期预测
    result.weak_indicators = find_weak_indicators(result)
    _predict_improvement(result)
    return result


# ============================================================
# 三、短板诊断
# ============================================================
WEAK_THRESHOLD = 7.0  # 低于此分视为短板


def find_weak_indicators(result: AnalysisResult, limit: int = 5) -> List[IndicatorResult]:
    """按得分从低到高返回得分最低的短板指标（最多 limit 个，且低于阈值）。"""
    weak = [r for r in result.indicators if r.score < WEAK_THRESHOLD]
    weak.sort(key=lambda r: r.score)
    return weak[:limit]


# ============================================================
# 四、优化预期预测
# ============================================================
def _predict_improvement(result: AnalysisResult) -> None:
    """
    假设所有短板指标按落地计划改善（最多提升 IMPROVE_STEP、上限 IMPROVE_CAP），
    重新计算综合满意度指数，得出提升空间。
    """
    projected_scores = dict(result.scores)
    changed_keys = set()
    for r in result.weak_indicators:
        if r.score < rules.IMPROVE_TARGET:
            new_score = min(r.score + rules.IMPROVE_STEP, rules.IMPROVE_CAP)
            projected_scores[r.key] = new_score
            changed_keys.add(r.key)

    # 计算优化后的维度平均分与综合指数
    dim_avg = {d.key: d.average for d in result.dimensions}
    ind_by_key = {r.key: r for r in result.indicators}
    projected_dims: Dict[str, float] = {}
    projected_total = 0.0
    for dim in rules.DIMENSIONS:
        dim_inds = dim["indicators"]
        new_avg = sum(projected_scores.get(i["key"], 0.0) for i in dim_inds) / len(dim_inds)
        projected_dims[dim["key"]] = round(new_avg, 2)
        projected_total += new_avg * dim["weight"] / 10.0

    result.projected_total = round(projected_total, 2)
    result.projected_delta = round(result.projected_total - result.total, 2)
    result.projected_dimensions = projected_dims


# ============================================================
# 五、实用工具函数
# ============================================================
def validate_scores(scores: Dict[str, float]):
    """校验得分：key 必须合法、分值必须在 0-10 之间。返回错误列表。"""
    errors = []
    imap = rules.indicator_map()
    for key, val in scores.items():
        if key not in imap:
            errors.append(f"未知指标 key: {key}")
            continue
        try:
            v = float(val)
        except (TypeError, ValueError):
            errors.append(f"指标 {key} 的分值无法解析为数字: {val!r}")
            continue
        if not (0.0 <= v <= 10.0):
            errors.append(f"指标 {key} 的分值超出 0-10 范围: {v}")
    return errors


def empty_scores() -> Dict[str, float]:
    """返回全 0 的得分字典（用于初始化）。"""
    return {ind["key"]: 0.0 for _, ind in rules.all_indicators()}

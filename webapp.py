# -*- coding: utf-8 -*-
"""
webapp.py —— Web 版猫咪家庭满意度指数分析器（Flask 后端）
提供交互式网页：滑杆打分、实时综合指数、雷达图、短板诊断、报告下载。
启动方式：
    .venv/bin/python webapp.py            # 启动并自动打开浏览器
    .venv/bin/python webapp.py --no-browser
"""
import argparse
import os
import sys
import threading
import webbrowser

from flask import Flask, Response, jsonify, render_template, request

import score_rule as rules
import data_model as dm
import report_gen as rg

# 打包后资源（模板）位于临时解压目录；源码运行时位于本文件同目录
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# 演示数据（与 main.py 保持一致，用于「一键填充示例」）
DEMO_SCORES = {
    "diet_food": 8.5, "diet_water": 6.0, "diet_snack": 7.5, "diet_env": 8.0,
    "env_rest": 7.0, "env_toilet": 5.5, "env_climate": 8.0, "env_quiet": 4.0,
    "safe_protect": 6.0, "safe_stress": 4.5, "safe_outing": 7.0,
    "inter_time": 5.0, "inter_quality": 7.5, "inter_affinity": 6.0,
    "inter_response": 7.0, "inter_tolerance": 8.0,
    "play_toys": 5.0, "play_climb": 6.5, "play_exercise": 4.0,
    "health_care": 7.0, "health_medical": 8.0, "health_condition": 7.5,
}

CATEGORY = {
    "diet": "饮食问题",
    "env": "环境问题",
    "safe": "安全问题",
    "inter": "主人互动问题",
    "play": "丰容娱乐问题",
    "health": "护理健康问题",
}


# ============================================================
# 序列化：把 AnalysisResult 转成前端友好的 dict
# ============================================================
def _result_to_dict(result: dm.AnalysisResult) -> dict:
    imap = rules.indicator_map()
    dimensions = []
    for d in result.dimensions:
        dimensions.append({
            "key": d.key,
            "name": d.name,
            "weight": d.weight,
            "average": round(d.average, 2),
            "weighted": round(d.weighted, 2),
            "band": d.band,
            "projected": result.projected_dimensions.get(d.key, d.average),
            "indicators": [
                {
                    "key": i.key,
                    "name": i.name,
                    "score": round(i.score, 2),
                    "band": i.band,
                }
                for i in d.indicators
            ],
        })

    weak = []
    for i in result.weak_indicators:
        _, ind_cfg = imap[i.key]
        weak.append({
            "key": i.key,
            "name": i.name,
            "dimension_name": i.dimension_name,
            "category": CATEGORY.get(i.dimension_key, "其他问题"),
            "score": round(i.score, 2),
            "band": i.band,
            "tips": ind_cfg["tips"],
        })

    return {
        "total": result.total,
        "grade_level": result.grade_level,
        "grade_desc": result.grade_desc,
        "dimensions": dimensions,
        "weak_indicators": weak,
        "projected_total": result.projected_total,
        "projected_delta": result.projected_delta,
    }


# ============================================================
# 路由
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config")
def api_config():
    """返回维度/指标配置 + 演示数据，供前端渲染输入控件。"""
    dims = [
        {
            "key": d["key"],
            "name": d["name"],
            "weight": d["weight"],
            "summary": d["summary"],
            "indicators": [
                {"key": i["key"], "name": i["name"], "desc": i["desc"]}
                for i in d["indicators"]
            ],
        }
        for d in rules.DIMENSIONS
    ]
    return jsonify({"dimensions": dims, "demo_scores": DEMO_SCORES})


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """接收 22 项得分，返回完整分析结果。"""
    payload = request.get_json(silent=True) or {}
    scores = payload.get("scores", {})

    errors = dm.validate_scores(scores)
    if errors:
        return jsonify({"error": errors}), 400

    full = dm.empty_scores()
    full.update({k: float(v) for k, v in scores.items()})
    result = dm.analyze(full)
    return jsonify(_result_to_dict(result))


@app.route("/api/report", methods=["POST"])
def api_report():
    """生成并返回 TXT 报告（供前端下载）。"""
    payload = request.get_json(silent=True) or {}
    scores = payload.get("scores", {})
    full = dm.empty_scores()
    full.update({k: float(v) for k, v in scores.items()})
    result = dm.analyze(full)
    report_text = rg.build_report(result)
    return Response(
        report_text,
        mimetype="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=cat_satisfaction_report.txt"
        },
    )


# ============================================================
# 入口
# ============================================================
def _open_browser(url: str):
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()


def main():
    parser = argparse.ArgumentParser(description="猫咪家庭满意度指数分析器 · Web 版")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口（macOS 上 5000 常被 AirPlay 占用）")
    parser.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print("=" * 60)
    print("🐱 猫咪家庭满意度指数分析器 · Web 版")
    print(f"   请在浏览器访问：{url}")
    print("   按 Ctrl+C 停止服务")
    print("=" * 60)

    if not args.no_browser:
        _open_browser(url)

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()

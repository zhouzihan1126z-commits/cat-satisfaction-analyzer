# -*- coding: utf-8 -*-
"""
main.py —— 程序主入口
负责：终端交互式录入 / JSON 配置录入 / 演示数据，调度四层完成全流程分析。
"""
import argparse
import json
import os
import sys

import score_rule as rules
import data_model as dm
import report_gen as rg
import visual_plot as viz

# 打包为可执行文件（PyInstaller）后，__file__ 指向临时解压目录，
# 因此改用 sys.executable 所在目录，保证数据与输出持久化到可执行文件旁。
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "user_data.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# 演示数据（覆盖高/中/低分，便于查看完整报告效果）
DEMO_SCORES = {
    "diet_food": 8.5, "diet_water": 6.0, "diet_snack": 7.5, "diet_env": 8.0,
    "env_rest": 7.0, "env_toilet": 5.5, "env_climate": 8.0, "env_quiet": 4.0,
    "safe_protect": 6.0, "safe_stress": 4.5, "safe_outing": 7.0,
    "inter_time": 5.0, "inter_quality": 7.5, "inter_affinity": 6.0,
    "inter_response": 7.0, "inter_tolerance": 8.0,
    "play_toys": 5.0, "play_climb": 6.5, "play_exercise": 4.0,
    "health_care": 7.0, "health_medical": 8.0, "health_condition": 7.5,
}


# ============================================================
# 打印横幅
# ============================================================
def print_banner():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         🐱 猫咪家庭满意度指数分析器 🐱                 ║")
    print("║        维度全覆盖 · 数据可量化 · 报告专业化            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


# ============================================================
# 终端交互式录入
# ============================================================
def _prompt_score(name: str, desc: str, default: float) -> float:
    while True:
        raw = input(f"    · {name}（参考：{desc}）\n"
                    f"      请打分 0-10 [默认 {default}]: ").strip()
        if raw == "":
            return default
        if raw.lower() == "q":
            raise KeyboardInterrupt
        try:
            val = float(raw)
        except ValueError:
            print("      ⚠ 请输入数字（0-10）。")
            continue
        if 0.0 <= val <= 10.0:
            return val
        print("      ⚠ 分数需在 0-10 之间。")


def interactive_input(existing: dict) -> dict:
    """逐维度逐指标交互录入，支持回车使用默认值、q 退出。"""
    print("开始逐项打分（输入数字回车；直接回车使用默认值 7；输入 q 随时退出）\n")
    scores = dict(existing)
    try:
        for dim in rules.DIMENSIONS:
            print(f"▶ 维度：{dim['name']}（权重 {dim['weight']}%）")
            for ind in dim["indicators"]:
                default = scores.get(ind["key"], 7.0)
                scores[ind["key"]] = _prompt_score(ind["name"], ind["desc"], default)
            print()
    except KeyboardInterrupt:
        print("\n已退出录入，使用已填写的分数继续。\n")
    return scores


# ============================================================
# 数据加载 / 保存
# ============================================================
def load_json_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("scores", {}) if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠ 读取 {DATA_FILE} 失败：{e}，将忽略。")
        return {}


def save_json_data(scores: dict):
    payload = {
        "description": "猫咪家庭满意度分析器数据缓存，可手动修改 scores 中的分值（0-10）。",
        "scores": {k: round(float(v), 2) for k, v in scores.items()},
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"✓ 数据已保存至 {DATA_FILE}")


# ============================================================
# 核心流程
# ============================================================
def run_analysis(scores: dict, output_dir: str):
    # 校验
    errors = dm.validate_scores(scores)
    if errors:
        print("⚠ 数据校验失败：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 缺失指标补 0
    full = dm.empty_scores()
    full.update(scores)

    print("正在计算……")
    result = dm.analyze(full)

    # 输出摘要
    print("\n" + "=" * 60)
    print(f"综合满意度指数：{result.total} / 100")
    print(f"满意度评级：{result.grade_level}")
    print(f"评级解读：{result.grade_desc}")
    print("=" * 60 + "\n")

    # 生成报告与图表
    report_path = rg.write_report(result, output_dir)
    chart_paths = viz.generate_all_charts(result, output_dir)

    print(f"✓ 分析报告已生成：{report_path}")
    for p in chart_paths:
        print(f"✓ 图表已生成：{p}")

    # 打印报告全文到终端
    print("\n" + rg.build_report(result))
    return result


# ============================================================
# 命令行入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="猫咪家庭满意度指数分析器 —— 全方位量化分析猫咪居家幸福感"
    )
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="交互式逐项录入（默认模式）")
    parser.add_argument("--json", "-j", action="store_true",
                        help="直接读取 user_data.json 进行分析")
    parser.add_argument("--demo", "-d", action="store_true",
                        help="使用内置演示数据运行")
    parser.add_argument("--output", "-o", default=OUTPUT_DIR,
                        help="输出目录（默认 ./output）")
    args = parser.parse_args()

    output_dir = args.output

    print_banner()

    # 配置校验
    config_errors = rules.validate_config()
    if config_errors:
        print("⚠ 配置错误：")
        for e in config_errors:
            print(f"  - {e}")
        sys.exit(1)

    if args.demo:
        print("模式：演示数据运行")
        run_analysis(DEMO_SCORES, output_dir)
        return

    if args.json:
        print("模式：读取 user_data.json")
        scores = load_json_data()
        if not scores:
            print("⚠ user_data.json 不存在或为空，可先使用交互模式录入，或使用 --demo。")
            sys.exit(1)
        run_analysis(scores, output_dir)
        return

    # 默认：交互式录入
    print("模式：交互式录入")
    scores = load_json_data()
    scores = interactive_input(scores)
    save_json_data(scores)
    run_analysis(scores, output_dir)


if __name__ == "__main__":
    main()

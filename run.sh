#!/bin/bash
# ============================================================
# 猫咪家庭满意度指数分析器 —— 终端启动脚本
# 用法：
#   ./run.sh            # 交互式录入（默认）
#   ./run.sh --json     # 读取 user_data.json
#   ./run.sh --demo     # 演示数据
# ============================================================
cd "$(dirname "$0")"

# 优先使用已打包的可执行文件，否则回退到虚拟环境运行源码
if [ -x "./dist/cat_satisfaction_analyzer" ]; then
    exec ./dist/cat_satisfaction_analyzer "$@"
elif [ -x "./.venv/bin/python" ]; then
    exec ./.venv/bin/python main.py "$@"
else
    echo "⚠ 未找到可执行文件或虚拟环境。"
    echo "  请先运行：python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

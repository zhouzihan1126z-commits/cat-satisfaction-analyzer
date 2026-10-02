#!/bin/bash
# ============================================================
# 猫咪家庭满意度指数分析器 —— 双击启动入口 (macOS)
# 双击本文件即可运行；也可在终端执行 ./start.command
# ============================================================
cd "$(dirname "$0")"

# 优先使用已打包的可执行文件，否则回退到虚拟环境运行源码
if [ -x "./dist/cat_satisfaction_analyzer" ]; then
    echo "▶ 使用打包版可执行文件运行..."
    ./dist/cat_satisfaction_analyzer "$@"
elif [ -x "./.venv/bin/python" ]; then
    echo "▶ 使用虚拟环境运行源码..."
    ./.venv/bin/python main.py "$@"
else
    echo "⚠ 未找到可执行文件或虚拟环境。"
    echo "  请先运行：python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 运行结束后停留，便于在双击打开时查看结果
echo ""
echo "============================================================"
echo "运行结束。输出文件位于 output/ 目录（报告 + 图表）。"
echo "按回车键关闭本窗口..."
read -r _

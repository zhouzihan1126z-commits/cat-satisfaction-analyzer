#!/bin/bash
# ============================================================
# 猫咪家庭满意度指数分析器 —— 网页版终端启动脚本
# 用法：
#   ./run_web.sh            # 启动并自动打开浏览器
#   ./run_web.sh --port 8000
# ============================================================
cd "$(dirname "$0")"

if [ -x "./.venv/bin/python" ]; then
  exec ./.venv/bin/python webapp.py "$@"
else
  exec python3 webapp.py "$@"
fi

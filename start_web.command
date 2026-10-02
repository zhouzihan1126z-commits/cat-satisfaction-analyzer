#!/bin/bash
# ============================================================
# 猫咪家庭满意度指数分析器 —— 网页版双击启动入口 (macOS)
# 双击本文件：自动启动 Web 服务并在浏览器打开交互界面
# ============================================================
cd "$(dirname "$0")"

# 自动寻找一个可用端口，避免端口被占用（5000 常被 macOS AirPlay 占用）
PORT=8000
if command -v lsof >/dev/null 2>&1 && lsof -i :$PORT -t >/dev/null 2>&1; then
  PORT=8080
fi

echo "🐱 正在启动猫咪家庭满意度指数分析器（网页版）..."
echo "   浏览器将自动打开：http://127.0.0.1:$PORT"
echo "   关闭本窗口即可停止服务。"
echo "============================================================"

# 优先使用虚拟环境；若不存在则尝试系统 python3
if [ -x "./.venv/bin/python" ]; then
  exec ./.venv/bin/python webapp.py --port $PORT
else
  exec python3 webapp.py --port $PORT
fi

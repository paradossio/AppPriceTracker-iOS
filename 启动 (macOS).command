#!/bin/bash
# macOS 双击启动器
# 这个文件双击即可启动 App 价格雷达
cd "$(dirname "$0")"

# 检测 Python 3
if command -v python3 &> /dev/null; then
    PY=python3
elif command -v python &> /dev/null && python -c "import sys; sys.exit(0 if sys.version_info[0]==3 else 1)"; then
    PY=python
else
    osascript -e 'display dialog "未检测到 Python 3。\n\nmacOS 通常自带 Python 3，请打开终端运行：\n  python3 --version\n\n如未安装，请前往 https://www.python.org/downloads/ 下载。" buttons {"好的"} default button 1 with icon stop'
    exit 1
fi

clear
echo ""
echo "  正在启动 App Store 全球比价工具..."
echo ""
$PY AppPriceTracker.py

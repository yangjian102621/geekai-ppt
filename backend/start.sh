#!/bin/bash
# 后端 API 启动脚本
# 功能：创建虚拟环境、安装依赖、启动服务

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 虚拟环境目录名
VENV_DIR="venv"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI PPT Backend 启动脚本 ===${NC}"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}检测到 Python: ${PYTHON_VERSION}${NC}"

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source "$VENV_DIR/bin/activate"

# 升级 pip
echo -e "${YELLOW}升级 pip...${NC}"
pip install --upgrade pip --quiet

# 安装依赖
echo -e "${YELLOW}安装依赖包...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}依赖安装完成${NC}"
else
    echo -e "${RED}错误: 未找到 requirements.txt${NC}"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到 .env 文件，将创建默认配置${NC}"
    cat > .env << EOF
API_KEY=
BASE_URL=https://api.geekai.pro
MODEL_LOGIC=google/gemini-3-pro-preview
MODEL_IMAGE=gemini-2.5-pro
PORT=8002
EOF
    echo -e "${YELLOW}请编辑 .env 文件设置你的 API_KEY${NC}"
fi

# 创建必要的目录
mkdir -p storage/images
mkdir -p storage/sessions

# 启动服务
echo -e "${GREEN}启动 FastAPI 服务...${NC}"
echo -e "${GREEN}服务将在 http://localhost:8002 运行${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

python3 main.py

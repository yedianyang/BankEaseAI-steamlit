#!/bin/bash

# BankEaseAI Development Startup Script
# This script starts both the backend API and frontend development servers

echo "🚀 Starting BankEaseAI Development Environment"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -f "start_dev.sh" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建完成${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}🔧 激活虚拟环境...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# Check and install dependencies
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}📦 安装后端依赖 (使用 requirements.txt)...${NC}"
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
    echo ""
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
    echo ""
fi

# Clean up ports
echo -e "${BLUE}🧹 清理端口...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
echo -e "${GREEN}✓ 端口已清理${NC}"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在关闭服务...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    deactivate 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend API
echo -e "${BLUE}📡 启动后端 API (端口 8000)...${NC}"
cd "$(dirname "$0")"
# 使用虚拟环境的 python 并设置 PYTHONPATH
PYTHONPATH=$(pwd) venv/bin/python api/main_v2.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ 后端已启动 (PID: $BACKEND_PID)${NC}"
echo ""

# Wait for backend to initialize
echo -e "${BLUE}⏳ 等待后端初始化...${NC}"
sleep 3
echo -e "${GREEN}✓ 后端就绪${NC}"
echo ""

# Start Frontend
echo -e "${BLUE}🎨 启动前端 (端口 3000)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ 前端启动 (PID: $FRONTEND_PID)${NC}"
echo ""

echo "=============================================="
echo -e "${GREEN}✅ 开发环境启动成功！${NC}"
echo ""
echo "📍 访问地址:"
echo "   后端 API:    http://localhost:8000"
echo "   API 文档:    http://localhost:8000/docs"
echo "   前端页面:    http://localhost:3000"
echo ""
echo "💡 按 Ctrl+C 停止所有服务"
echo "=============================================="

# Wait for processes
wait

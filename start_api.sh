#!/bin/bash

# BankEaseAI API 服务启动脚本

# 设置环境变量
export STREAMLIT_ENV=production
export JWT_SECRET_KEY="your-super-secret-jwt-key-change-in-production"

# 激活虚拟环境
source bankeaseai/bin/activate

# 启动API服务
echo "🚀 启动 BankEaseAI API 服务..."
echo "📖 API文档: http://localhost:8000/docs"
echo "🔍 健康检查: http://localhost:8000/health"
echo ""

# 使用uvicorn启动FastAPI应用（主版本 - 集成真实业务逻辑）
uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info

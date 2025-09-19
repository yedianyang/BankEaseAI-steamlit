#!/bin/bash
# 生产环境启动脚本

# 设置生产环境变量
export STREAMLIT_ENV=production
export PYTHONWARNINGS=ignore

# 设置数据库路径
export DB_PATH=/var/lib/bankeaseai/users.db

# 设置输出目录
export OUTPUT_DIR=/tmp/bankeaseai

# 激活虚拟环境
source bankeaseai/bin/activate

# 启动应用
python -m streamlit run script/main.py --server.port 8501 --server.address 0.0.0.0

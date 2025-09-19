# script/config/imports.py
"""
统一的导入配置
解决相对导入问题
"""
import os
import sys
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPT_ROOT = Path(__file__).parent.parent

# 添加路径到sys.path
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 标准化的导入函数
def get_script_path():
    """获取script目录的绝对路径"""
    return SCRIPT_ROOT

def get_project_path():
    """获取项目根目录的绝对路径"""
    return PROJECT_ROOT

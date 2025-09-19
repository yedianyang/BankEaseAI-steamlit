# script/__init__.py
"""
BankEaseAI - 银行账单处理应用
"""

__version__ = "1.0.0"
__author__ = "BankEaseAI Team"

# 确保所有子模块可以被正确导入
from . import controllers
from . import views
from . import utils
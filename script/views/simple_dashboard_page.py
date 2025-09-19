# script/views/simple_dashboard_page.py
import streamlit as st
import sys
import os
from datetime import datetime

# 添加路径以便导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.api_client import get_api_client

class SimpleDashboardPage:
    """简化的用户仪表板页面（使用API）"""
    
    def __init__(self):
        self.api_client = get_api_client()
    
    def render(self):
        """渲染仪表板页面"""
        if not st.session_state.get('logged_in') or not st.session_state.get('user'):
            st.warning("请先登录以查看仪表板")
            return
        
        # 检查API服务状态
        if not self.api_client.check_api_health():
            st.error("⚠️ API服务未运行，请先启动API服务")
            st.info("运行命令: `./start_api.sh`")
            return
        
        user = st.session_state.user
        
        # 页面标题
        st.title(f"📊 欢迎, {user['username']}!")
        st.markdown("---")
        
        # 获取仪表板数据
        with st.spinner("正在加载数据..."):
            stats = self.api_client.get_dashboard_stats()
        
        if "error" in stats:
            st.error(f"加载数据失败: {stats['error']}")
            return
        
        # 用户信息卡片
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("当前计划", stats['user_info']['plan'].upper())
        
        with col2:
            usage_stats = stats['usage_stats']
            st.metric("本月已处理", f"{usage_stats['monthly_usage']}/{usage_stats['plan_limits']['max_files']} 文件")
        
        with col3:
            st.metric("剩余额度", f"{usage_stats['remaining']} 文件")
        
        # 使用进度条
        st.markdown("### 📈 使用进度")
        progress = usage_stats['monthly_usage'] / usage_stats['plan_limits']['max_files']
        st.progress(progress)
        
        if progress >= 0.8:
            st.warning("⚠️ 使用量接近限制，请考虑升级计划")
        elif progress >= 0.5:
            st.info("ℹ️ 使用量已过半")
        
        # 快速操作
        st.markdown("### 🚀 快速操作")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 开始转换PDF", use_container_width=True):
                st.session_state.current_page = "转换为iCost模版"
                st.rerun()
        
        with col2:
            if st.button("📊 查看详细统计", use_container_width=True):
                self._show_detailed_stats(stats)
        
        # 账户管理
        st.markdown("### ⚙️ 账户管理")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 刷新数据", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🚪 退出登录", use_container_width=True):
                self._logout()
    
    def _show_detailed_stats(self, stats):
        """显示详细统计信息"""
        st.markdown("### 📊 详细使用统计")
        
        # 显示总体统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总用户数", stats['database_stats']['user_count'])
        with col2:
            st.metric("总处理次数", stats['database_stats']['log_count'])
        with col3:
            st.metric("数据库大小", f"{stats['database_stats']['db_size_mb']} MB")
        
        # 显示使用情况
        usage_stats = stats['usage_stats']
        st.markdown("### 📈 使用历史")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("本月使用", f"{usage_stats['monthly_usage']} 次")
        with col2:
            st.metric("累计使用", f"{usage_stats['total_usage']} 次")
        
        # 显示计划信息
        st.markdown("### 💎 计划详情")
        user_info = stats['user_info']
        plan_limits = usage_stats['plan_limits']
        
        st.info(f"""
        **当前计划：{user_info['plan'].upper()}**
        - 每月最大处理文件数：{plan_limits['max_files']} 个
        - 支持格式：PDF
        - 输出格式：Excel, CSV
        """)
    
    def _logout(self):
        """登出用户"""
        self.api_client.logout()
        st.success("已成功退出登录")
        st.rerun()

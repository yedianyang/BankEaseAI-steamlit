# script/views/simple_auth_page.py
import streamlit as st
import sys
import os

# 添加路径以便导入utils模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.api_client import get_api_client

class SimpleAuthPage:
    """简化的用户认证页面（使用API）"""
    
    def __init__(self):
        self.api_client = get_api_client()
    
    def render(self):
        """渲染认证页面"""
        st.title("🔐 用户登录")
        st.markdown("---")
        
        # 检查API服务状态
        if not self.api_client.check_api_health():
            st.error("⚠️ API服务未运行，请先启动API服务")
            st.info("运行命令: `./start_api.sh`")
            return
        
        # 创建标签页
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            st.subheader("登录账户")
            
            with st.form("login_form"):
                username = st.text_input("用户名", key="login_username")
                password = st.text_input("密码", type="password", key="login_password")
                
                login_button = st.form_submit_button("登录", use_container_width=True)
                
                if login_button:
                    if username and password:
                        with st.spinner("正在登录..."):
                            result = self.api_client.login(username, password)
                            
                        if "access_token" in result:
                            st.success(f"欢迎回来, {result['user']['username']}!")
                            st.rerun()
                        elif "error" in result:
                            st.error(result["error"])
                    else:
                        st.error("请填写用户名和密码")
        
        with tab2:
            st.subheader("注册新账户")
            
            with st.form("register_form"):
                new_username = st.text_input("用户名", key="register_username")
                new_email = st.text_input("邮箱", key="register_email")
                new_password = st.text_input("密码", type="password", key="register_password")
                confirm_password = st.text_input("确认密码", type="password", key="confirm_password")
                
                register_button = st.form_submit_button("注册", use_container_width=True)
                
                if register_button:
                    if new_username and new_email and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("两次输入的密码不一致")
                        elif len(new_password) < 6:
                            st.error("密码长度至少6位")
                        else:
                            with st.spinner("正在注册..."):
                                result = self.api_client.register(new_username, new_email, new_password)
                            
                            if result.get("success"):
                                st.success("注册成功！请使用新账户登录。")
                            elif "error" in result:
                                st.error(result["error"])
                    else:
                        st.error("请填写所有字段")
        
        # 显示使用说明
        st.markdown("---")
        st.info("""
        **使用说明：**
        - 免费用户每月可处理5个PDF文件
        - 注册后即可开始使用PDF转换功能
        - 如需更多使用量，请联系管理员升级计划
        """)
    
    def logout(self):
        """登出用户"""
        self.api_client.logout()
        st.rerun()

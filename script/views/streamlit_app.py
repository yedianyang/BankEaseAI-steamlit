# views/streamlit_app.py
import streamlit as st
from typing import Optional
from .conversion_to_icost_page_web import ConversionToiCostPage
# 导入简化的认证页面
from .simple_auth_page import SimpleAuthPage
from .simple_dashboard_page import SimpleDashboardPage
# from .auth_modal import AuthModal  # 已删除弹窗功能
#from .settings_page import SettingsPage

class BankStatementView:
    """银行账单处理应用的视图层
    
    遵循 macOS 设计标准:
    - 清晰的信息层级
    - 一致的交互模式
    - 高效的空间利用
    """
    
    def __init__(self, controller=None):
        """初始化视图
        
        Args:
            controller: 控制器实例，处理用户交互
        """
        self.controller = controller
        # 初始化简化的认证页面
        self.conversion_to_icost_page_web = ConversionToiCostPage(controller)
        self.simple_auth_page = SimpleAuthPage()
        self.simple_dashboard_page = SimpleDashboardPage()
        # self.auth_modal = AuthModal()  # 已删除弹窗功能
        #self.settings_page = SettingsPage(controller)
        # Help page will be implemented later
        #self.help_page = HelpPage(controller)
        self._configure_page()
    
    def _configure_page(self):
        """配置页面基本设置"""
        # 设置标题字体大小
        st.markdown("""
            <style>
                .title {
                    font-size: 5rem !important;
                }
            </style>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> str:
        """渲染侧边栏导航
        
        Returns:
            str: 当前选中的页面名称
        """
        with st.sidebar:
            st.title("💰BankEase AI")
            st.markdown("---")
            
            # 注入符合 macOS 设计规范的 CSS
            st.markdown("""
                <style>
                    /* 基础按钮样式 - 统一宽度为100% */
                    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > button {
                        width: 100%;
                        padding: 0.5rem 1.5rem;
                        border-radius: 8px;
                        margin: 0.1rem 0;
                        transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                        font-size: 0.95rem;
                        text-align: left;
                        border: none;
                        background: transparent;
                        color: inherit;
                    }
                    
                    /* Hover 状态 */
                    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > button:hover {
                        background: rgba(255, 0, 0, 0.05) !important;
                        color: #000 !important;
                    }
                    
                    /* 选中状态 */
                    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > button[data-selected="true"] {
                        background: rgba(100, 122, 255, 0.1) !important;
                        color: #000 !important;
                        font-weight: 500;
                        border-left: 3px solid #007AFF;
                    }
                    
                    /* 点击反馈 */
                    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > button:active {
                        background: rgba(100, 122, 255, 0.2) !important;
                    }
                    
                    /* 统一按钮宽度和间距 */
                    .stSidebar .stButton > button {
                        width: 100%;
                        min-width: 240px;
                        margin: 2px 0;
                    }
            """, unsafe_allow_html=True)
            
            # 移除强制登录检查，允许未登录用户访问主页面
            # if not st.session_state.get('logged_in', False):
            #     # 显示登录页面
            #     self.simple_auth_page.render()
            #     return
            
            # 获取当前页面
            current_page = st.session_state.get('current_page', "转换为iCost模版")
            
            # 导航选项（根据登录状态显示不同选项）
            if st.session_state.get('logged_in', False):
                pages = {
                    "仪表板": "📊",
                    "转换为iCost模版": "🔄",
                    "账户设置": "⚙️",
                    #"帮助": "🆘",
                }
            else:
                pages = {
                    "转换为iCost模版": "🔄",
                    #"帮助": "🆘",
                }
            
            def nav_callback(page_name):
                st.session_state.current_page = page_name
            
            for page, icon in pages.items():
                is_selected = current_page == page
                # 使用按钮替代markdown来实现点击交互
                if st.button(
                    f"{icon} {page}",
                    key=f"nav_{page}",
                    type="secondary" if not is_selected else "primary",
                    on_click=nav_callback,
                    args=(page,)
                ):
                    pass
            
            # 添加登录/注册按钮
            st.markdown("---")
            if st.session_state.get('logged_in', False):
                # 已登录用户显示用户信息和退出按钮
                user = st.session_state.get('user', {})
                st.write(f"👤 {user.get('username', '用户')}")
                if st.button("🚪 退出登录", key="logout_btn", use_container_width=True):
                    # 使用API客户端登出
                    from script.utils.api_client import get_api_client
                    api_client = get_api_client()
                    api_client.logout()
                    st.rerun()
            else:
                # 未登录用户显示登录/注册按钮
                if st.button("🔐 登录/注册", key="login_btn", use_container_width=True):
                    st.session_state.current_page = "账户设置"
                    st.rerun()
            
            return current_page
    def render(self):
        
        """渲染主界面"""
        # 渲染侧边栏并获取选中的页面
        selected_page = self.render_sidebar()
        
        # 弹窗功能已删除，直接跳转到账户设置页面
        
        # 如果用户未登录，render_sidebar会直接渲染登录页面并返回None
        if selected_page is None:
            return
        
        # 根据选择渲染对应页面
        page_mapping = {
            "仪表板": self.simple_dashboard_page.render,
            "转换为iCost模版": self.conversion_to_icost_page_web.render,
            "账户设置": self.simple_auth_page.render,
            #"帮助": self.help_page.render,
        }
        
        # 确保selected_page在page_mapping中存在
        if selected_page in page_mapping:
            page_mapping[selected_page]()
        else:
            # 如果页面不存在，默认显示仪表板
            self.simple_dashboard_page.render()
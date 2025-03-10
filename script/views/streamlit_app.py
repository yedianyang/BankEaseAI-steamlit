# views/streamlit_app.py
import streamlit as st
from typing import Optional
from .conversion_to_icost_page_web import ConversionToiCostPage
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
        self.conversion_to_icost_page_web = ConversionToiCostPage(controller)
        #self.settings_page = SettingsPage(controller)
        # Help page will be implemented later
        #self.help_page = HelpPage(controller)
        self._configure_page()
    
    def _configure_page(self):
        """配置页面基本设置"""
        st.set_page_config(
            page_title="BankEase AI",
            page_icon="💰",
            # layout: 控制页面布局
            # - "wide": 页面使用全宽布局，适合展示大量内容
            # - "centered": 页面内容居中，宽度受限，适合阅读
            layout="centered",  
            
            # initial_sidebar_state: 控制侧边栏初始状态
            # - "expanded": 侧边栏默认展开
            # - "collapsed": 侧边栏默认折叠
            # - "auto": 根据屏幕宽度自动决定
            initial_sidebar_state="auto",
        )
        
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
            
            # 获取当前页面
            current_page = st.session_state.get('current_page', "转换为iCost模版")
            
            # 导航选项
            pages = {
                "转换为iCost模版": "",
                #"设置": "",
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
            return current_page
    def render(self):
        
        """渲染主界面"""
        # 渲染侧边栏并获取选中的页面
        selected_page = self.render_sidebar()
        
        # 根据选择渲染对应页面
        page_mapping = {
            "转换为iCost模版": self.conversion_to_icost_page_web.render,
            #"转换为iCost模版": self.conversion_to_icost_page.render,
            #"设置": self.settings_page.render,
            #"帮助": self.help_page.render,
        }
        page_mapping[selected_page]()
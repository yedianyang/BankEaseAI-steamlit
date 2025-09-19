# script/main.py
import streamlit as st
import os

# 必须在任何其他Streamlit命令之前调用
st.set_page_config(
    page_title="BankEase AI",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="auto",
)

from views import BankStatementView
from controllers import BankStatementController

def main():
    # 初始化控制器和视图
    output_dir = os.environ.get("OUTPUT_DIR", "/tmp")
    controller = BankStatementController(
        output_dir=output_dir,
        model="gpt-4o",
        temperature=0.3
    )
    
    # 初始化并显示视图
    view = BankStatementView(controller=controller)
    view.render()

if __name__ == "__main__":
    main()
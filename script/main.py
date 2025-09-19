# script/main.py
from views import BankStatementView
from controllers import BankStatementController
import os

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
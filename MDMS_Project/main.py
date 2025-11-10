# main.py
import sys
from PySide6.QtWidgets import QApplication
from mdms.controllers.main_controller import MainController
from mdms.database.models import Base
from mdms.database.session import engine

def main():
    # 初始化数据库 (如果表不存在，则创建)
    # 在生产环境中，你会使用 Alembic 来管理数据库迁移
    print("正在初始化数据库，创建表结构...")
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成。")

    # 创建 Qt 应用实例
    app = QApplication(sys.argv)
    
    # 创建主控制器
    controller = MainController()
    
    # 显示主窗口
    controller.show()
    
    # 启动应用事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
# mdms/controllers/main_controller.py

from PySide6.QtWidgets import QMessageBox # 举例，导入可能需要的对话框
from ..views.main_window import MainWindow
from ..database.session import SessionLocal
from ..database.models import Movie

class MainController:
    def __init__(self):
        # 1. 创建 View 的实例
        self.view = MainWindow() 
        
        # 2. 创建数据库会话
        self.db_session = SessionLocal()

    def show(self):
        """显示主窗口"""
        # 显示的是加载了UI的QMainWindow实例，即 self.view.ui
        self.view.show()

    def __del__(self):
        """确保在程序退出时关闭数据库会话"""
        if self.db_session:
            print("关闭数据库会-话...")
            self.db_session.close()
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

        # 3. 将 View 中的信号连接到 Controller 的方法（槽）
        self.connect_signals()

    def connect_signals(self):
        """集中管理所有信号和槽的连接"""
        # 这里的 self.view.ui 是从 MainWindow 实例中访问加载的 UI 对象
        # 然后访问 UI 对象上的控件，比如名为 button_search 的 QPushButton
        try:
            self.view.ui.button_search.clicked.connect(self.search_movies)
            # 在这里连接其他所有信号，例如：
            # self.view.ui.button_add.clicked.connect(self.open_add_dialog)
            # self.view.ui.table_widget.itemDoubleClicked.connect(self.edit_movie)
        except AttributeError as e:
            # 如果 .ui 文件中的控件名写错了，这里会报错，给出清晰的提示
            print(f"连接信号时出错: {e}")
            print("请检查你的 .ui 文件中的控件名称是否与代码中的一致。")


    def search_movies(self):
        """处理搜索按钮点击事件的逻辑"""
        print("搜索按钮被点击了！现在由 Controller 来处理这个逻辑。")
        
        # 示例：从数据库查询数据并打印
        try:
            movie_count = self.db_session.query(Movie).count()
            print(f"数据库中共有 {movie_count} 部电影。")
            
            # 可以在这里弹出一个简单的消息框来验证交互
            QMessageBox.information(self.view.ui, "提示", "搜索功能已被触发！")

        except Exception as e:
            print(f"数据库查询失败: {e}")
            QMessageBox.critical(self.view.ui, "错误", f"数据库操作失败: {e}")

    def show(self):
        """显示主窗口"""
        # 显示的是加载了UI的QMainWindow实例，即 self.view.ui
        self.view.ui.show()

    def __del__(self):
        """确保在程序退出时关闭数据库会话"""
        if self.db_session:
            print("关闭数据库会-话...")
            self.db_session.close()
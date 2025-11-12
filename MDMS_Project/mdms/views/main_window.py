# mdms/views/main_window.py
import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 它的职责就是加载 UI 文件，没有其他任何逻辑
        
        ui_file_path = os.path.join(os.path.dirname(__file__), "ui/main_window.ui")
        ui_file = QFile(ui_file_path)
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
            return

        loader = QUiLoader()
        # 将加载的UI顶级窗口（QMainWindow）赋值给 self.ui
        # 第二个参数 self 是可选的，但有时有助于解决某些控件的父子关系问题
        self.ui = loader.load(ui_file, self)
        
        ui_file.close()

        # 检查 UI 是否成功加载
        if not self.ui:
            print(loader.errorString())
            return
            
        # 将加载的 UI 设置为中央部件 (如果你的 .ui 文件顶级对象是 QWidget)
        # 如果 .ui 文件的顶级对象是 QMainWindow，这一步通常由 loader.load(ui_file, self) 自动处理
        # self.setCentralWidget(self.ui) # 如果顶级是QWidget，取消这行注释
        
    # 注意：这里不应该有任何业务逻辑，比如 on_button_click() 之类的方法。
    # 所有事件处理都应该在 Controller 中完成。
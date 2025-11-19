import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale
from qfluentwidgets import FluentTranslator

# 导入你的窗口类
# 请确保路径正确，根据你的项目结构调整 import
from mdms.views.login.login_window import LoginWindow
from mdms.views.main_window import MainWindow


def main():
    # 1. 初始化 Application
    app = QApplication(sys.argv)

    # 国际化设置 (FluentWidgets)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)

    # 2. 创建登录窗口
    login_window = LoginWindow()

    # 定义切换到主界面的函数
    def show_main_window():
        # 创建主窗口
        # MainWindow 初始化时会读取 user_manager 的状态
        # 因为 LoginWindow 已经执行了 user_manager.login(user)，
        # 所以此时 MainWindow 能正确识别管理员/普通用户
        window = MainWindow()
        window.show()

        # 注意：必须保持对 window 的引用，否则会被垃圾回收导致窗口一闪而过
        # 我们将其挂载到 app 实例上，或者声明为全局变量
        app.main_window = window

    # 3. 连接信号
    # 当登录窗口发出 loginSuccess 信号时，执行 show_main_window
    login_window.loginSuccess.connect(show_main_window)

    # 4. 显示登录窗口
    login_window.show()

    # 5. 进入事件循环
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
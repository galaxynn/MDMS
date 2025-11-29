import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale
from qfluentwidgets import FluentTranslator

from mdms.views.login.login_window import LoginWindow
from mdms.views.main_window import MainWindow
from mdms.common.user_manager import user_manager


class ApplicationController:
    """应用程序控制器，管理窗口切换"""

    def __init__(self):
        self.app = QApplication(sys.argv)

        # 国际化设置
        translator = FluentTranslator(QLocale())
        self.app.installTranslator(translator)

        self.login_window = None
        self.main_window = None

    def show_login(self):
        """显示登录窗口"""
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_window = LoginWindow()
        self.login_window.loginSuccess.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self):
        """显示主窗口"""
        if self.login_window:
            self.login_window.close()
            self.login_window = None

        self.main_window = MainWindow()
        # 连接退出登录信号
        self.main_window.logoutRequested.connect(self.show_login)
        self.main_window.show()

    def run(self):
        """运行应用程序"""
        self.show_login()
        return self.app.exec()


def main():
    controller = ApplicationController()
    sys.exit(controller.run())


if __name__ == '__main__':
    main()
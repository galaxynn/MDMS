# mdms/views/main_window.py
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QApplication)
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SubtitleLabel,
                            setFont, PushButton, FluentIcon as FIF)
from mdms.common.user_manager import user_manager
from mdms.views.movie_interface import MovieInterface
from mdms.views.my_review_interface import MyReviewInterface
# 新增导入
from mdms.views.setting_interface import SettingInterface


class Widget(QFrame):
    """
    通用占位组件
    用于快速生成尚未开发的页面
    """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)
        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class MainWindow(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 1. [Module 2 & 4] 电影核心浏览 (Core Database & Display)
        # 首页：电影海报墙、搜索、点击进入详情
        self.homeInterface = MovieInterface('Movie Library', self)

        # 影人浏览页：搜索导演、演员
        self.peopleInterface = Widget('People Library', self)

        # 2. [Module 3] 用户中心 (Review System)
        # 我的影评：用户查看、修改、删除自己发布的评论
        # 未来功能：列出当前用户的所有 Review，点击可修改
        self.myReviewInterface = MyReviewInterface('My Reviews', self)

        # 3. [Module 1 & 2] 管理员后台 (Admin Management)
        # 数据管理：电影录入(C)、修改(U)、删除(D)；用户管理
        self.adminInterface = None
        if user_manager.is_logged_in and user_manager.current_user.role == 'admin':
            self.adminInterface = Widget('Admin Data Management', self)

        # 4. 系统设置 - 替换为真正的设置界面
        self.settingInterface = SettingInterface('Settings', self)
        # 连接退出登录信号
        self.settingInterface.logoutRequested.connect(self.handle_logout)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        # --- 顶部导航 (普通用户常用) ---

        # 1. 首页 (浏览电影)
        self.addSubInterface(self.homeInterface, FIF.HOME, '电影库')

        # 2. 演职人员 (浏览导演/演员)
        self.addSubInterface(self.peopleInterface, FIF.PEOPLE, '演职人员')

        # 3. 我的影评 (用户个人数据)
        self.addSubInterface(self.myReviewInterface, FIF.CHAT, '我的影评')

        self.navigationInterface.addSeparator()

        # --- 滚动/底部导航 (管理与设置) ---
        # 4. 管理后台 (建议只对管理员显示)
        # 功能包含：
        # - 电影管理 (添加/编辑电影)
        # - 人员管理 (添加/编辑演员)
        # - 用户管理 (封禁用户)
        # 为管理员动态添加此导航项
        if user_manager.is_logged_in and user_manager.current_user.role == 'admin':
            self.addSubInterface(self.adminInterface, FIF.EDIT, '数据管理', NavigationItemPosition.SCROLL)

        # 5. 设置
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1000, 700)  # 稍微宽一点以容纳详情
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('电影资料库管理系统 (MDMS)')

    def handle_logout(self):
        """处理退出登录"""
        # 关闭主窗口
        self.close()

        # 重新显示登录窗口
        from mdms.views.login.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()


if __name__ == '__main__':
    # 开启高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
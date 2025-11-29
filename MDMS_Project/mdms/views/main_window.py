import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import NavigationItemPosition, FluentWindow, FluentIcon as FIF

from mdms.common.user_manager import user_manager
from mdms.views.admin.admin_interface import AdminInterface
from mdms.views.movie.movie_interface import MovieInterface
from mdms.views.my_review.my_review_interface import MyReviewInterface
from mdms.views.people.people_interface import PeopleInterface
from mdms.views.setting.setting_interface import SettingInterface
# 新增导入
from mdms.views.top100.top100_interface import Top100Interface


class MainWindow(FluentWindow):
    """ 主界面 """

    # 定义退出登录信号
    logoutRequested = Signal()

    def __init__(self, test_mode=False):
        super().__init__()

        # 测试标志，用于强制显示管理员界面
        self.test_mode = test_mode

        # 电影核心浏览
        self.MovieInterface = MovieInterface('Movie Library', self)

        # 新增：TOP100页面
        self.top100Interface = Top100Interface('TOP 100 Movies', self)

        # 影人浏览页：搜索导演、演员
        self.peopleInterface = PeopleInterface('People Library', self)

        # 用户中心
        self.myReviewInterface = MyReviewInterface('My Reviews', self)

        # 管理员后台
        self.adminInterface = None
        if (user_manager.is_logged_in and user_manager.session_role == 'admin') or self.test_mode:
            self.adminInterface = AdminInterface('Admin Data Management', self)

        # 系统设置
        self.settingInterface = SettingInterface('Settings', self)
        self.settingInterface.logoutRequested.connect(self.handle_logout)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        """初始化导航栏"""

        # 首页 (浏览电影)
        self.addSubInterface(self.MovieInterface, FIF.HOME, '电影库')

        # 新增：TOP100页面 - 使用肯定存在的HEART图标
        self.addSubInterface(self.top100Interface, FIF.HEART, 'TOP100')

        # 演职人员 (浏览导演/演员)
        self.addSubInterface(self.peopleInterface, FIF.PEOPLE, '演职人员')

        # 我的影评 (用户个人数据)
        self.addSubInterface(self.myReviewInterface, FIF.CHAT, '我的影评')

        self.navigationInterface.addSeparator()

        # 管理后台 (建议只对管理员显示)
        if (user_manager.is_logged_in and user_manager.session_role == 'admin' and self.adminInterface) or self.test_mode:
            self.addSubInterface(self.adminInterface, FIF.EDIT, '数据管理', NavigationItemPosition.SCROLL)

        # 设置
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """初始化窗口属性"""
        self.resize(1000, 700)  # 稍微宽一点以容纳详情
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle('电影资料库管理系统 (MDMS)')

    def handle_logout(self):
        """处理退出登录"""
        # 发射退出登录信号，由应用程序控制器处理窗口切换
        self.logoutRequested.emit()


if __name__ == '__main__':
    # 开启高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    w = MainWindow(test_mode=True)
    w.show()
    app.exec()
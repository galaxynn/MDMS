import sys
import traceback

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import NavigationItemPosition, FluentWindow, FluentIcon as FIF

from mdms.common.user_manager import user_manager
from mdms.common.review_manager import review_manager
from mdms.database.models import Movie
from mdms.database.session import SessionLocal
from mdms.views.admin.admin_interface import AdminInterface
from mdms.views.movie.movie_interface import MovieInterface
from mdms.views.my_review.my_review_interface import MyReviewInterface
from mdms.views.people.people_interface import PeopleInterface
from mdms.views.setting.setting_interface import SettingInterface
from mdms.views.top100.top100_interface import Top100Interface


class MainWindow(FluentWindow):
    """
    系统主界面容器
    继承自 FluentWindow，提供侧边导航栏架构。
    负责各功能子界面的生命周期管理、导航路由初始化以及系统启动时的数据同步。
    """

    # 定义退出登录信号，用于通知应用程序控制器（Controller）切换回登录界面
    logoutRequested = Signal()

    def __init__(self, test_mode=False):
        super().__init__()

        # 测试模式标志：若为 True，则忽略权限直接实例化管理员后台界面
        self.test_mode = test_mode

        # 系统冷启动数据自检：重新计算并更新所有电影的平均分与评分人数，确保数据一致性
        self.sync_movie_stats()

        # 实例化各功能模块接口
        # 1. 电影库：核心画廊浏览
        self.MovieInterface = MovieInterface('Movie Library', self)

        # 2. 排行榜：展示评分最高的前 100 部电影
        self.top100Interface = Top100Interface('TOP 100 Movies', self)

        # 3. 演职人员库：导演、演员数据的搜索与查看
        self.peopleInterface = PeopleInterface('People Library', self)

        # 4. 个人中心：展示当前登录用户的影评记录
        self.myReviewInterface = MyReviewInterface('My Reviews', self)

        # 5. 管理员后台：仅在管理员登录或测试模式下实例化
        self.adminInterface = None
        if (user_manager.is_logged_in and user_manager.session_role == 'admin') or self.test_mode:
            self.adminInterface = AdminInterface('Admin Data Management', self)

        # 6. 系统设置：包含应用偏好设置及退出登录逻辑
        self.settingInterface = SettingInterface('Settings', self)
        # 监听设置界面的登出请求并转发给控制器
        self.settingInterface.logoutRequested.connect(self.handle_logout)

        # 初始化侧边导航栏路由
        self.initNavigation()
        # 配置主窗口几何属性与全局样式
        self.initWindow()

    def initNavigation(self):
        """
        初始化导航菜单架构
        按照业务逻辑排列菜单顺序，并配置图标与滚动位置。
        """
        # 核心业务区：电影浏览与排行
        self.addSubInterface(self.MovieInterface, FIF.HOME, '电影库')
        self.addSubInterface(self.top100Interface, FIF.HEART, 'TOP100 电影排行榜')

        # 资料检索区：人员数据
        self.addSubInterface(self.peopleInterface, FIF.PEOPLE, '演职人员')

        # 用户交互区：影评记录
        self.addSubInterface(self.myReviewInterface, FIF.CHAT, '我的影评')

        # 添加菜单分隔线，区分业务功能与系统管理功能
        self.navigationInterface.addSeparator()

        # 管理后台：具有权限约束的动态导航项
        if (
                user_manager.is_logged_in and user_manager.session_role == 'admin' and self.adminInterface) or self.test_mode:
            self.addSubInterface(
                self.adminInterface,
                FIF.EDIT,
                '数据管理',
                NavigationItemPosition.SCROLL
            )

        # 固定在底部的系统项
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            '设置',
            NavigationItemPosition.BOTTOM
        )

    def initWindow(self):
        """
        配置窗口初始属性
        """
        self.resize(1000, 700)
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle('电影资料库管理系统 (MDMS)')

    def handle_logout(self):
        """
        处理登出逻辑
        发射退出信号，由外部 Controller 负责执行具体的界面销毁与跳转。
        """
        self.logoutRequested.emit()

    def sync_movie_stats(self):
        """
        启动时数据同步逻辑
        遍历数据库中所有电影记录，调用 ReviewManager 重新计算每部电影的平均分。
        此操作解决了直接修改评论数据可能导致的平均分统计滞后问题。
        """
        session = SessionLocal()
        try:
            # 性能优化：仅查询主键 movie_id，减少内存占用
            all_movies = session.query(Movie.movie_id).all()

            if not all_movies:
                return

            print(f"数据初始化：正在同步 {len(all_movies)} 部电影的评分统计数据...")

            # 遍历所有电影 ID 执行状态更新
            for (mid,) in all_movies:
                # 核心逻辑：查询该 ID 下的所有评论并重写 Movie 表中的冗余统计字段
                review_manager.update_movie_status(session, mid)

            # 统一提交事务，确保操作原子性
            session.commit()
            print("数据初始化：评分统计数据同步完成。")

        except Exception as e:
            print(f"同步失败：启动自检过程中发生错误: {e}")
            session.rollback()
        finally:
            session.close()


if __name__ == '__main__':
    # 启用 Fluent 设计规范建议的高分屏缩放策略
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    # 启动测试模式，方便在无需登录的情况下调试 UI
    w = MainWindow(test_mode=True)
    w.show()

    app.exec()
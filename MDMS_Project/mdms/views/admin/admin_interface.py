from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QStackedWidget
from qfluentwidgets import Pivot

from mdms.views.admin.movie_management import MovieManagementWidget
from mdms.views.admin.person_management import PersonManagementWidget
from mdms.views.admin.user_management import UserManagementWidget


class AdminInterface(QFrame):
    """管理员界面"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.pivot = None
        self.stacked_widget = None
        # 设置 objectName，这是修复错误的关键
        self.setObjectName(text.replace(' ', '-'))
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 创建标签页
        self.pivot = Pivot(self)
        self.stacked_widget = QStackedWidget(self)

        # 创建三个管理页面
        self.movie_management = MovieManagementWidget()
        self.person_management = PersonManagementWidget()
        self.user_management = UserManagementWidget()

        # 添加页面到堆叠窗口
        self.stacked_widget.addWidget(self.movie_management)
        self.stacked_widget.addWidget(self.person_management)
        self.stacked_widget.addWidget(self.user_management)

        # 添加标签页
        self.pivot.addItem(
            routeKey='movie_management',
            text='电影管理',
            onClick=lambda: self.stacked_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey='person_management',
            text='人员管理',
            onClick=lambda: self.stacked_widget.setCurrentIndex(1)
        )
        self.pivot.addItem(
            routeKey='user_management',
            text='用户管理',
            onClick=lambda: self.stacked_widget.setCurrentIndex(2)
        )

        # 设置布局
        layout.addWidget(self.pivot)
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # 连接信号
        self.stacked_widget.currentChanged.connect(self.on_current_index_changed)
        self.stacked_widget.setCurrentIndex(0)
        self.pivot.setCurrentItem('movie_management')

    def on_current_index_changed(self, index):
        """当前页面改变时的处理"""
        self.pivot.setCurrentItem(list(self.pivot.items.keys())[index])
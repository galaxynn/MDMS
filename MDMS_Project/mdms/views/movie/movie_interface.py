from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QStackedWidget)
from mdms.views.movie.movie_gallery_widget import MovieGalleryWidget
from mdms.views.movie.movie_detail_widget import MovieDetailWidget


class MovieInterface(QFrame):
    """
    电影模块容器组件
    该组件充当“路由器”角色，管理电影列表（Gallery）与电影详情（Detail）两个子页面的堆叠与切换。
    通过信号与槽机制实现子页面间的数据传递，而不直接暴露内部复杂的布局逻辑。
    """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # 必须设置 ObjectName，以便 QFluentWidgets 的样式系统和导航系统正常识别
        self.setObjectName(text.replace(' ', '-'))

        # 初始化主布局：使用垂直布局包裹堆叠小部件（QStackedWidget）
        self.mainLayout = QVBoxLayout(self)
        # 边距设为 0，确保子页面内容能够完整填充整个父容器
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        # 实例化堆叠容器，它是实现多页面单窗口显示的布局核心
        self.stackedWidget = QStackedWidget(self)
        self.mainLayout.addWidget(self.stackedWidget)

        # 初始化具体的业务子页面
        # 1. 列表页：展示电影海报墙、分页及搜索
        self.galleryInterface = MovieGalleryWidget("电影展示", self)
        # 2. 详情页：展示单部电影的深度信息、演职员及影评
        self.detailInterface = MovieDetailWidget(self)

        # 将子页面注入堆叠容器
        # Index 0: 默认显示的画廊页面
        self.stackedWidget.addWidget(self.galleryInterface)
        # Index 1: 详情页面
        self.stackedWidget.addWidget(self.detailInterface)

        # 核心交互逻辑连接：通过自定义信号实现页面跳转

        #  在画廊中选中某部电影 -> 触发详情展示
        # 信号 requestOpenDetail(str) 携带选中的电影 UUID
        self.galleryInterface.requestOpenDetail.connect(self.show_detail)

        # 在详情页点击“返回”按钮 -> 切换回画廊
        # 信号 backClicked 无需携带参数
        self.detailInterface.backClicked.connect(self.show_gallery)

    @Slot(str)
    def show_detail(self, movie_id):
        """
        跳转至详情页的槽函数

        参数:
            movie_id (str): 需要查询并展示的电影唯一标识符

        逻辑流:
            1. 调用详情组件的 set_movie 方法，触发数据库查询并刷新 UI 内容。
            2. 将堆叠布局的当前索引切换至详情页 (Index 1)。
        """
        print(f"MovieInterface: 正在切换至详情视图，电影 ID: {movie_id}")

        # 确保在界面切换前，数据已经开始加载
        self.detailInterface.set_movie(movie_id)

        # 执行界面切换
        self.stackedWidget.setCurrentIndex(1)

    @Slot()
    def show_gallery(self):
        """
        回退至列表页的槽函数

        逻辑流:
            1. 直接将堆叠布局切换回画廊页面 (Index 0)。
            2. 画廊页面保持之前的搜索和分页状态，无需重新加载数据（除非需要强制刷新）。
        """
        self.stackedWidget.setCurrentIndex(0)
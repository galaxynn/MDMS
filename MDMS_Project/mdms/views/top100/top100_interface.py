from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFrame, QVBoxLayout, QStackedWidget

from mdms.views.top100.top100_gallery_widget import Top100GalleryWidget
from mdms.views.movie.movie_detail_widget import MovieDetailWidget


class Top100Interface(QFrame):
    """
    TOP100界面 - 管理 'TOP100列表页' 和 '电影详情页' 的切换
    """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 1. 堆叠布局
        self.stackLayout = QVBoxLayout(self)
        self.stackLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self)
        self.stackLayout.addWidget(self.stackedWidget)

        # 2. 初始化子界面
        self.galleryInterface = Top100GalleryWidget("TOP 100 电影", self)
        self.detailInterface = MovieDetailWidget(self)  # 复用电影详情组件

        # 3. 添加到堆叠窗口
        self.stackedWidget.addWidget(self.galleryInterface)  # Index 0
        self.stackedWidget.addWidget(self.detailInterface)   # Index 1

        # 4. 信号连接
        # 列表页点击电影 -> 跳转详情
        self.galleryInterface.requestOpenDetail.connect(self.show_detail)

        # 详情页点击返回 -> 回到列表
        self.detailInterface.backClicked.connect(self.show_gallery)

    @Slot(str)
    def show_detail(self, movie_id):
        """切换到详情页"""
        print(f"TOP100跳转详情页 ID: {movie_id}")
        self.detailInterface.set_movie(movie_id)
        self.stackedWidget.setCurrentIndex(1)

    @Slot()
    def show_gallery(self):
        """切换回列表页"""
        self.stackedWidget.setCurrentIndex(0)
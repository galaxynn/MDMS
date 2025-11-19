from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QStackedWidget)

# 引入两个业务Widget组件
from movie_gallery_widget import MovieGalleryWidget
from movie_detail_widget import MovieDetailWidget

class MovieInterface(QFrame):
    """
    [核心修改] Home 容器组件
    它不直接显示内容，而是管理 '列表页' 和 '详情页' 的切换
    """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # 必备: 设置ObjectName
        self.setObjectName(text.replace(' ', '-'))

        # 1. 使用堆叠布局
        self.stackLayout = QVBoxLayout(self)
        self.stackLayout.setContentsMargins(0, 0, 0, 0)  # 去掉边距，让子界面填满
        self.stackedWidget = QStackedWidget(self)
        self.stackLayout.addWidget(self.stackedWidget)

        # 2. 初始化两个子界面
        # 注意：这里传入 self 作为 parent
        self.galleryInterface = MovieGalleryWidget("电影库", self)
        self.detailInterface = MovieDetailWidget(self)

        # 3. 添加到堆叠窗口
        self.stackedWidget.addWidget(self.galleryInterface)  # Index 0
        self.stackedWidget.addWidget(self.detailInterface)  # Index 1

        # 4. 信号连接 (逻辑核心)

        # 当列表页点击电影 -> 切换到详情页
        # 假设 gallery 发出的信号叫 requestOpenDetail，携带 movie_id
        self.galleryInterface.requestOpenDetail.connect(self.show_detail)

        # 当详情页点击返回 -> 切换回列表页
        # 假设 detail 发出的信号叫 backClicked
        self.detailInterface.backClicked.connect(self.show_gallery)

    @Slot(int)
    def show_detail(self, movie_id):
        """ 切换到详情页 """
        print(f"跳转详情页 ID: {movie_id}")
        # 调用详情页的数据加载方法
        self.detailInterface.set_movie(movie_id)
        # 切换 Stack 下标
        self.stackedWidget.setCurrentIndex(1)

    @Slot()
    def show_gallery(self):
        """ 切换回列表页 """
        self.stackedWidget.setCurrentIndex(0)
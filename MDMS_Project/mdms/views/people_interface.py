from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QStackedWidget)

# 引入业务组件
from mdms.views.people_gallery_widget import PeopleGalleryWidget
from mdms.views.people_detail_widget import PeopleDetailWidget


class PeopleInterface(QFrame):
    """
    [演职人员] 模块核心容器
    管理 '人员列表页' 和 '人员详情页' 的切换
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
        self.galleryInterface = PeopleGalleryWidget("演职人员库", self)
        self.detailInterface = PeopleDetailWidget(self)

        # 3. 添加到堆叠窗口
        self.stackedWidget.addWidget(self.galleryInterface)  # Index 0
        self.stackedWidget.addWidget(self.detailInterface)  # Index 1

        # 4. 信号连接
        # 列表页点击某人 -> 跳转详情
        self.galleryInterface.requestOpenDetail.connect(self.show_detail)

        # 详情页点击返回 -> 回到列表
        self.detailInterface.backClicked.connect(self.show_gallery)

    @Slot(str)
    def show_detail(self, person_id: str):
        """ 切换到详情页并加载数据 """
        print(f"跳转人员详情页 ID: {person_id}")
        self.detailInterface.set_person(person_id)
        self.stackedWidget.setCurrentIndex(1)

    @Slot()
    def show_gallery(self):
        """ 切换回列表页 """
        self.stackedWidget.setCurrentIndex(0)
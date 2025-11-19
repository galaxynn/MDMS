# mdms/views/main_window.py
import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QApplication,
                               QVBoxLayout, QStackedWidget)  # 引入 StackedWidget
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SubtitleLabel,
                            setFont, PushButton, FluentIcon as FIF)

# 引入两个业务组件
from movie_gallery_widget import MovieGalleryWidget
from movie_detail_widget import MovieDetailWidget


class Widget(QFrame):
    """ 测试用的占位组件 """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)
        self.button = PushButton("Test Button", self)
        self.hBoxLayout.addWidget(self.button)
        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class HomeInterface(QFrame):
    """
    [核心修改] Home 容器组件
    它不直接显示内容，而是管理 '列表页' 和 '详情页' 的切换
    """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
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


class MainWindow(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 1. 创建子界面

        # [修改] 这里不再直接实例化 MovieGalleryWidget，而是实例化我们的容器 HomeInterface
        self.homeInterface = HomeInterface('Home Interface', self)

        # 其他子界面保持不变
        self.musicInterface = Widget('Music Interface', self)
        self.videoInterface = Widget('Video Interface', self)
        self.settingInterface = Widget('Setting Interface', self)
        self.albumInterface = Widget('Album Interface', self)
        self.albumInterface1 = Widget('Album Interface 1', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        # 添加 Home 界面
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')

        self.addSubInterface(self.musicInterface, FIF.MUSIC, 'Music library')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.albumInterface, FIF.ALBUM, 'Albums', NavigationItemPosition.SCROLL)
        self.addSubInterface(self.albumInterface1, FIF.ALBUM, 'Album 1', parent=self.albumInterface)

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(900, 700)
        # 确保资源文件已编译或路径正确
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('电影资料库管理系统')


if __name__ == '__main__':
    # 开启高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QApplication, QWidget,
                               QHBoxLayout)
from qfluentwidgets import (ElevatedCardWidget, ImageLabel, CaptionLabel,
                            SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            SearchLineEdit)
from mdms.database.session import SessionLocal
from mdms.database.models import Movie



class MovieCard(ElevatedCardWidget):
    """
    自定义电影卡片组件
    """
    # 修改信号：发送 str 类型的 ID (因为数据库定义 movie_id 为 String(36)/UUID)
    movieClicked = Signal(str)

    def __init__(self, movie_id: str, iconPath: str, name: str, parent=None):
        super().__init__(parent)
        self.movie_id = movie_id  # 存储数据库 UUID
        self.movieName = name  # 用于搜索

        # 处理图片路径：如果是 None 或者空字符串，使用默认图标
        if not iconPath:
            iconPath = ":/qfluentwidgets/images/logo.png"

        # 1. 封面图片
        self.iconWidget = ImageLabel(iconPath, self)
        self.iconWidget.scaledToHeight(120)
        self.iconWidget.setBorderRadius(8, 8, 8, 8)

        # 2. 电影名称
        self.label = CaptionLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)
        # 如果电影名太长，可以截断或允许换行，这里保持原样

        # 3. 布局管理
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)

        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

        self.setFixedSize(160, 200)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        # 触发点击信号，发送 UUID
        self.movieClicked.emit(self.movie_id)


class MovieGalleryWidget(QFrame):
    """
    电影库主界面
    """
    # 新增信号：请求打开详情页，传递 movie_id (str)
    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 存储卡片列表
        self.cards = []

        # 1. 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # 2. 头部布局
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)

        # 搜索框
        self.searchEdit = SearchLineEdit(self)
        self.searchEdit.setPlaceholderText("搜索电影...")
        self.searchEdit.setFixedWidth(240)
        self.searchEdit.textChanged.connect(self.search_movies)
        self.headerLayout.addWidget(self.searchEdit)

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(10)

        # 3. 滚动区域
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setSmoothMode(SmoothMode.NO_SMOOTH, Qt.Orientation.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")

        # 4. 内容容器
        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background: transparent;")

        # 5. FlowLayout
        self.flowLayout = FlowLayout(self.scrollWidget)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setVerticalSpacing(20)
        self.flowLayout.setHorizontalSpacing(20)

        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

        # 6. 从数据库加载数据
        self.load_movies_from_db()

    def load_movies_from_db(self):
        """
        使用 SQLAlchemy 从数据库读取电影数据
        """
        if SessionLocal is None:
            print("数据库模块未导入，无法加载数据。")
            return

        session = SessionLocal()
        try:
            # 查询所有电影
            # 如果需要特定排序，可以使用 .order_by(Movie.release_date.desc())
            movies = session.query(Movie).all()

            for movie in movies:
                # 这里的字段名需要对应 models.py 中的 Movie 类
                # movie_id, poster_url, title
                card = MovieCard(
                    movie_id=movie.movie_id,
                    iconPath=movie.poster_url,
                    name=movie.title,
                    parent=self.scrollWidget
                )

                # 连接卡片内部信号 -> 界面跳转信号
                card.movieClicked.connect(self.on_card_clicked)

                self.flowLayout.addWidget(card)
                self.cards.append(card)

        except Exception as e:
            print(f"加载电影数据出错: {e}")
        finally:
            session.close()

    def on_card_clicked(self, movie_id: str):
        """中转函数：打印日志并向上发送信号"""
        print(f"点击了电影 ID: {movie_id}")
        self.requestOpenDetail.emit(movie_id)

    def search_movies(self, text: str):
        """
        搜索逻辑：移除 -> 筛选 -> 重新添加
        """
        text = text.strip().lower()

        # 1. 移除当前布局中的所有控件
        for i in range(self.flowLayout.count() - 1, -1, -1):
            item = self.flowLayout.itemAt(i)
            if item and item.widget():
                self.flowLayout.removeWidget(item.widget())
                item.widget().hide()

        # 2. 筛选并重新添加
        for card in self.cards:
            movie_name = card.movieName.lower()
            if not text or text in movie_name:
                card.show()
                self.flowLayout.addWidget(card)


if __name__ == '__main__':
    # 简单的测试入口
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    # 注意：如果是单独运行此文件测试，需确保数据库配置文件路径正确
    w = MovieGalleryWidget("电影资料库")
    w.resize(900, 700)
    w.show()

    app.exec()
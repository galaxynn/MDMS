import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QApplication, QWidget, QHBoxLayout
from qfluentwidgets import SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode, BodyLabel, CaptionLabel
from sqlalchemy import and_

from mdms.database.session import SessionLocal
from mdms.database.models import Movie


class Top100MovieCard(QFrame):
    """
    自定义TOP100电影卡片组件 - 专门为TOP100页面优化显示
    """
    movieClicked = Signal(str)

    def __init__(self, movie_id: str, iconPath: str, name: str, rank: int, rating: float, parent=None):
        super().__init__(parent)
        self.movie_id = movie_id
        self.setFixedSize(160, 220)  # 稍微增加高度以容纳更多内容
        self.setCursor(Qt.PointingHandCursor)

        # 设置样式
        self.setObjectName("movieCard")
        self.setStyleSheet("""
            #movieCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            #movieCard:hover {
                background-color: #f5f5f5;
            }
        """)

        if not iconPath:
            iconPath = ":/qfluentwidgets/images/logo.png"

        # 1. 排名标签
        from qfluentwidgets import CaptionLabel
        self.rankLabel = CaptionLabel(f"#{rank}", self)
        self.rankLabel.setAlignment(Qt.AlignCenter)
        self.rankLabel.setStyleSheet("""
            background-color: #ff6b00;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            margin: 5px;
        """)

        # 2. 封面图片
        from qfluentwidgets import ImageLabel
        self.iconWidget = ImageLabel(iconPath, self)
        self.iconWidget.scaledToHeight(120)
        self.iconWidget.setBorderRadius(8, 8, 8, 8)

        # 3. 电影名称
        self.titleLabel = CaptionLabel(name, self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setMaximumHeight(40)
        self.titleLabel.setToolTip(name)

        # 4. 评分标签
        self.ratingLabel = CaptionLabel(f"⭐ {rating:.1f}", self)
        self.ratingLabel.setAlignment(Qt.AlignCenter)
        self.ratingLabel.setStyleSheet("color: #ff6b00; font-weight: bold;")

        # 5. 布局管理
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(8, 8, 8, 8)
        self.vBoxLayout.setSpacing(5)

        self.vBoxLayout.addWidget(self.rankLabel, 0, Qt.AlignRight)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.ratingLabel, 0, Qt.AlignCenter)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.movieClicked.emit(self.movie_id)


class Top100GalleryWidget(QFrame):
    """
    TOP100画廊组件 - 专门用于显示TOP100电影
    """

    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 状态变量
        self.cards = []

        # 初始化UI
        self.init_ui(text)

        # 加载TOP100数据
        self.load_top100_data()

    def init_ui(self, text):
        """初始化界面"""
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # === 头部 ===
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)

        # === 描述信息 ===
        self.descriptionLabel = BodyLabel("根据电影评分排序的前100部高评分电影", self)
        self.descriptionLabel.setStyleSheet("color: #666; margin-bottom: 10px;")

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addWidget(self.descriptionLabel)
        self.mainLayout.addSpacing(10)

        # === 滚动区域 ===
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setSmoothMode(SmoothMode.NO_SMOOTH, Qt.Orientation.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")

        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background: transparent;")

        self.flowLayout = FlowLayout(self.scrollWidget)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setVerticalSpacing(20)
        self.flowLayout.setHorizontalSpacing(20)

        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def load_top100_data(self):
        """加载TOP100电影数据"""
        if SessionLocal is None:
            print("Warning: Database SessionLocal is None.")
            return

        session = SessionLocal()
        try:
            # 查询TOP100电影：只选择有评分且评分大于0的电影，按平均评分降序排序
            movies = session.query(Movie).filter(
                and_(
                    Movie.average_rating > 0,
                    Movie.rating_count > 0  # 确保至少有一个评分
                )
            ).order_by(
                Movie.average_rating.desc()  # 只按评分排序
            ).limit(100).all()

            # 渲染界面
            self.update_gallery(movies)

        except Exception as e:
            print(f"加载TOP100电影失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

    def update_gallery(self, movies):
        """清除旧卡片并显示新卡片"""
        # 1. 清空 FlowLayout
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cards.clear()

        # 2. 创建新卡片
        if not movies:
            no_data_label = CaptionLabel("暂无评分数据", self.scrollWidget)
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 16px; color: #999; padding: 50px;")
            self.flowLayout.addWidget(no_data_label)
            return

        for index, movie in enumerate(movies):
            # 创建电影卡片，使用专门的TOP100卡片组件
            card = Top100MovieCard(
                movie_id=movie.movie_id,
                iconPath=movie.poster_url,
                name=movie.title,
                rank=index + 1,
                rating=float(movie.average_rating),
                parent=self.scrollWidget
            )

            card.movieClicked.connect(self.on_card_clicked)
            self.flowLayout.addWidget(card)
            self.cards.append(card)

    def on_card_clicked(self, movie_id: str):
        """处理卡片点击事件"""
        print(f"TOP100点击了电影 ID: {movie_id}")
        self.requestOpenDetail.emit(movie_id)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    w = Top100GalleryWidget("TOP 100 电影")
    w.resize(960, 700)
    w.show()

    app.exec()
import sys
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QFrame, QVBoxLayout, QApplication, QWidget, QHBoxLayout
from qfluentwidgets import (SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            BodyLabel, CaptionLabel, TransparentToolButton, FluentIcon)
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
        self.setFixedSize(160, 240)
        self.setCursor(Qt.PointingHandCursor)

        # 设置样式 (保持不变)
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

        # 1. 排名标签 (保持不变)
        from qfluentwidgets import CaptionLabel
        self.rankLabel = CaptionLabel(f"#{rank}", self)
        self.rankLabel.setAlignment(Qt.AlignCenter)
        self.rankLabel.setStyleSheet("""
            background-color: #ff6b00;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-weight: bold;
            margin: 5px 5px 0px 5px; /* 稍微调整边距 */
        """)

        # 2. 封面图片
        from qfluentwidgets import ImageLabel
        self.iconWidget = ImageLabel(iconPath, self)
        # 明确固定图片大小
        # 卡片宽度160 - 左右边距各8 = 144宽度。高度固定为120。
        self.iconWidget.setFixedSize(144, 120)
        # 确保图片内容填充在这个固定区域内
        self.iconWidget.setScaledContents(True)
        self.iconWidget.setBorderRadius(8, 8, 8, 8)

        # 3. 电影名称
        self.titleLabel = CaptionLabel(name, self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        # 允许换行
        self.titleLabel.setWordWrap(True)
        # 移除硬性的最大高度限制，让布局决定高度
        # self.titleLabel.setMaximumHeight(40)
        self.titleLabel.setToolTip(name)
        # 可以设置一个最小高度确保至少显示一行
        self.titleLabel.setMinimumHeight(20)

        # 4. 评分标签 (保持不变)
        self.ratingLabel = CaptionLabel(f"⭐ {rating:.1f}", self)
        self.ratingLabel.setAlignment(Qt.AlignCenter)
        self.ratingLabel.setStyleSheet("color: #ff6b00; font-weight: bold; margin-bottom: 5px;")

        # 5. 布局管理
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(8, 8, 8, 8)
        # 稍微减小间距
        self.vBoxLayout.setSpacing(4)

        # 设置拉伸因子
        # 第二个参数是拉伸因子。设为 0 表示固定高度，不参与拉伸。
        # 将 titleLabel 的拉伸因子设为 1，表示它占据剩余所有空间。
        self.vBoxLayout.addWidget(self.rankLabel, 0, Qt.AlignRight)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.titleLabel, 1, Qt.AlignCenter) # stretch=1
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

        # 标题
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)
        self.headerLayout.addWidget(self.titleLabel)

        # 弹簧 (将刷新按钮推到最右侧)
        self.headerLayout.addStretch(1)

        # 增刷新按钮
        # 使用透明工具按钮，图标为 SYNC (刷新/同步图标)
        self.refreshBtn = TransparentToolButton(FluentIcon.SYNC, self)
        self.refreshBtn.setToolTip("刷新榜单")
        self.refreshBtn.setFixedSize(32, 32)  # 设置合适的大小
        self.refreshBtn.setIconSize(QSize(16, 16))  # 设置图标大小

        # 3. 连接信号槽：点击时调用 load_top100_data
        self.refreshBtn.clicked.connect(self.on_refresh_clicked)

        self.headerLayout.addWidget(self.refreshBtn)

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

    def on_refresh_clicked(self):
        """处理刷新点击，可以添加一些额外的UI反馈逻辑"""
        print("正在刷新TOP100榜单...")
        # 这里你可以选择先清空列表，或者直接重新加载
        # self.cards.clear()
        # 重新加载数据
        self.load_top100_data()

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

        # 1. 清空 FlowLayout (修复版)
        # qfluentwidgets 的 FlowLayout.takeAt() 有时直接返回 Widget，而不是 QLayoutItem
        if self.flowLayout:
            # 如果组件支持 removeAllWidgets (新版特性)，优先使用
            if hasattr(self.flowLayout, 'removeAllWidgets'):
                self.flowLayout.removeAllWidgets()
            else:
                # 兼容性手动清空
                while self.flowLayout.count():
                    item = self.flowLayout.takeAt(0)
                    if item is None:
                        break

                    # 关键修改：判断取出来的是 Widget 本身还是 LayoutItem
                    if isinstance(item, QWidget):
                        # 如果直接是 Widget (Top100MovieCard)
                        item.deleteLater()
                    elif hasattr(item, 'widget'):
                        # 如果是 QLayoutItem 包装器
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
            # 创建电影卡片
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
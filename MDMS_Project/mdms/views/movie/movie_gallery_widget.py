import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QApplication, QWidget,
                               QHBoxLayout)
from qfluentwidgets import (ElevatedCardWidget, ImageLabel, CaptionLabel,
                            SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            SearchLineEdit)

# 导入数据库相关 (请确保路径正确)
from mdms.database.session import SessionLocal
from mdms.database.models import Movie

# 导入刚才创建的分页组件
from mdms.common.fluent_paginator import FluentPaginator


class MovieCard(ElevatedCardWidget):
    """
    自定义电影卡片组件
    """
    movieClicked = Signal(str)

    def __init__(self, movie_id: str, iconPath: str, name: str, parent=None):
        super().__init__(parent)
        self.movie_id = movie_id
        self.movieName = name

        if not iconPath:
            iconPath = ":/qfluentwidgets/images/logo.png"

        # 1. 封面图片
        self.iconWidget = ImageLabel(iconPath, self)
        self.iconWidget.scaledToHeight(120)
        self.iconWidget.setBorderRadius(8, 8, 8, 8)

        # 2. 电影名称
        self.label = CaptionLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)
        # 限制文本长度，防止破坏布局
        font_metrics = self.label.fontMetrics()
        elided_text = font_metrics.elidedText(name, Qt.ElideRight, 140)
        self.label.setText(elided_text)
        self.label.setToolTip(name)  # 鼠标悬停显示全名

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
        self.movieClicked.emit(self.movie_id)


class MovieGalleryWidget(QFrame):
    """
    电影库主界面 (带分页功能)
    """
    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 状态变量
        self.current_search_text = ""
        self.cards = []  # 仅存储当前页的卡片对象

        # 1. 初始化UI
        self.init_ui(text)

        # 2. 初始加载第一页数据
        self.load_data(page=1)

    def init_ui(self, text):
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # === 头部 ===
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)

        # === 搜索框 ===
        self.searchEdit = SearchLineEdit(self)
        self.searchEdit.setPlaceholderText("搜索电影名称...")
        self.searchEdit.setFixedWidth(240)
        # 绑定搜索事件：按下回车或点击搜索图标触发
        self.searchEdit.searchSignal.connect(self.on_search_triggered)
        self.searchEdit.returnPressed.connect(self.on_search_triggered)
        # 可选：清空搜索框时自动重置
        self.searchEdit.textChanged.connect(self.on_search_text_changed)

        self.headerLayout.addWidget(self.searchEdit)
        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(10)

        # === 滚动区域 ===
        self.scrollArea = ScrollArea(self)
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

        # === 底部：集成自定义分页器 ===
        self.paginator = FluentPaginator(self)
        self.paginator.set_page_size(18)  # 设置每页显示18个
        self.paginator.pageChanged.connect(self.load_data)  # 连接翻页信号

        self.mainLayout.addWidget(self.paginator, 0, Qt.AlignBottom)

    def load_data(self, page: int):
        """
        核心数据加载逻辑：
        1. 根据搜索词过滤
        2. 计算总数并更新分页器
        3. 使用 Limit/Offset 获取当前页数据
        4. 渲染卡片
        """
        if SessionLocal is None:
            print("Warning: Database SessionLocal is None.")
            return

        session = SessionLocal()
        try:
            # 构建基础查询
            query = session.query(Movie)

            # 1. 应用搜索过滤
            if self.current_search_text:
                # 假设搜索标题，使用 ilike 进行不区分大小写模糊匹配
                query = query.filter(Movie.title.ilike(f"%{self.current_search_text}%"))

            # 如果有默认排序需求 (例如按发布时间倒序)
            # query = query.order_by(Movie.release_date.desc())

            # 2. 获取总数 (这对于分页器计算总页数至关重要)
            total_items = query.count()
            self.paginator.set_total_items(total_items)

            # 这里的 set_current_page 主要是为了确保 UI 状态正确
            # 例如用户在第5页搜索导致只有1页结果，UI需要跳回第1页高亮
            self.paginator.set_current_page(page)

            # 3. 分页查询 (Limit Offset)
            limit = self.paginator.get_page_size()
            offset = (page - 1) * limit
            movies = query.offset(offset).limit(limit).all()

            # 4. 渲染界面
            self.update_gallery(movies)

            # 翻页后，自动滚回到顶部
            self.scrollArea.verticalScrollBar().setValue(0)

        except Exception as e:
            print(f"数据加载失败: {e}")
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
            # 可以添加一个 "无数据" 的提示标签
            no_data_label = CaptionLabel("未找到相关电影", self.scrollWidget)
            no_data_label.setAlignment(Qt.AlignCenter)
            self.flowLayout.addWidget(no_data_label)
            return

        for movie in movies:
            card = MovieCard(
                movie_id=movie.movie_id,
                iconPath=movie.poster_url,
                name=movie.title,
                parent=self.scrollWidget
            )
            card.movieClicked.connect(self.on_card_clicked)
            self.flowLayout.addWidget(card)
            self.cards.append(card)

    def on_search_triggered(self):
        """当用户点击搜索或按回车时触发"""
        text = self.searchEdit.text().strip()
        self.current_search_text = text
        # 搜索时，强制回到第一页
        self.load_data(page=1)

    def on_search_text_changed(self, text):
        """可选：当清空搜索框时，自动重置回全部列表"""
        if not text.strip() and self.current_search_text:
            self.current_search_text = ""
            self.load_data(page=1)

    def on_card_clicked(self, movie_id: str):
        print(f"点击了电影 ID: {movie_id}")
        self.requestOpenDetail.emit(movie_id)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    w = MovieGalleryWidget("电影资料库")
    w.resize(960, 700)
    w.show()

    app.exec()
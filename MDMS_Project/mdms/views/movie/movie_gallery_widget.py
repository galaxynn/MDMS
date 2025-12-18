import sys
import traceback

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QApplication, QWidget,
                               QHBoxLayout)
from qfluentwidgets import (ElevatedCardWidget, ImageLabel, CaptionLabel,
                            SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            SearchLineEdit, ComboBox)

from mdms.database.session import SessionLocal
from mdms.database.models import Movie, Genre
from mdms.common.fluent_paginator import FluentPaginator


class MovieCard(ElevatedCardWidget):
    """
    电影卡片展示组件
    继承自 ElevatedCardWidget 以获得悬浮阴影效果
    用于展示单部电影的海报、名称，并处理点击事件
    """
    # 当卡片被点击时发送此信号，携带 movie_id 供详情页跳转使用
    movieClicked = Signal(str)

    def __init__(self, movie_id: str, iconPath: str, name: str, parent=None):
        super().__init__(parent)
        self.movie_id = movie_id
        self.movieName = name

        # 如果数据库中海报路径为空，则使用 QFluentWidgets 默认 Logo 作为占位图
        if not iconPath:
            iconPath = ":/qfluentwidgets/images/logo.png"

        # 初始化海报图片标签，设置固定高度并开启圆角剪裁
        self.iconWidget = ImageLabel(iconPath, self)
        self.iconWidget.scaledToHeight(120)
        self.iconWidget.setBorderRadius(8, 8, 8, 8)

        # 初始化电影名称标签
        self.label = CaptionLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)

        # 文本省略处理：如果电影标题过长，自动在 140px 处截断并添加省略号，防止破坏网格布局
        font_metrics = self.label.fontMetrics()
        elided_text = font_metrics.elidedText(name, Qt.ElideRight, 140)
        self.label.setText(elided_text)
        # 鼠标悬停时显示完整电影名称
        self.label.setToolTip(name)

        # 垂直布局：海报在上，文字在下
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

        # 设置卡片固定尺寸，并根据 Fluent 设计规范将鼠标样式改为手型
        self.setFixedSize(160, 200)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, e):
        """
        重写鼠标释放事件，实现点击卡片发送电影 ID 信号
        """
        super().mouseReleaseEvent(e)
        self.movieClicked.emit(self.movie_id)


class MovieGalleryWidget(QFrame):
    """
    电影库画廊主界面
    集成搜索、类型筛选、自动换行布局以及分页查询功能
    """
    # 请求主窗口打开详情页的信号
    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # 设置对象名称以便于样式表识别，将空格替换为连字符
        self.setObjectName(text.replace(' ', '-'))

        # 维护当前筛选状态：搜索关键词和电影类型
        self.current_search_text = ""
        self.current_genre_text = "全部分类"
        self.cards = []

        # 构造 UI 界面组件
        self.init_ui(text)
        # 从数据库加载 Genre 表填充下拉框
        self.load_filter_options()
        # 执行初始数据加载，展示第一页
        self.load_data(page=1)

    def init_ui(self, text):
        """
        初始化界面布局与组件
        """
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # 头部区域：左侧标题，右侧筛选与搜索
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)

        # 类型筛选下拉框：连接 currentTextChanged 信号实现联动筛选
        self.genreComboBox = ComboBox(self)
        self.genreComboBox.setPlaceholderText("选择类型")
        self.genreComboBox.setFixedWidth(140)
        self.genreComboBox.addItem("全部分类")
        self.genreComboBox.currentTextChanged.connect(self.on_genre_changed)
        self.headerLayout.addWidget(self.genreComboBox)
        self.headerLayout.addSpacing(10)

        # 搜索输入框：支持点击搜索图标、按回车键触发搜索
        self.searchEdit = SearchLineEdit(self)
        self.searchEdit.setPlaceholderText("搜索电影名称...")
        self.searchEdit.setFixedWidth(240)
        self.searchEdit.searchSignal.connect(self.on_search_triggered)
        self.searchEdit.returnPressed.connect(self.on_search_triggered)
        self.searchEdit.textChanged.connect(self.on_search_text_changed)
        self.headerLayout.addWidget(self.searchEdit)

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(10)

        # 中间滚动区域：承载 FlowLayout 实现卡片自动换行排版
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # 禁用平滑滚动以提升大数据量下的响应速度
        self.scrollArea.setSmoothMode(SmoothMode.NO_SMOOTH, Qt.Orientation.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")

        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background: transparent;")
        # 使用 FlowLayout 实现流式布局，卡片会自动根据窗口宽度换行
        self.flowLayout = FlowLayout(self.scrollWidget)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setVerticalSpacing(20)
        self.flowLayout.setHorizontalSpacing(20)

        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

        # 底部区域：集成自定义分页器，绑定 pageChanged 信号实现分页逻辑
        self.paginator = FluentPaginator(self)
        self.paginator.set_page_size(20)
        self.paginator.pageChanged.connect(self.load_data)
        self.mainLayout.addWidget(self.paginator, 0, Qt.AlignBottom)

    def load_filter_options(self):
        """
        数据库交互：初始化时获取所有分类名称填充至 ComboBox
        """
        if SessionLocal is None:
            return
        session = SessionLocal()
        try:
            # 获取所有类型名称并按字母升序排列
            genres = session.query(Genre).order_by(Genre.name).all()
            genre_names = [g.name for g in genres]
            self.genreComboBox.addItems(genre_names)
        except Exception as e:
            print(f"加载类型数据失败: {e}")
        finally:
            session.close()

    def load_data(self, page: int):
        """
        核心业务逻辑：根据分页、类型和搜索关键词从数据库查询电影
        """
        if SessionLocal is None:
            return

        session = SessionLocal()
        try:
            # 基础查询对象
            query = session.query(Movie)

            # 多条件复合过滤：类型筛选
            if self.current_genre_text and self.current_genre_text != "全部分类":
                # 通过多对多关联关系连接 Movie 和 Genre 表
                query = query.join(Movie.genres).filter(Genre.name == self.current_genre_text)

            # 多条件复合过滤：模糊搜索标题
            if self.current_search_text:
                query = query.filter(Movie.title.ilike(f"%{self.current_search_text}%"))

            # 获取符合条件的记录总数，用于更新分页器的总页数显示
            total_items = query.count()
            self.paginator.set_total_items(total_items)
            self.paginator.set_current_page(page)

            # 计算分页偏移量执行物理分页查询
            limit = self.paginator.get_page_size()
            offset = (page - 1) * limit
            # 查询当前页数据，默认按模型定义排序（如 ID 或发布日期）
            movies = query.offset(offset).limit(limit).all()

            # 刷新画廊展示
            self.update_gallery(movies)
            # 翻页后重置滚动条位置到顶部，提升用户体验
            self.scrollArea.verticalScrollBar().setValue(0)

        except Exception as e:
            print(f"数据库分页查询失败: {e}")
            traceback.print_exc()
        finally:
            session.close()

    def update_gallery(self, movies):
        """
        UI 刷新逻辑：销毁旧卡片并根据新查询结果创建新卡片
        """
        # 遍历销毁旧卡片 widget，释放内存资源
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget() if hasattr(item, 'widget') else item
            if widget:
                widget.deleteLater()

        self.cards.clear()

        # 空数据处理：显示提示文字
        if not movies:
            no_data_label = CaptionLabel("未找到符合条件的电影", self.scrollWidget)
            no_data_label.setAlignment(Qt.AlignCenter)
            self.flowLayout.addWidget(no_data_label)
            return

        # 遍历电影列表，批量实例化卡片并添加到流式布局
        for movie in movies:
            card = MovieCard(
                movie_id=movie.movie_id,
                iconPath=movie.poster_url,
                name=movie.title,
                parent=self.scrollWidget
            )
            # 绑定卡片点击信号至本类的槽函数
            card.movieClicked.connect(self.on_card_clicked)
            self.flowLayout.addWidget(card)
            self.cards.append(card)

    def on_genre_changed(self, text):
        """
        事件槽：类型下拉框切换，重置到第 1 页并刷新
        """
        self.current_genre_text = text
        self.load_data(page=1)

    def on_search_triggered(self):
        """
        事件槽：点击搜索图标或回车键执行搜索
        """
        text = self.searchEdit.text().strip()
        self.current_search_text = text
        self.load_data(page=1)

    def on_search_text_changed(self, text):
        """
        事件槽：当用户手动删除搜索框内容时，自动重置列表到全部状态
        """
        if not text.strip() and self.current_search_text:
            self.current_search_text = ""
            self.load_data(page=1)

    def on_card_clicked(self, movie_id: str):
        """
        转发卡片点击事件：供上级主窗口捕获并跳转到详情页
        """
        print(f"触发详情跳转，电影 ID: {movie_id}")
        self.requestOpenDetail.emit(movie_id)


if __name__ == '__main__':
    # 启用高分屏支持，解决 4K 屏幕下界面模糊问题
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    w = MovieGalleryWidget("电影资料库")
    w.resize(960, 700)
    w.show()

    app.exec()
# mdms/views/movie_detail_widget.py
import sys
import os
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                               QFrame, QSizePolicy)
from qfluentwidgets import (ImageLabel, TitleLabel, BodyLabel, DisplayLabel,
                            StrongBodyLabel, PushButton, FluentIcon,
                            ScrollArea, SmoothMode)

# --- 1. 引入数据库模块 ---
# 根据项目结构引入 SessionLocal 和 Movie
try:
    from mdms.database.session import SessionLocal
    from mdms.database.models import Movie
except ImportError:
    print("ImportError: 无法导入数据库模块，请检查路径。")
    SessionLocal = None
    Movie = None


class MovieDetailWidget(QWidget):
    """
    电影详情页组件
    """
    # 信号：点击返回按钮时触发
    backClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(10)

        # --- 1. 顶部导航栏 ---
        self.headerLayout = QHBoxLayout()
        self.backBtn = PushButton("返回电影库", self, FluentIcon.RETURN)
        self.backBtn.clicked.connect(self.backClicked.emit)
        self.headerLayout.addWidget(self.backBtn)
        self.headerLayout.addStretch(1)

        self.mainLayout.addLayout(self.headerLayout)

        # --- 2. 滚动区域 (防止简介过长) ---
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")

        self.contentWidget = QWidget()
        self.contentWidget.setStyleSheet("background: transparent;")
        self.contentLayout = QHBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(10, 10, 10, 10)
        self.contentLayout.setSpacing(30)
        self.contentLayout.setAlignment(Qt.AlignTop)  # 内容顶对齐

        # --- 3. 左侧：海报 ---
        self.imageLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        # 设置海报大小，保持一般电影海报比例 (约 2:3)
        self.imageLabel.setFixedSize(240, 360)
        self.imageLabel.setBorderRadius(10, 10, 10, 10)
        self.imageLabel.setScaledContents(True)  # 确保图片填满控件

        # 将图片放入一个 VBox 以便顶对齐
        self.posterLayout = QVBoxLayout()
        self.posterLayout.addWidget(self.imageLabel)
        self.posterLayout.addStretch(1)

        self.contentLayout.addLayout(self.posterLayout)

        # --- 4. 右侧：详细信息 ---
        self.infoLayout = QVBoxLayout()
        self.infoLayout.setSpacing(10)
        self.infoLayout.setAlignment(Qt.AlignTop)

        # 4.1 电影标题
        self.titleLabel = DisplayLabel("加载中...", self)
        self.titleLabel.setWordWrap(True)
        self.infoLayout.addWidget(self.titleLabel)

        # 4.2 基础元数据 (年份 | 地区 | 时长 | 评分)
        self.metaLayout = QHBoxLayout()
        self.metaLayout.setSpacing(20)
        self.metaLayout.setAlignment(Qt.AlignLeft)

        # 创建几个用于显示的 Label
        self.yearLabel = StrongBodyLabel("年份: -", self)
        self.countryLabel = StrongBodyLabel("地区: -", self)
        self.runtimeLabel = StrongBodyLabel("时长: -", self)
        self.ratingLabel = StrongBodyLabel("评分: 0.0", self)

        # 给评分加个颜色突出一下（可选）
        self.ratingLabel.setStyleSheet("color: #009FAA; font-weight: bold;")

        self.metaLayout.addWidget(self.yearLabel)
        self.metaLayout.addWidget(self.countryLabel)
        self.metaLayout.addWidget(self.runtimeLabel)
        self.metaLayout.addWidget(self.ratingLabel)
        self.metaLayout.addStretch(1)  # 靠左对齐

        self.infoLayout.addLayout(self.metaLayout)
        self.infoLayout.addSpacing(10)  # 标题和简介稍微隔开一点

        # 4.3 简介标题
        self.synopsisTitle = StrongBodyLabel("剧情简介", self)
        self.infoLayout.addWidget(self.synopsisTitle)

        # 4.4 简介正文
        self.descLabel = BodyLabel("暂无简介", self)
        self.descLabel.setWordWrap(True)  # 关键：允许自动换行
        # 设置行高稍微大一点，利于阅读
        self.infoLayout.addWidget(self.descLabel)

        self.infoLayout.addStretch(1)  # 把内容顶上去

        # 将右侧布局加入主内容布局
        self.contentLayout.addLayout(self.infoLayout, 1)  # 1 表示右侧占用剩余空间

        # 完成滚动区域设置
        self.scrollArea.setWidget(self.contentWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def set_movie(self, movie_id: str):
        """
        核心方法：接收 UUID 字符串，查询数据库，更新界面
        """
        if not SessionLocal:
            return

        session = SessionLocal()
        try:
            # 根据 movie_id (UUID string) 查询
            movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()

            if movie:
                # 1. 设置标题
                self.titleLabel.setText(movie.title)

                # 2. 设置年份 (从 release_date 获取)
                year_str = str(movie.release_date.year) if movie.release_date else "未知"
                self.yearLabel.setText(f"年份: {year_str}")

                # 3. 设置地区
                self.countryLabel.setText(f"地区: {movie.country or '未知'}")

                # 4. 设置时长
                self.runtimeLabel.setText(f"时长: {movie.runtime_minutes or 0} 分钟")

                # 5. 设置评分
                self.ratingLabel.setText(f"评分: {movie.average_rating:.1f}")

                # 6. 设置简介 (映射 models.py 中的 synopsis 字段)
                desc = movie.synopsis if movie.synopsis else "暂无剧情简介。"
                self.descLabel.setText(desc)

                # 7. 设置海报 (映射 models.py 中的 poster_url 字段)
                # 逻辑：如果路径存在且不为空，则加载；否则加载默认图
                if movie.poster_url and os.path.exists(movie.poster_url):
                    self.imageLabel.setImage(movie.poster_url)
                else:
                    # 这里可以设置一张默认的 "暂无图片" 占位图
                    self.imageLabel.setImage(":/qfluentwidgets/images/logo.png")
            else:
                self.titleLabel.setText("未找到该电影信息")
                self.descLabel.setText("")

        except Exception as e:
            print(f"查询电影详情失败: {e}")
            self.titleLabel.setText("数据加载错误")
        finally:
            session.close()
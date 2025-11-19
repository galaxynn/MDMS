import os
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QSpacerItem, QSizePolicy)
from qfluentwidgets import (ImageLabel, DisplayLabel, StrongBodyLabel, BodyLabel,
                            PushButton, FluentIcon, ScrollArea, CardWidget,
                            IconWidget, PrimaryPushButton, MessageBoxBase,
                            Slider, TextEdit, InfoBar, InfoBarPosition, CaptionLabel)

# --- 引入项目模块 ---
from mdms.database.session import SessionLocal
from mdms.database.models import Movie, Review, MoviePerson, Genre
from mdms.common.user_manager import user_manager
from mdms.common.review_manager import review_manager


# =============================================================================
# 1. 辅助组件：添加评论弹窗
# =============================================================================
class AddReviewDialog(MessageBoxBase):
    """ 用户添加评论的弹窗 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = StrongBodyLabel("撰写影评", self)

        # 评分滑块
        self.ratingValueLabel = StrongBodyLabel("评分: 8 / 10", self)
        self.ratingSlider = Slider(Qt.Horizontal, self)
        self.ratingSlider.setRange(1, 10)
        self.ratingSlider.setValue(8)
        self.ratingSlider.valueChanged.connect(
            lambda v: self.ratingValueLabel.setText(f"评分: {v} / 10")
        )

        # 评论内容
        self.contentLabel = BodyLabel("评论内容:", self)
        self.contentEdit = TextEdit(self)
        self.contentEdit.setPlaceholderText("说说你对这部电影的看法...")
        self.contentEdit.setFixedHeight(120)

        # 添加到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.ratingValueLabel)
        self.viewLayout.addWidget(self.ratingSlider)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.contentEdit)

        self.yesButton.setText("发布")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(400)

    def get_data(self):
        return self.ratingSlider.value(), self.contentEdit.toPlainText().strip()


# =============================================================================
# 2. 辅助组件：单条评论卡片
# =============================================================================
class ReviewCard(CardWidget):
    """ 展示单条评论的卡片 """

    def __init__(self, username, rating, content, time_str, parent=None):
        super().__init__(parent)
        self.setContentsMargins(16, 16, 16, 16)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 第一行：用户名 + 评分 + 时间
        top_layout = QHBoxLayout()

        user_icon = IconWidget(FluentIcon.PEOPLE, self)
        user_icon.setFixedSize(16, 16)
        user_label = BodyLabel(username, self)

        rating_icon = IconWidget(FluentIcon.HEART, self)  # 用心形或星形代表评分
        rating_icon.setFixedSize(16, 16)
        rating_label = StrongBodyLabel(f"{rating} 分", self)
        rating_label.setStyleSheet("color: #009FAA;")  # 高亮评分

        time_label = CaptionLabel(time_str, self)
        time_label.setTextColor("#808080", "#808080")  # 灰色

        top_layout.addWidget(user_icon)
        top_layout.addWidget(user_label)
        top_layout.addSpacing(15)
        top_layout.addWidget(rating_icon)
        top_layout.addWidget(rating_label)
        top_layout.addStretch(1)
        top_layout.addWidget(time_label)

        # 第二行：内容
        content_label = BodyLabel(content, self)
        content_label.setWordWrap(True)

        layout.addLayout(top_layout)
        layout.addWidget(content_label)


# =============================================================================
# 3. 核心组件：电影详情页
# =============================================================================
class MovieDetailWidget(QWidget):
    backClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_movie_id = None  # 记录当前电影ID

        # --- 主布局 (包含顶部返回栏 + 滚动区域) ---
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # 1. 顶部导航栏
        self.headerBar = QFrame(self)
        self.headerBar.setFixedHeight(50)
        self.headerLayout = QHBoxLayout(self.headerBar)
        self.headerLayout.setContentsMargins(20, 0, 20, 0)

        self.backBtn = PushButton("返回", self, FluentIcon.RETURN)
        self.backBtn.clicked.connect(self.backClicked.emit)
        self.headerLayout.addWidget(self.backBtn)
        self.headerLayout.addStretch(1)

        self.mainLayout.addWidget(self.headerBar)

        # 2. 滚动区域 (整个页面内容都在滚动区内)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")

        # 滚动区的内容容器
        self.contentWidget = QWidget()
        self.contentWidget.setStyleSheet("background: transparent;")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(30, 20, 30, 40)
        self.contentLayout.setSpacing(30)

        # --- A. 电影信息区 (水平布局：左海报，右详情) ---
        self.topInfoContainer = QWidget()
        self.topInfoLayout = QHBoxLayout(self.topInfoContainer)
        self.topInfoLayout.setContentsMargins(0, 0, 0, 0)
        self.topInfoLayout.setSpacing(30)
        self.topInfoLayout.setAlignment(Qt.AlignTop)

        # A.1 左侧海报
        self.posterLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        self.posterLabel.setFixedSize(220, 330)
        self.posterLabel.setBorderRadius(8, 8, 8, 8)
        self.posterLabel.setScaledContents(True)
        self.topInfoLayout.addWidget(self.posterLabel)

        # A.2 右侧详情文字
        self.detailsContainer = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsContainer)
        self.detailsLayout.setContentsMargins(0, 0, 0, 0)
        self.detailsLayout.setSpacing(10)
        self.detailsLayout.setAlignment(Qt.AlignTop)

        self.titleLabel = DisplayLabel("Loading...", self)
        self.titleLabel.setWordWrap(True)

        self.metaLabel = StrongBodyLabel("年份 / 地区 / 类型", self)
        self.metaLabel.setStyleSheet("color: gray;")

        self.ratingLabel = DisplayLabel("9.0", self)  # 大号评分
        self.ratingLabel.setStyleSheet("color: #009FAA; font-family: 'Segoe UI', sans-serif; font-weight: bold;")

        self.peopleLabel = BodyLabel("导演: -\n主演: -", self)
        self.peopleLabel.setWordWrap(True)

        self.synopsisLabel = BodyLabel("简介内容...", self)
        self.synopsisLabel.setWordWrap(True)
        self.synopsisLabel.setStyleSheet("margin-top: 10px;")

        self.detailsLayout.addWidget(self.titleLabel)
        self.detailsLayout.addWidget(self.metaLabel)
        self.detailsLayout.addWidget(self.ratingLabel)
        self.detailsLayout.addWidget(self.peopleLabel)
        self.detailsLayout.addWidget(self.synopsisLabel)

        self.topInfoLayout.addWidget(self.detailsContainer, 1)  # Stretch factor 1
        self.contentLayout.addWidget(self.topInfoContainer)

        # --- 分割线 ---
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setStyleSheet("background-color: #E0E0E0;")
        self.contentLayout.addWidget(self.line)

        # --- B. 评论区 ---
        self.reviewsHeaderLayout = QHBoxLayout()
        self.reviewsTitle = StrongBodyLabel("用户影评", self)
        self.reviewsTitle.setStyleSheet("font-size: 18px;")

        self.addReviewBtn = PrimaryPushButton("写影评", self, FluentIcon.EDIT)
        self.addReviewBtn.setFixedWidth(120)
        self.addReviewBtn.clicked.connect(self.on_add_review_clicked)

        self.reviewsHeaderLayout.addWidget(self.reviewsTitle)
        self.reviewsHeaderLayout.addStretch(1)
        self.reviewsHeaderLayout.addWidget(self.addReviewBtn)

        self.contentLayout.addLayout(self.reviewsHeaderLayout)

        # 评论列表容器
        self.reviewsListLayout = QVBoxLayout()
        self.reviewsListLayout.setSpacing(10)
        self.contentLayout.addLayout(self.reviewsListLayout)

        self.scrollArea.setWidget(self.contentWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def set_movie(self, movie_id: str):
        """ 加载并显示电影详情 """
        self.current_movie_id = movie_id

        # 滚动条回到顶部
        self.scrollArea.verticalScrollBar().setValue(0)

        with SessionLocal() as session:
            try:

                # 强制刷新评分
                # 调用 Manager 重新计算该电影的评分和人数
                review_manager.update_movie_stats(session, movie_id)
                # 必须提交事务，否则下面的查询还是旧数据
                session.commit()

                # 查询电影数据
                movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
                if not movie:
                    self.titleLabel.setText("未找到电影")
                    return

                # --- 基础信息 ---
                self.titleLabel.setText(movie.title)


                # 评分显示逻辑 (核心修改点)
                if movie.rating_count > 0:
                    # 有人评分：显示分数
                    self.ratingLabel.setText(f"{movie.average_rating:.1f}")
                    # 恢复高亮颜色
                    self.ratingLabel.setStyleSheet("color: #009FAA; font-family: 'Segoe UI', sans-serif; font-weight: bold;")
                else:
                    # 无人评分：显示文案
                    self.ratingLabel.setText("暂无评分")
                    # 设置为灰色，避免误解为 0 分很差
                    self.ratingLabel.setStyleSheet("color: #808080; font-family: 'Segoe UI', sans-serif; font-weight: bold;")

                # --- 处理海报 ---
                if movie.poster_url and os.path.exists(movie.poster_url):
                    self.posterLabel.setImage(movie.poster_url)
                else:
                    self.posterLabel.setImage(":/qfluentwidgets/images/logo.png")

                # --- 拼接元数据 ---
                year = str(movie.release_date.year) if movie.release_date else "-"
                country = movie.country or "-"
                runtime = f"{movie.runtime_minutes}分钟" if movie.runtime_minutes else "-"

                genre_names = [g.name for g in movie.genres]
                genres_str = "/".join(genre_names) if genre_names else "无类型"

                self.metaLabel.setText(f"{year}  •  {country}  •  {genres_str}  •  {runtime}")

                # --- 拼接演职人员 ---
                directors = []
                actors = []
                for mp in movie.people_associations:
                    if mp.role == 'Director':
                        directors.append(mp.person.name)
                    elif mp.role == 'Actor':
                        actors.append(mp.person.name)

                people_text = ""
                if directors:
                    people_text += f"导演: {', '.join(directors)}\n"
                if actors:
                    display_actors = ', '.join(actors[:5]) + ('...' if len(actors) > 5 else '')
                    people_text += f"主演: {display_actors}"

                self.peopleLabel.setText(people_text)

                # --- 简介 ---
                self.synopsisLabel.setText(movie.synopsis or "暂无剧情简介。")

                # --- 加载评论列表 ---
                self.load_reviews(session, movie_id)

            except Exception as e:
                print(f"Load movie details error: {e}")
                self.titleLabel.setText("数据加载错误")

    def load_reviews(self, session, movie_id):
        """ 加载评论列表 """
        # 清空旧评论
        while self.reviewsListLayout.count():
            item = self.reviewsListLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 查询评论 (按时间倒序)
        reviews = session.query(Review).filter(
            Review.movie_id == movie_id
        ).order_by(Review.created_at.desc()).all()

        self.reviewsTitle.setText(f"用户影评 ({len(reviews)})")

        if not reviews:
            empty_label = BodyLabel("还没有人评论，快来抢沙发吧！", self)
            empty_label.setStyleSheet("color: gray; margin: 20px;")
            self.reviewsListLayout.addWidget(empty_label, 0, Qt.AlignCenter)
            return

        for rev in reviews:
            # 安全获取用户名
            username = rev.user.username if rev.user else "未知用户"
            time_str = rev.created_at.strftime("%Y-%m-%d") if rev.created_at else ""

            card = ReviewCard(
                username=username,
                rating=rev.rating,
                content=rev.comment or "",
                time_str=time_str,
                parent=self
            )
            self.reviewsListLayout.addWidget(card)

    @Slot()
    def on_add_review_clicked(self):
        """ 点击写影评按钮 """
        # 检查登录
        if not user_manager.is_logged_in:
            InfoBar.warning(
                title='未登录',
                content='请先登录后再发表影评。',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return

        # 弹出对话框
        dialog = AddReviewDialog(self)
        if dialog.exec():
            rating, content = dialog.get_data()

            # 调用 ReviewManager 提交
            with SessionLocal() as session:
                try:
                    review_manager.create_review(
                        session=session,
                        user_id=user_manager.current_user.user_id,
                        movie_id=self.current_movie_id,
                        rating=rating,
                        comment=content
                    )
                    session.commit()

                    # 成功提示
                    InfoBar.success(
                        title='发布成功',
                        content='你的影评已发布！',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )

                    # 刷新整个页面 (为了更新平均分和评论列表)
                    self.set_movie(self.current_movie_id)

                except ValueError as ve:
                    # 处理重复评论等业务逻辑错误
                    InfoBar.warning(title='提示', content=str(ve), parent=self)
                except Exception as e:
                    session.rollback()
                    print(f"Add review error: {e}")
                    InfoBar.error(title='错误', content='发布失败，请稍后重试', parent=self)
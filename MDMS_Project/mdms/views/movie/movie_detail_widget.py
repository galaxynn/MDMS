import os

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy)
from qfluentwidgets import (ImageLabel, TitleLabel, StrongBodyLabel, BodyLabel,
                            PushButton, FluentIcon, ScrollArea, CardWidget,
                            IconWidget, PrimaryPushButton, MessageBoxBase,
                            Slider, TextEdit, InfoBar, InfoBarPosition, CaptionLabel)

from mdms.common.review_manager import review_manager
from mdms.common.user_manager import user_manager
from mdms.database.models import Movie, Review
from mdms.database.session import SessionLocal


class AddReviewDialog(MessageBoxBase):
    """
    用户撰写影评的交互弹窗
    集成 1-10 分的滑块评分和文本评论框
    支持传入 old_rating 和 old_content 以保留或预设内容
    """

    def __init__(self, old_rating=8, old_content="", parent=None):
        super().__init__(parent)
        self.titleLabel = StrongBodyLabel("撰写影评", self)

        # 初始化评分展示与滑动条
        # 使用传入的 old_rating 设置初始值，默认为 8
        self.ratingValueLabel = StrongBodyLabel(f"评分: {old_rating} / 10", self)
        self.ratingSlider = Slider(Qt.Horizontal, self)
        self.ratingSlider.setRange(1, 10)
        self.ratingSlider.setValue(old_rating)
        self.ratingSlider.valueChanged.connect(
            lambda v: self.ratingValueLabel.setText(f"评分: {v} / 10")
        )

        # 评论文本输入框，设置固定高度
        self.contentLabel = BodyLabel("评论内容:", self)
        self.contentEdit = TextEdit(self)
        self.contentEdit.setPlaceholderText("说说你对这部电影的看法...")
        # 设置旧内容（如果有），否则为空
        self.contentEdit.setPlainText(old_content)
        self.contentEdit.setFixedHeight(120)

        # 将组件依次添加至弹窗的视图布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.ratingValueLabel)
        self.viewLayout.addWidget(self.ratingSlider)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.contentEdit)

        self.yesButton.setText("发布")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(400)

    def get_data(self):
        """ 获取弹窗输入的评分值和清理后的评论文本 """
        return self.ratingSlider.value(), self.contentEdit.toPlainText().strip()


class ReviewCard(CardWidget):
    """
    影评展示卡片
    以紧凑的水平布局展示用户信息、评分和发布时间，下方展示评论正文
    """

    def __init__(self, username, rating, content, time_str, parent=None):
        super().__init__(parent)
        self.setContentsMargins(16, 16, 16, 16)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 头部栏：包含头像图标、用户名、评分图标、分数值及日期
        top_layout = QHBoxLayout()

        user_icon = IconWidget(FluentIcon.PEOPLE, self)
        user_icon.setFixedSize(16, 16)
        user_label = BodyLabel(username, self)

        rating_icon = IconWidget(FluentIcon.HEART, self)
        rating_icon.setFixedSize(16, 16)
        rating_label = StrongBodyLabel(f"{rating} 分", self)
        rating_label.setStyleSheet("color: #009FAA;")  # 统一的主题色高亮评分

        time_label = CaptionLabel(time_str, self)
        time_label.setTextColor("#808080", "#808080")

        top_layout.addWidget(user_icon)
        top_layout.addWidget(user_label)
        top_layout.addSpacing(15)
        top_layout.addWidget(rating_icon)
        top_layout.addWidget(rating_label)
        top_layout.addStretch(1)  # 弹性空间将时间标签推向最右侧
        top_layout.addWidget(time_label)

        # 正文标签：开启自动换行以适应长篇评论
        content_label = BodyLabel(content, self)
        content_label.setWordWrap(True)

        layout.addLayout(top_layout)
        layout.addWidget(content_label)


class MovieDetailWidget(QWidget):
    """
    电影详情主页面
    展示海报、完整的元数据信息（年份/地区/演职人员/简介）以及用户评论列表
    针对超长标题进行了换行兼容性优化
    """
    backClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_movie_id = None

        # 主容器布局：移除边距以实现顶部导航栏全宽显示
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # 顶部导航工具栏
        self.headerBar = QFrame(self)
        self.headerBar.setFixedHeight(50)
        self.headerLayout = QHBoxLayout(self.headerBar)
        self.headerLayout.setContentsMargins(20, 0, 20, 0)

        self.backBtn = PushButton("返回", self, FluentIcon.RETURN)
        self.backBtn.clicked.connect(self.backClicked.emit)
        self.headerLayout.addWidget(self.backBtn)
        self.headerLayout.addStretch(1)

        self.mainLayout.addWidget(self.headerBar)

        # 全局滚动区域：确保在小屏幕下详情内容可滚动
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")

        self.contentWidget = QWidget()
        self.contentWidget.setStyleSheet("background: transparent;")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(30, 20, 30, 40)
        self.contentLayout.setSpacing(30)

        # 电影顶部核心信息容器
        self.topInfoContainer = QWidget()
        self.topInfoLayout = QHBoxLayout(self.topInfoContainer)
        self.topInfoLayout.setContentsMargins(0, 0, 0, 0)
        self.topInfoLayout.setSpacing(30)
        self.topInfoLayout.setAlignment(Qt.AlignTop)

        # 海报展示区：固定尺寸以防止布局塌陷
        self.posterLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        self.posterLabel.setFixedSize(220, 330)
        self.posterLabel.setBorderRadius(8, 8, 8, 8)
        self.posterLabel.setScaledContents(True)
        self.topInfoLayout.addWidget(self.posterLabel)

        # 文字信息详情容器
        self.detailsContainer = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsContainer)
        self.detailsLayout.setContentsMargins(0, 0, 0, 0)
        self.detailsLayout.setSpacing(10)
        self.detailsLayout.setAlignment(Qt.AlignTop)

        # 标题组件：使用 TitleLabel 替代 DisplayLabel 以降低超长标题的视觉负担
        # 开启 WordWrap 并设置 Expanding Policy，使其在水平空间不足时垂直向下延伸，不挤压海报
        self.titleLabel = TitleLabel("Loading...", self)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.metaLabel = StrongBodyLabel("年份 / 地区 / 类型", self)
        self.metaLabel.setStyleSheet("color: gray;")

        self.ratingLabel = TitleLabel("9.0", self)
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

        # 详情文字区拉伸因子设为 1，确保其占据海报右侧所有剩余空间
        self.topInfoLayout.addWidget(self.detailsContainer, 1)
        self.contentLayout.addWidget(self.topInfoContainer)

        # 视觉分割线
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setStyleSheet("background-color: #E0E0E0;")
        self.contentLayout.addWidget(self.line)

        # 影评区头部栏
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

        # 评论列表垂直布局
        self.reviewsListLayout = QVBoxLayout()
        self.reviewsListLayout.setSpacing(10)
        self.contentLayout.addLayout(self.reviewsListLayout)

        self.scrollArea.setWidget(self.contentWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def set_movie(self, movie_id: str):
        """
        数据库驱动的视图更新函数
        根据 movie_id 加载电影完整信息并刷新 UI
        """
        self.current_movie_id = movie_id
        self.scrollArea.verticalScrollBar().setValue(0)

        with SessionLocal() as session:
            try:
                movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
                if not movie:
                    self.titleLabel.setText("未找到电影")
                    return

                # 直接显示原始标题，配合 TitleLabel 的 WordWrap 属性实现安全换行
                self.titleLabel.setText(movie.title)

                # 评分展示：根据是否存在有效评分切换颜色状态
                if movie.rating_count > 0:
                    self.ratingLabel.setText(f"{movie.average_rating:.1f}")
                    self.ratingLabel.setStyleSheet(
                        "color: #009FAA; font-family: 'Segoe UI', sans-serif; font-weight: bold;")
                else:
                    self.ratingLabel.setText("暂无评分")
                    self.ratingLabel.setStyleSheet(
                        "color: #808080; font-family: 'Segoe UI', sans-serif; font-weight: bold;")

                # 海报资源加载逻辑
                if movie.poster_url and os.path.exists(movie.poster_url):
                    self.posterLabel.setImage(movie.poster_url)
                else:
                    self.posterLabel.setImage(":/qfluentwidgets/images/logo.png")

                # 元数据字符串拼接：年份、国家、类型及片长
                year = str(movie.release_date.year) if movie.release_date else "-"
                country = movie.country or "-"
                runtime = f"{movie.runtime_minutes}分钟" if movie.runtime_minutes else "-"
                genre_names = [g.name for g in movie.genres]
                genres_str = "/".join(genre_names) if genre_names else "无类型"

                self.metaLabel.setText(f"{year}  •  {country}  •  {genres_str}  •  {runtime}")

                # 演职人员提取：筛选导演与前 5 位主演
                directors = [mp.person.name for mp in movie.people_associations if mp.role == 'Director']
                actors = [mp.person.name for mp in movie.people_associations if mp.role == 'Actor']

                people_text = ""
                if directors:
                    people_text += f"导演: {', '.join(directors)}\n"
                if actors:
                    display_actors = ', '.join(actors[:5]) + ('...' if len(actors) > 5 else '')
                    people_text += f"主演: {display_actors}"

                self.peopleLabel.setText(people_text)
                self.synopsisLabel.setText(movie.synopsis or "暂无剧情简介。")

                # 异步或级联加载评论区内容
                self.load_reviews(session, movie_id)

            except Exception as e:
                print(f"数据加载异常: {e}")
                self.titleLabel.setText("数据加载错误")

    def load_reviews(self, session, movie_id):
        """ 清空并重新根据时间倒序加载电影的所有评论 """
        while self.reviewsListLayout.count():
            item = self.reviewsListLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
        """ 提交评论的槽函数：自动检测是新增还是修改 """
        if not user_manager.is_logged_in:
            InfoBar.warning(
                title='未登录',
                content='请先登录后再发表影评。',
                orient=Qt.Horizontal,
                position=InfoBarPosition.TOP,
                parent=self
            )
            return

        user_id = user_manager.current_user.user_id
        movie_id = self.current_movie_id

        # 变量初始化
        is_edit_mode = False
        review_id = None
        old_rating = 8
        old_content = ""

        # 1. 第一步：查询是否存在旧评论
        # 使用临时 session 读取数据，读取后立即提取值，以免 session 关闭后对象过期
        with SessionLocal() as session:
            existing_review = session.query(Review).filter_by(
                user_id=user_id,
                movie_id=movie_id
            ).first()

            if existing_review:
                is_edit_mode = True
                review_id = existing_review.review_id
                old_rating = existing_review.rating
                # 注意处理 comment 为 None 的情况
                old_content = existing_review.comment or ""

        # 2. 第二步：打开弹窗
        # 将查询到的旧数据传入弹窗
        dialog = AddReviewDialog(old_rating=old_rating, old_content=old_content, parent=self)

        # 为了更好的体验，如果是修改，更改弹窗标题和按钮文字
        if is_edit_mode:
            dialog.titleLabel.setText("修改我的影评")
            dialog.yesButton.setText("更新")

        if dialog.exec():
            rating, content = dialog.get_data()

            # 3. 第三步：写入数据库
            with SessionLocal() as session:
                try:
                    if is_edit_mode:
                        # --- 修改模式 ---
                        review_manager.update_review(
                            session=session,
                            review_id=review_id,
                            new_rating=rating,
                            new_comment=content
                        )
                        success_msg = '你的影评已修改！'
                    else:
                        # --- 新增模式 ---
                        review_manager.create_review(
                            session=session,
                            user_id=user_id,
                            movie_id=movie_id,
                            rating=rating,
                            comment=content
                        )
                        success_msg = '你的影评已发布！'

                    session.commit()

                    InfoBar.success(
                        title='成功',
                        content=success_msg,
                        orient=Qt.Horizontal,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    # 重新加载视图以刷新平均分和评论列表
                    self.set_movie(self.current_movie_id)

                except ValueError as ve:
                    # 捕获业务逻辑错误
                    InfoBar.warning(title='提示', content=str(ve), parent=self)
                except Exception as e:
                    session.rollback()
                    print(f"影评操作失败: {e}")
                    InfoBar.error(title='错误', content='操作失败，请稍后重试', parent=self)
import os

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QGraphicsDropShadowEffect)
from qfluentwidgets import (ImageLabel, StrongBodyLabel, BodyLabel,
                            FluentIcon, SmoothScrollArea, CardWidget,
                            IconWidget, CaptionLabel, LargeTitleLabel, SubtitleLabel,
                            TitleLabel, TransparentToolButton, themeColor)

from mdms.database.models import Person
from mdms.database.session import SessionLocal


class FilmographyCard(CardWidget):
    """
    影视作品表单条记录卡片
    采用水平布局，左侧显示缩略海报，中间展示电影标题与参与角色，右侧高亮年份
    """

    def __init__(self, title, role, year, poster_url, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)  # 固定高度以保证列表整齐
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 20, 10)
        layout.setSpacing(16)

        # 1. 电影海报：微缩图展示，固定纵横比
        self.poster = ImageLabel(poster_url if poster_url else ":/qfluentwidgets/images/logo.png", self)
        self.poster.setFixedSize(52, 70)
        self.poster.setBorderRadius(6, 6, 6, 6)
        self.poster.setScaledContents(True)

        # 2. 作品信息区：标题与具体角色（如：担任 导演/演员）
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignVCenter)
        info_layout.setSpacing(4)

        self.titleLabel = TitleLabel(title, self)
        self.roleLabel = BodyLabel(self)
        self.roleLabel.setText(f"担任: {role}")
        self.roleLabel.setStyleSheet("color: #666666; font-size: 13px;")

        info_layout.addWidget(self.titleLabel)
        info_layout.addWidget(self.roleLabel)

        # 3. 年份标识：使用当前主题色（ThemeColor）进行高亮
        self.yearLabel = StrongBodyLabel(year, self)
        self.yearLabel.setStyleSheet(f"color: {themeColor().name()}; font-size: 16px;")

        layout.addWidget(self.poster)
        layout.addLayout(info_layout)
        layout.addStretch(1)
        layout.addWidget(self.yearLabel)


class PeopleDetailWidget(QWidget):
    """
    演职人员详情页面
    包含 Hero Section（头像与个人基本信息）和影视作品年表
    """
    backClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.person_id = None
        self.setObjectName("PeopleDetailWidget")
        self.setStyleSheet("PeopleDetailWidget{background-color: transparent;}")

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # 1. 顶部返回导航栏
        self.headerBar = QFrame(self)
        self.headerBar.setFixedHeight(50)
        self.headerBar.setStyleSheet("border-bottom: 1px solid rgba(0, 0, 0, 0.05); background-color: transparent;")

        self.headerLayout = QHBoxLayout(self.headerBar)
        self.headerLayout.setContentsMargins(16, 0, 16, 0)

        self.backBtn = TransparentToolButton(FluentIcon.RETURN, self)
        self.backBtn.setFixedSize(32, 32)
        self.backBtn.setIconSize(QSize(14, 14))
        self.backBtn.clicked.connect(self.backClicked.emit)

        self.headerTitle = StrongBodyLabel("返回列表", self)

        self.headerLayout.addWidget(self.backBtn)
        self.headerLayout.addWidget(self.headerTitle)
        self.headerLayout.addStretch(1)

        self.mainLayout.addWidget(self.headerBar)

        # 2. 丝滑滚动区域：承载下方所有内容
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")
        self.scrollArea.viewport().setStyleSheet("background: transparent;")

        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(40, 30, 40, 50)
        self.contentLayout.setSpacing(30)

        # --- A. 人员头部核心信息区 (Hero Section) ---
        self.topInfoContainer = QWidget()
        self.topInfoLayout = QHBoxLayout(self.topInfoContainer)
        self.topInfoLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.topInfoLayout.setSpacing(40)

        # A.1 个人照片：增加阴影效果（GraphicsDropShadowEffect）以提升视觉层次感
        self.photoContainer = QWidget()
        self.photoLayout = QVBoxLayout(self.photoContainer)
        self.photoLayout.setContentsMargins(0, 0, 0, 0)

        self.photoLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        self.photoLabel.setFixedSize(200, 280)
        self.photoLabel.setBorderRadius(12, 12, 12, 12)
        self.photoLabel.setScaledContents(True)

        shadow = QGraphicsDropShadowEffect(self.photoLabel)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.photoLabel.setGraphicsEffect(shadow)

        self.photoLayout.addWidget(self.photoLabel)
        self.topInfoLayout.addWidget(self.photoContainer)

        # A.2 文字介绍区：包括姓名、生卒日期及简介
        self.detailsContainer = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsContainer)
        self.detailsLayout.setAlignment(Qt.AlignTop)
        self.detailsLayout.setSpacing(8)

        self.nameLabel = LargeTitleLabel("Loading...", self)
        self.nameLabel.setWordWrap(True)

        # Meta 数据行（如：出生日期）
        self.metaContainer = QWidget()
        self.metaLayout = QHBoxLayout(self.metaContainer)
        self.metaLayout.setContentsMargins(0, 0, 0, 0)
        self.metaLayout.setSpacing(8)
        self.metaLayout.setAlignment(Qt.AlignLeft)

        self.calendarIcon = IconWidget(FluentIcon.CALENDAR, self)
        self.calendarIcon.setFixedSize(16, 16)
        self.metaLabel = BodyLabel("出生日期: -", self)
        self.metaLabel.setStyleSheet("color: gray;")

        self.metaLayout.addWidget(self.calendarIcon)
        self.metaLayout.addWidget(self.metaLabel)
        self.metaLayout.addStretch(1)

        self.bioHeader = SubtitleLabel("个人简介", self)
        self.bioHeader.setStyleSheet("margin-top: 20px;")

        self.bioLabel = BodyLabel("暂无简介", self)
        self.bioLabel.setWordWrap(True)
        self.bioLabel.setStyleSheet("color: #404040; line-height: 1.6;")

        self.detailsLayout.addWidget(self.nameLabel)
        self.detailsLayout.addWidget(self.metaContainer)
        self.detailsLayout.addWidget(self.bioHeader)
        self.detailsLayout.addWidget(self.bioLabel)
        self.detailsLayout.addStretch(1)

        self.topInfoLayout.addWidget(self.detailsContainer, 1)
        self.contentLayout.addWidget(self.topInfoContainer)

        # --- B. 影视作品年表 ---
        self.filmHeaderLayout = QHBoxLayout()
        self.filmTitle = SubtitleLabel("影视作品", self)
        self.filmCountLabel = CaptionLabel("(0部)", self)
        self.filmCountLabel.setStyleSheet("color: gray; margin-bottom: 4px;")

        self.filmHeaderLayout.addWidget(self.filmTitle)
        self.filmHeaderLayout.addWidget(self.filmCountLabel, 0, Qt.AlignBottom)
        self.filmHeaderLayout.addStretch(1)

        self.contentLayout.addLayout(self.filmHeaderLayout)

        # 动态生成的作品列表容器
        self.filmListLayout = QVBoxLayout()
        self.filmListLayout.setSpacing(12)
        self.contentLayout.addLayout(self.filmListLayout)

        self.scrollArea.setWidget(self.contentWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def set_person(self, person_id: str):
        """
        数据加载入口：根据人员 ID 加载并刷新视图
        """
        self.person_id = person_id
        # 切换人员时，自动将滚动条重置回顶部
        self.scrollArea.verticalScrollBar().setValue(0)

        session = SessionLocal()
        try:
            # 执行数据库查询，通过 ID 获取 Person 对象
            person = session.query(Person).filter(Person.person_id == person_id).first()
            if not person:
                self.nameLabel.setText("未找到人员信息")
                return

            # 刷新 UI 基础文字信息
            self.nameLabel.setText(person.name)
            birth = person.birthdate.strftime("%Y年%m月%d日") if person.birthdate else "未知日期"
            self.metaLabel.setText(f"{birth}")
            self.bioLabel.setText(person.bio if person.bio else "暂无简介。")

            # 异步处理本地图片加载，如果路径无效则回退至 Logo
            if person.photo_url and os.path.exists(person.photo_url):
                self.photoLabel.setImage(person.photo_url)
            else:
                self.photoLabel.setImage(":/qfluentwidgets/images/logo.png")

            # 调用子函数加载其名下的影视作品列表
            self.load_filmography(person)

        except Exception as e:
            print(f"载入人员详情错误: {e}")
            self.nameLabel.setText("数据加载错误")
        finally:
            session.close()

    def load_filmography(self, person_obj):
        """
        影视作品加载逻辑：从 Person 对象中提取 MoviePerson 关联并按日期排序展示
        """
        # 第一步：清空界面上现有的作品卡片，防止重复堆叠
        while self.filmListLayout.count():
            item = self.filmListLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 第二步：获取多对多关联数据并执行业务排序 (按上映日期从新到旧)
        associations = person_obj.movie_associations
        associations.sort(
            key=lambda x: x.movie.release_date.strftime("%Y-%m-%d") if x.movie and x.movie.release_date else "0000",
            reverse=True
        )

        count = len(associations)
        self.filmCountLabel.setText(f"({count}部)")

        # 第三步：空数据友好展示
        if not associations:
            empty_card = CardWidget(self)
            empty_layout = QHBoxLayout(empty_card)
            empty_icon = IconWidget(FluentIcon.INFO, self)
            empty_icon.setFixedSize(20, 20)
            empty_text = BodyLabel("暂无相关作品记录", self)
            empty_layout.addStretch(1)
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_text)
            empty_layout.addStretch(1)
            self.filmListLayout.addWidget(empty_card)
            return

        # 第四步：遍历关联结果并实例化卡片
        for relation in associations:
            movie = relation.movie
            if not movie: continue

            year_str = str(movie.release_date.year) if movie.release_date else "-"

            card = FilmographyCard(
                title=movie.title,
                role=relation.role,
                year=year_str,
                poster_url=movie.poster_url,
                parent=self
            )
            self.filmListLayout.addWidget(card)
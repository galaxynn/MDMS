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
    作品表卡片
    """

    def __init__(self, title, role, year, poster_url, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)  # 固定卡片高度
        self.setCursor(Qt.PointingHandCursor)  # 鼠标悬停变为手型

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 20, 10)  # 调整内部边距
        layout.setSpacing(16)

        # 1. 电影海报 (带圆角，固定尺寸)
        # 这里固定尺寸为 52x70，比例约为 0.74，适合海报展示
        self.poster = ImageLabel(poster_url if poster_url else ":/qfluentwidgets/images/logo.png", self)
        self.poster.setFixedSize(52, 70)
        self.poster.setBorderRadius(6, 6, 6, 6)
        self.poster.setScaledContents(True)

        # 2. 信息区
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignVCenter)
        info_layout.setSpacing(4)  # 紧凑一点

        # 标题使用 TitleLabel (更突出)
        self.titleLabel = TitleLabel(title, self)

        # 角色使用 BodyLabel (辅助文字)
        self.roleLabel = BodyLabel(self)
        self.roleLabel.setText(f"担任: {role}")
        self.roleLabel.setStyleSheet("color: #666666; font-size: 13px;")

        info_layout.addWidget(self.titleLabel)
        info_layout.addWidget(self.roleLabel)

        # 3. 年份 (强样式，靠右对齐)
        self.yearLabel = StrongBodyLabel(year, self)
        self.yearLabel.setStyleSheet(f"color: {themeColor().name()}; font-size: 16px;")

        layout.addWidget(self.poster)
        layout.addLayout(info_layout)
        layout.addStretch(1)
        layout.addWidget(self.yearLabel)


class PeopleDetailWidget(QWidget):
    backClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.person_id = None
        self.setObjectName("PeopleDetailWidget")
        # 设置背景色为透明，避免遮挡主窗口背景
        self.setStyleSheet("PeopleDetailWidget{background-color: transparent;}")

        # --- 主布局 ---
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # 1. 顶部导航栏
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

        # 2. 滚动区域
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent;")
        self.scrollArea.viewport().setStyleSheet("background: transparent;")

        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(40, 30, 40, 50)
        self.contentLayout.setSpacing(30)

        # --- A. 人员头部信息区 (Hero Section) ---
        self.topInfoContainer = QWidget()
        self.topInfoLayout = QHBoxLayout(self.topInfoContainer)
        self.topInfoLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.topInfoLayout.setSpacing(40)

        # A.1 照片 (带阴影和固定尺寸)
        self.photoContainer = QWidget()
        self.photoLayout = QVBoxLayout(self.photoContainer)
        self.photoLayout.setContentsMargins(0, 0, 0, 0)

        self.photoLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        self.photoLabel.setFixedSize(200, 280) # 固定人物照片大小
        self.photoLabel.setBorderRadius(12, 12, 12, 12)
        self.photoLabel.setScaledContents(True)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self.photoLabel)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.photoLabel.setGraphicsEffect(shadow)

        self.photoLayout.addWidget(self.photoLabel)
        self.topInfoLayout.addWidget(self.photoContainer)

        # A.2 文字详情
        self.detailsContainer = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsContainer)
        self.detailsLayout.setAlignment(Qt.AlignTop)
        self.detailsLayout.setSpacing(8)

        # 姓名
        self.nameLabel = LargeTitleLabel("Loading...", self)
        self.nameLabel.setWordWrap(True)

        # Meta 信息行
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

        # 简介
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

        self.contentLayout.addSpacing(10)

        # --- B. 影视作品 ---
        self.filmHeaderLayout = QHBoxLayout()
        self.filmTitle = SubtitleLabel("影视作品", self)
        self.filmCountLabel = CaptionLabel("(0部)", self)
        self.filmCountLabel.setStyleSheet("color: gray; margin-bottom: 4px;")

        self.filmHeaderLayout.addWidget(self.filmTitle)
        self.filmHeaderLayout.addWidget(self.filmCountLabel, 0, Qt.AlignBottom)
        self.filmHeaderLayout.addStretch(1)

        self.contentLayout.addLayout(self.filmHeaderLayout)

        # 列表容器
        self.filmListLayout = QVBoxLayout()
        self.filmListLayout.setSpacing(12)
        self.contentLayout.addLayout(self.filmListLayout)

        self.scrollArea.setWidget(self.contentWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def set_person(self, person_id: str):
        """ 加载人员详情 """
        self.person_id = person_id
        self.scrollArea.verticalScrollBar().setValue(0)

        session = SessionLocal()
        try:
            person = session.query(Person).filter(Person.person_id == person_id).first()
            if not person:
                self.nameLabel.setText("未找到人员信息")
                return

            # 1. 基础信息
            self.nameLabel.setText(person.name)
            birth = person.birthdate.strftime("%Y年%m月%d日") if person.birthdate else "未知日期"
            self.metaLabel.setText(f"{birth}")
            self.bioLabel.setText(person.bio if person.bio else "暂无简介。")

            # 设置图片
            if person.photo_url and os.path.exists(person.photo_url):
                self.photoLabel.setImage(person.photo_url)
            else:
                self.photoLabel.setImage(":/qfluentwidgets/images/logo.png")

            # 2. 加载作品列表
            self.load_filmography(person)

        except Exception as e:
            print(f"Load person details error: {e}")
            self.nameLabel.setText("数据加载错误")
        finally:
            session.close()

    def load_filmography(self, person_obj):
        """ 加载该人员参与的电影 """
        # 清空旧列表
        while self.filmListLayout.count():
            item = self.filmListLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 获取并排序关联作品 (按上映日期倒序)
        associations = person_obj.movie_associations
        associations.sort(
            key=lambda x: x.movie.release_date.strftime("%Y-%m-%d") if x.movie and x.movie.release_date else "0000",
            reverse=True
        )

        count = len(associations)
        self.filmCountLabel.setText(f"({count}部)")

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

        for relation in associations:
            movie = relation.movie
            if not movie:
                continue

            year_str = str(movie.release_date.year) if movie.release_date else "-"

            card = FilmographyCard(
                title=movie.title,
                role=relation.role,
                year=year_str,
                poster_url=movie.poster_url,
                parent=self
            )
            self.filmListLayout.addWidget(card)
from PySide6.QtCore import Qt, Signal
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QWidget,
                               QHBoxLayout)
from qfluentwidgets import (ElevatedCardWidget, ImageLabel, CaptionLabel,
                            SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            SearchLineEdit)

from mdms.database.models import Person
from mdms.database.session import SessionLocal


class PersonCard(ElevatedCardWidget):
    """
    自定义人员卡片组件
    """
    personClicked = Signal(str)

    def __init__(self, person_id: str, photoPath: str, name: str, parent=None):
        super().__init__(parent)
        self.person_id = person_id
        self.personName = name  # 用于搜索

        # 默认头像处理
        if not photoPath:
            # 建议准备一个默认的 placeholder_person.png
            photoPath = ":/qfluentwidgets/images/logo.png"

        # 1. 头像图片 (圆形或圆角矩形)
        self.iconWidget = ImageLabel(photoPath, self)
        self.iconWidget.scaledToHeight(120)
        # 设置稍大的圆角使其看起来柔和，或者设为 60 变成圆形(如果宽高一致)
        self.iconWidget.setBorderRadius(60, 60, 60, 60)
        self.iconWidget.setFixedSize(120, 120)

        # 2. 姓名
        self.label = CaptionLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)

        # 3. 布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 20, 10, 10)

        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignTop)

        self.setFixedSize(160, 210)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.personClicked.emit(self.person_id)


class PeopleGalleryWidget(QFrame):
    """
    演职人员库展示主界面
    """
    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.cards = []

        # 1. 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # 2. 头部 (标题 + 搜索)
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)

        self.searchEdit = SearchLineEdit(self)
        self.searchEdit.setPlaceholderText("搜索导演/演员...")
        self.searchEdit.setFixedWidth(240)
        self.searchEdit.textChanged.connect(self.search_people)

        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.searchEdit)

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(10)

        # 3. 滚动区域
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

        # 4. 加载数据
        self.load_people_from_db()

    def load_people_from_db(self):
        """ 加载所有人员数据 """
        session = SessionLocal()
        try:
            people = session.query(Person).all()
            for person in people:
                card = PersonCard(
                    person_id=person.person_id,
                    photoPath=person.photo_url,
                    name=person.name,
                    parent=self.scrollWidget
                )
                card.personClicked.connect(self.on_card_clicked)
                self.flowLayout.addWidget(card)
                self.cards.append(card)
        except Exception as e:
            print(f"Error loading people: {e}")
        finally:
            session.close()

    def on_card_clicked(self, person_id: str):
        self.requestOpenDetail.emit(person_id)

    def search_people(self, text: str):
        text = text.strip().lower()
        for i in range(self.flowLayout.count() - 1, -1, -1):
            item = self.flowLayout.itemAt(i)
            if item and item.widget():
                self.flowLayout.removeWidget(item.widget())
                item.widget().hide()

        for card in self.cards:
            if not text or text in card.personName.lower():
                card.show()
                self.flowLayout.addWidget(card)
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QApplication, QWidget,
                               QHBoxLayout)
from qfluentwidgets import (ElevatedCardWidget, ImageLabel, CaptionLabel,
                            SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            SearchLineEdit)

# 导入数据库相关
from mdms.database.session import SessionLocal
from mdms.database.models import Person

# 导入通用的分页组件
from mdms.common.fluent_paginator import FluentPaginator


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
            # 建议准备一个默认的 placeholder_person.png，这里暂时用 logo 代替
            photoPath = ":/qfluentwidgets/images/logo.png"

        # 1. 头像图片 (圆形或圆角矩形)
        self.iconWidget = ImageLabel(photoPath, self)
        # 调整为正方形以配合圆形遮罩
        self.iconWidget.setFixedSize(120, 120)
        # 设置半径为边长的一半，实现圆形效果
        self.iconWidget.setBorderRadius(60, 60, 60, 60)
        self.iconWidget.setScaledContents(True)  # 确保图片填满容器

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
    演职人员库展示主界面 (已集成 FluentPaginator 分页)
    """
    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 状态变量
        self.current_search_text = ""
        self.cards = []

        # 1. 初始化UI
        self.init_ui(text)

        # 2. 初始加载数据
        self.load_data(page=1)

    def init_ui(self, text):
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # === 头部 (标题 + 搜索) ===
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)

        self.searchEdit = SearchLineEdit(self)
        self.searchEdit.setPlaceholderText("搜索导演/演员...")
        self.searchEdit.setFixedWidth(240)

        # 绑定搜索事件 (回车或点击按钮触发数据库查询)
        self.searchEdit.searchSignal.connect(self.on_search_triggered)
        self.searchEdit.returnPressed.connect(self.on_search_triggered)
        # 可选：清空时重置
        self.searchEdit.textChanged.connect(self.on_search_text_changed)

        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.searchEdit)

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(10)

        # === 滚动区域 ===
        self.scrollArea = ScrollArea(self)

        # [关键修复] 强制垂直滚动条始终显示，防止布局抖动
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

        # === 底部：集成自定义分页器 ===
        self.paginator = FluentPaginator(self)
        self.paginator.set_page_size(20)  # 设置为每页20个
        self.paginator.pageChanged.connect(self.load_data)  # 连接翻页信号

        self.mainLayout.addWidget(self.paginator, 0, Qt.AlignBottom)

    def load_data(self, page: int):
        """ 核心数据加载逻辑 (带分页) """
        if SessionLocal is None:
            return

        session = SessionLocal()
        try:
            # 构建基础查询
            query = session.query(Person)

            # 1. 搜索过滤
            if self.current_search_text:
                query = query.filter(Person.name.ilike(f"%{self.current_search_text}%"))

            # 2. 获取总数并更新分页器
            total_items = query.count()
            self.paginator.set_total_items(total_items)
            self.paginator.set_current_page(page)

            # 3. 分页查询
            limit = self.paginator.get_page_size()
            offset = (page - 1) * limit
            people = query.offset(offset).limit(limit).all()

            # 4. 渲染
            self.update_gallery(people)

            # 回到顶部
            self.scrollArea.verticalScrollBar().setValue(0)

        except Exception as e:
            print(f"Error loading people: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

    def update_gallery(self, people):
        """ 刷新界面卡片 """
        # 清空现有卡片
        # [修复] 兼容 takeAt 返回 Widget 或 QLayoutItem 的情况
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)

            # 如果 item 有 .widget() 方法（它是 QLayoutItem），则调用它获取 widget
            # 否则（它是 PersonCard 实例），直接把它当作 widget
            widget = item.widget() if hasattr(item, 'widget') else item

            if widget:
                widget.deleteLater()

        self.cards.clear()

        # 生成新卡片
        if not people:
            no_data_label = CaptionLabel("未找到相关演职人员", self.scrollWidget)
            no_data_label.setAlignment(Qt.AlignCenter)
            self.flowLayout.addWidget(no_data_label)
            return

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

    def on_search_triggered(self):
        """ 搜索触发 """
        self.current_search_text = self.searchEdit.text().strip()
        self.load_data(page=1)

    def on_search_text_changed(self, text):
        """ 搜索框清空时自动恢复 """
        if not text.strip() and self.current_search_text:
            self.current_search_text = ""
            self.load_data(page=1)

    def on_card_clicked(self, person_id: str):
        self.requestOpenDetail.emit(person_id)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    # 测试代码
    w = PeopleGalleryWidget("演职人员库")
    w.resize(960, 700)
    w.show()

    app.exec()
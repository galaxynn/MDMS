import sys
import traceback

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QApplication, QWidget,
                               QHBoxLayout)
from qfluentwidgets import (ElevatedCardWidget, ImageLabel, CaptionLabel,
                            SubtitleLabel, setFont, FlowLayout, ScrollArea, SmoothMode,
                            SearchLineEdit)

# 导入底层数据模型与会话管理
from mdms.database.session import SessionLocal
from mdms.database.models import Person

# 导入通用的分页控制组件
from mdms.common.fluent_paginator import FluentPaginator


class PersonCard(ElevatedCardWidget):
    """
    演职人员展示卡片组件
    采用圆形头像设计，并提供悬浮阴影（Elevated）视觉效果。
    """
    # 点击卡片时向父组件发送人员唯一标识符 ID
    personClicked = Signal(str)

    def __init__(self, person_id: str, photoPath: str, name: str, parent=None):
        super().__init__(parent)
        self.person_id = person_id
        self.personName = name

        # 容错处理：若数据库中无照片路径，使用默认占位图
        if not photoPath:
            photoPath = ":/qfluentwidgets/images/logo.png"

        # 1. 头像组件配置
        self.iconWidget = ImageLabel(photoPath, self)
        # 固定尺寸并设置 border-radius 为边长的一半，从而渲染为圆形
        self.iconWidget.setFixedSize(120, 120)
        self.iconWidget.setBorderRadius(60, 60, 60, 60)
        self.iconWidget.setScaledContents(True)

        # 2. 姓名标签配置
        self.label = CaptionLabel(name, self)
        self.label.setAlignment(Qt.AlignCenter)

        # 3. 内部布局：垂直居中排列头像与姓名
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 20, 10, 10)

        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignTop)

        # 设置卡片容器固定尺寸与手型光标
        self.setFixedSize(160, 210)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, e):
        """ 捕获释放事件以触发自定义点击信号 """
        super().mouseReleaseEvent(e)
        self.personClicked.emit(self.person_id)


class PeopleGalleryWidget(QFrame):
    """
    演职人员库主界面
    支持实时搜索过滤、流式布局展示以及物理分页查询。
    """
    # 请求打开人员详细信息页面的信号
    requestOpenDetail = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 状态变量：维护当前搜索词以便分页查询时共享过滤状态
        self.current_search_text = ""
        self.cards = []

        # 1. 构造用户界面
        self.init_ui(text)

        # 2. 初始加载第一页数据
        self.load_data(page=1)

    def init_ui(self, text):
        """ 初始化 UI 布局与信号绑定 """
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # 头部导航栏：标题与搜索框
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel(text, self)
        setFont(self.titleLabel, 24)

        self.searchEdit = SearchLineEdit(self)
        self.searchEdit.setPlaceholderText("搜索导演/演员...")
        self.searchEdit.setFixedWidth(240)

        # 绑定搜索逻辑：按下回车或点击搜索按钮均触发查询
        self.searchEdit.searchSignal.connect(self.on_search_triggered)
        self.searchEdit.returnPressed.connect(self.on_search_triggered)
        self.searchEdit.textChanged.connect(self.on_search_text_changed)

        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.searchEdit)

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(10)

        # 中间滚动区域：使用 FlowLayout 实现自动换行网格布局
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) # 防止因滚动条出现导致的水平宽度抖动
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

        # 底部区域：集成物理分页器
        self.paginator = FluentPaginator(self)
        self.paginator.set_page_size(20)
        # 监听翻页动作：点击数字或“下一页”时重新执行 load_data
        self.paginator.pageChanged.connect(self.load_data)

        self.mainLayout.addWidget(self.paginator, 0, Qt.AlignBottom)

    def load_data(self, page: int):
        """
        核心数据加载逻辑
        执行基于 SQLAlchemy 的数据库过滤、统计与分页查询
        """
        if SessionLocal is None:
            return

        session = SessionLocal()
        try:
            # 构建基础查询语句
            query = session.query(Person)

            # 1. 应用模糊搜索过滤
            if self.current_search_text:
                query = query.filter(Person.name.ilike(f"%{self.current_search_text}%"))

            # 2. 获取符合条件的记录总数并同步给分页器
            total_items = query.count()
            self.paginator.set_total_items(total_items)
            self.paginator.set_current_page(page)

            # 3. 计算偏移量并执行物理分页查询（提升大数据量下的加载性能）
            limit = self.paginator.get_page_size()
            offset = (page - 1) * limit
            people = query.offset(offset).limit(limit).all()

            # 4. 刷新前端画廊界面展示
            self.update_gallery(people)

            # 每次翻页后自动将视图滚动回顶部
            self.scrollArea.verticalScrollBar().setValue(0)

        except Exception as e:
            print(f"载入人员数据失败: {e}")
            traceback.print_exc()
        finally:
            session.close()

    def update_gallery(self, people):
        """ UI 刷新逻辑：安全地销毁旧卡片并渲染新数据 """
        # 清空布局内现有的所有 widget，防止内存泄漏和重叠显示
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget() if hasattr(item, 'widget') else item
            if widget:
                widget.deleteLater()

        self.cards.clear()

        # 空状态反馈
        if not people:
            no_data_label = CaptionLabel("未找到相关演职人员", self.scrollWidget)
            no_data_label.setAlignment(Qt.AlignCenter)
            self.flowLayout.addWidget(no_data_label)
            return

        # 循环实例化人员卡片并添加至流式布局
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
        """ 搜索事件响应：重置页码为 1 并更新状态执行查询 """
        self.current_search_text = self.searchEdit.text().strip()
        self.load_data(page=1)

    def on_search_text_changed(self, text):
        """ 交互增强：当搜索框被手动清空时，自动恢复完整列表展示 """
        if not text.strip() and self.current_search_text:
            self.current_search_text = ""
            self.load_data(page=1)

    def on_card_clicked(self, person_id: str):
        """ 转发点击信号：通知主框架跳转至特定人员的详情页面 """
        self.requestOpenDetail.emit(person_id)


if __name__ == '__main__':
    # 启用 Fluent 组件的高 DPI 缩放兼容性设置
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    w = PeopleGalleryWidget("演职人员库")
    w.resize(960, 700)
    w.show()

    app.exec()
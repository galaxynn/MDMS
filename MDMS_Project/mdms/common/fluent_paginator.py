import math
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QButtonGroup
from qfluentwidgets import (CaptionLabel, TransparentToolButton,
                            PrimaryPushButton, FluentIcon as FIF)


class FluentPaginator(QWidget):
    """
    基于 QFluentWidgets 风格的自定义数字分页器
    替代收费的 Pager 组件，提供上一页、下一页及数字跳转功能。
    """

    # 信号：当页码发生改变时触发，参数为新的页码 (int)
    pageChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # === 内部状态 ===
        self._total_items = 0
        self._page_size = 20
        self._current_page = 1
        self._total_pages = 1
        self._max_visible_buttons = 7  # 能够显示的数字按钮最大数量

        # === UI 布局 ===
        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 10, 0, 10)
        self.hLayout.setSpacing(5)
        self.hLayout.setAlignment(Qt.AlignCenter)

        # 按钮组 (用于管理按钮状态，虽然这里主要靠重新渲染)
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.buttonClicked.connect(self._on_button_clicked)

        # 初始化绘制
        self._update_ui()

    def set_total_items(self, total: int):
        """
        设置数据总条数。
        通常在数据库执行 .count() 后调用此方法，组件会自动计算总页数并刷新 UI。
        """
        self._total_items = total
        self._calculate_pages()
        self._update_ui()

    def set_page_size(self, size: int):
        """设置每页显示的数量"""
        if size < 1: size = 1
        self._page_size = size
        self._calculate_pages()
        self._update_ui()

    def get_page_size(self) -> int:
        return self._page_size

    def get_current_page(self) -> int:
        return self._current_page

    def set_current_page(self, page: int):
        """
        代码主动设置当前页 (例如搜索后重置为第1页)。
        注意：此方法不会触发 pageChanged 信号，以避免循环调用。
        """
        if page < 1: page = 1
        if page > self._total_pages: page = self._total_pages

        self._current_page = page
        self._update_ui()

    def _calculate_pages(self):
        """根据总条数和每页大小计算总页数"""
        self._total_pages = math.ceil(self._total_items / self._page_size)
        if self._total_pages < 1:
            self._total_pages = 1

        # 如果数据变少导致当前页码越界，自动修复
        if self._current_page > self._total_pages:
            self._current_page = 1

    def _on_button_clicked(self, button):
        """处理UI点击事件"""
        val = button.property("page_num")

        new_page = self._current_page

        if val == "prev":
            new_page -= 1
        elif val == "next":
            new_page += 1
        elif isinstance(val, int):
            new_page = val

        # 边界检查
        if new_page < 1: new_page = 1
        if new_page > self._total_pages: new_page = self._total_pages

        # 只有页码真正改变时才触发信号
        if new_page != self._current_page:
            self._current_page = new_page
            self._update_ui()
            self.pageChanged.emit(new_page)

    def _create_page_button(self, text, page_num, is_active=False):
        """工厂方法：创建数字按钮"""
        if is_active:
            # 当前页：使用实心主题色按钮
            btn = PrimaryPushButton(str(text), self)
        else:
            # 其他页：使用透明背景按钮
            btn = TransparentToolButton(str(text), self)

        btn.setFixedSize(32, 32)
        btn.setProperty("page_num", page_num)

        self.hLayout.addWidget(btn)
        self.buttonGroup.addButton(btn)
        return btn

    def _create_icon_button(self, icon, page_action, enabled=True):
        """工厂方法：创建图标按钮 (上一页/下一页)"""
        btn = TransparentToolButton(icon, self)
        btn.setFixedSize(32, 32)
        btn.setProperty("page_num", page_action)
        btn.setEnabled(enabled)

        self.hLayout.addWidget(btn)
        self.buttonGroup.addButton(btn)
        return btn

    def _update_ui(self):
        """
        核心渲染逻辑：根据当前页和总页数，重绘所有按钮。
        实现了类似于 1 ... 4 5 6 ... 10 的省略号逻辑。
        """
        # 1. 清除旧组件
        for btn in self.buttonGroup.buttons():
            self.buttonGroup.removeButton(btn)

        while self.hLayout.count():
            item = self.hLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. 添加“上一页”按钮
        self._create_icon_button(FIF.LEFT_ARROW, "prev", enabled=(self._current_page > 1))

        # 3. 计算需要显示的页码集合
        pages_to_show = set()
        pages_to_show.add(1)  # 始终显示第一页
        pages_to_show.add(self._total_pages)  # 始终显示最后一页

        # 显示当前页的前后2页 (范围可调)
        range_start = max(1, self._current_page - 2)
        range_end = min(self._total_pages, self._current_page + 2)

        for i in range(range_start, range_end + 1):
            pages_to_show.add(i)

        sorted_pages = sorted(list(pages_to_show))

        # 4. 渲染数字按钮和省略号
        last_num = 0
        for page_num in sorted_pages:
            # 如果数字不连续，插入省略号 "..."
            if last_num != 0 and page_num - last_num > 1:
                dots = CaptionLabel("...", self)
                dots.setAlignment(Qt.AlignCenter)
                dots.setFixedWidth(20)
                self.hLayout.addWidget(dots)

            self._create_page_button(
                text=page_num,
                page_num=page_num,
                is_active=(page_num == self._current_page)
            )
            last_num = page_num

        # 5. 添加“下一页”按钮
        self._create_icon_button(FIF.RIGHT_ARROW, "next", enabled=(self._current_page < self._total_pages))
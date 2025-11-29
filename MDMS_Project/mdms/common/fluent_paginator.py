import math
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QButtonGroup
from qfluentwidgets import (CaptionLabel, TransparentToolButton,
                            PrimaryPushButton, FluentIcon as FIF,
                            TransparentPushButton)


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

        # === UI 布局 ===
        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 10, 0, 10)
        self.hLayout.setSpacing(5)
        self.hLayout.setAlignment(Qt.AlignCenter)

        # 按钮组 (用于管理按钮状态)
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.buttonClicked.connect(self._on_button_clicked)

        # 初始化绘制
        self._update_ui()

    def set_total_items(self, total: int):
        """设置数据总条数"""
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
        """代码主动设置当前页 (不触发信号)"""
        if page < 1: page = 1
        if page > self._total_pages: page = self._total_pages

        self._current_page = page
        self._update_ui()

    def _calculate_pages(self):
        """计算总页数"""
        self._total_pages = math.ceil(self._total_items / self._page_size)
        if self._total_pages < 1:
            self._total_pages = 1

        if self._current_page > self._total_pages:
            self._current_page = 1

    def _on_button_clicked(self, button):
        """处理点击事件"""
        val = button.property("page_num")

        new_page = self._current_page

        if val == "prev":
            new_page -= 1
        elif val == "next":
            new_page += 1
        elif isinstance(val, int):
            new_page = val

        if new_page < 1: new_page = 1
        if new_page > self._total_pages: new_page = self._total_pages

        if new_page != self._current_page:
            self._current_page = new_page
            self._update_ui()
            self.pageChanged.emit(new_page)

    def _create_page_button(self, text, page_num, is_active=False):
        """创建数字按钮"""
        if is_active:
            btn = PrimaryPushButton(str(text), self)
        else:
            # 使用 TransparentPushButton 以显示数字文本
            btn = TransparentPushButton(str(text), self)

        # [修改] 增加宽度到 40px，以容纳两位数或三位数
        btn.setFixedSize(40, 32)
        btn.setProperty("page_num", page_num)

        self.hLayout.addWidget(btn)
        self.buttonGroup.addButton(btn)
        return btn

    def _create_icon_button(self, icon, page_action, enabled=True):
        """创建图标按钮"""
        btn = TransparentToolButton(icon, self)
        # [修改] 保持与数字按钮尺寸一致
        btn.setFixedSize(40, 32)
        btn.setProperty("page_num", page_action)
        btn.setEnabled(enabled)

        self.hLayout.addWidget(btn)
        self.buttonGroup.addButton(btn)
        return btn

    def _update_ui(self):
        """
        核心渲染逻辑：重构为滑动窗口模式
        """
        # 1. 清理旧组件
        for btn in self.buttonGroup.buttons():
            self.buttonGroup.removeButton(btn)

        while self.hLayout.count():
            item = self.hLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. 上一页
        self._create_icon_button(FIF.LEFT_ARROW, "prev", enabled=(self._current_page > 1))

        # 3. 计算需要显示的页码列表 (0 代表省略号)
        page_nums = []
        total = self._total_pages
        curr = self._current_page

        # 逻辑：最多显示 7 个数字位 (不含上一页/下一页)
        if total <= 7:
            # 页数很少，全部显示: 1 2 3 4 5 6 7
            page_nums = list(range(1, total + 1))
        else:
            if curr <= 4:
                # 当前页靠前: 1 2 3 4 5 ... 100
                # 显示前5个 + 省略号 + 最后一个
                page_nums = [1, 2, 3, 4, 5, 0, total]
            elif curr >= total - 3:
                # 当前页靠后: 1 ... 96 97 98 99 100
                # 显示第1个 + 省略号 + 后5个
                page_nums = [1, 0, total - 4, total - 3, total - 2, total - 1, total]
            else:
                # 当前页在中间: 1 ... 4 5 6 ... 100
                # 显示第1个 + 省略号 + 中间3个(curr-1, curr, curr+1) + 省略号 + 最后一个
                page_nums = [1, 0, curr - 1, curr, curr + 1, 0, total]

        # 4. 渲染按钮
        for num in page_nums:
            if num == 0:
                # 渲染省略号
                dots = CaptionLabel("...", self)
                dots.setAlignment(Qt.AlignCenter)
                dots.setFixedWidth(20)
                self.hLayout.addWidget(dots)
            else:
                # 渲染数字
                self._create_page_button(
                    text=num,
                    page_num=num,
                    is_active=(num == self._current_page)
                )

        # 5. 下一页
        self._create_icon_button(FIF.RIGHT_ARROW, "next", enabled=(self._current_page < self._total_pages))
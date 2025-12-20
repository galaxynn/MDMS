from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QDate
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, LineEdit, BodyLabel,
    InfoBarIcon, Flyout, FlyoutAnimationType, DateEdit,
    SpinBox, TextEdit, ScrollArea
)
from datetime import datetime


class MovieFormDialog(MessageBoxBase):
    """新增/编辑电影表单对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_data = {}
        self.is_edit_mode = False

        # 设置对话框标题
        self.titleLabel = SubtitleLabel('新增电影', self)

        # 创建带滚动的表单区域
        self.setup_scroll_form()

        # 设置按钮
        self.yesButton.setText('保存')
        self.cancelButton.setText('取消')

        # 设置对话框尺寸 - 固定大小
        self.widget.setFixedSize(500, 600)

    def setup_scroll_form(self):
        """设置带滚动的表单区域"""
        scroll_area = ScrollArea()
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)

        # 设置滚动区域属性
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        # 设置滚动区域高度，留出空间给标题和底部按钮
        scroll_area.setFixedHeight(450)

        # 创建表单控件
        self.setup_form_controls()

        # 将滚动区域添加到主布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(scroll_area)

    def setup_form_controls(self):
        """设置表单控件"""
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        # 电影标题
        self.scroll_layout.addWidget(BodyLabel("电影标题 *"))
        self.titleLineEdit = LineEdit()
        self.titleLineEdit.setPlaceholderText('请输入电影标题')
        self.titleLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.titleLineEdit)

        # 上映日期
        self.scroll_layout.addWidget(BodyLabel("上映日期"))
        self.releaseDateEdit = DateEdit()
        self.releaseDateEdit.setDisplayFormat('yyyy-MM-dd')
        self.releaseDateEdit.setDate(datetime.now().date())  # 默认为今天
        self.scroll_layout.addWidget(self.releaseDateEdit)

        # 片长（分钟）
        self.scroll_layout.addWidget(BodyLabel("片长（分钟）"))
        self.runtimeSpinBox = SpinBox()
        self.runtimeSpinBox.setRange(1, 999)
        self.runtimeSpinBox.setSuffix(' 分钟')
        self.runtimeSpinBox.setValue(120)  # 默认值
        self.scroll_layout.addWidget(self.runtimeSpinBox)

        # 国家
        self.scroll_layout.addWidget(BodyLabel("国家"))
        self.countryLineEdit = LineEdit()
        self.countryLineEdit.setPlaceholderText('请输入国家（可选）')
        self.countryLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.countryLineEdit)

        # 语言
        self.scroll_layout.addWidget(BodyLabel("语言"))
        self.languageLineEdit = LineEdit()
        self.languageLineEdit.setPlaceholderText('请输入语言（可选）')
        self.languageLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.languageLineEdit)

        # 平均评分 (通常由计算得出，但如果需要手动修正可解开注释)
        # self.scroll_layout.addWidget(BodyLabel("当前评分"))
        # self.ratingLineEdit = LineEdit()
        # self.ratingLineEdit.setPlaceholderText('0.00')
        # self.ratingLineEdit.setEnabled(False) # 设为只读
        # self.scroll_layout.addWidget(self.ratingLineEdit)

        # 剧情简介
        self.scroll_layout.addWidget(BodyLabel("剧情简介"))
        self.synopsisTextEdit = TextEdit()
        self.synopsisTextEdit.setPlaceholderText('请输入剧情简介（可选）')
        self.synopsisTextEdit.setMinimumHeight(80)
        self.synopsisTextEdit.setMaximumHeight(120)
        self.scroll_layout.addWidget(self.synopsisTextEdit)

        # 海报URL
        self.scroll_layout.addWidget(BodyLabel("海报URL"))
        self.posterUrlLineEdit = LineEdit()
        self.posterUrlLineEdit.setPlaceholderText('请输入海报URL（可选）')
        self.posterUrlLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.posterUrlLineEdit)

        # 添加弹性空间
        self.scroll_layout.addStretch(1)

        # 绑定回车键
        self.posterUrlLineEdit.returnPressed.connect(self.yesButton.click)

    def set_form_data(self, data: dict):
        """
        设置表单初始数据（用于编辑模式）
        :param data: 包含电影信息的字典 (通常来自 TableWidget)
        """
        self.is_edit_mode = True
        self.titleLabel.setText('编辑电影')

        # 文本字段直接赋值
        self.titleLineEdit.setText(data.get('title', ''))
        self.countryLineEdit.setText(data.get('country', ''))
        self.languageLineEdit.setText(data.get('language', ''))
        self.synopsisTextEdit.setText(data.get('synopsis', ''))
        self.posterUrlLineEdit.setText(data.get('poster_url', ''))

        # 数值处理
        try:
            runtime = int(float(data.get('runtime_minutes', '120')))
            self.runtimeSpinBox.setValue(runtime)
        except (ValueError, TypeError):
            self.runtimeSpinBox.setValue(120)

        # 日期处理 (从字符串 'YYYY-MM-DD' 转回 QDate)
        date_str = data.get('release_date', '')
        if date_str:
            qdate = QDate.fromString(date_str, 'yyyy-MM-dd')
            if qdate.isValid():
                self.releaseDateEdit.setDate(qdate)

    def validate(self):
        """验证表单数据"""
        title = self.titleLineEdit.text().strip()

        # 必填字段验证
        if not title:
            self.show_error("电影标题不能为空", self.titleLineEdit)
            return False

        # 收集表单数据
        self.form_data = {
            'title': title,
            'release_date': self.releaseDateEdit.date().toPython(),
            'runtime_minutes': self.runtimeSpinBox.value(),
            'country': self.countryLineEdit.text().strip() or None,
            'language': self.languageLineEdit.text().strip() or None,
            'synopsis': self.synopsisTextEdit.toPlainText().strip() or None,
            'poster_url': self.posterUrlLineEdit.text().strip() or None
        }

        return True

    def get_form_data(self):
        """获取验证后的表单数据"""
        return self.form_data

    def show_error(self, text, target):
        """显示错误提示气泡"""
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title='注意',
            content=text,
            target=target,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
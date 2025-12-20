from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QDate
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, LineEdit, BodyLabel,
    InfoBarIcon, Flyout, FlyoutAnimationType, DateEdit,
    TextEdit, ScrollArea
)
from datetime import datetime


class PersonFormDialog(MessageBoxBase):
    """新增/编辑人员表单对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_data = {}
        self.is_edit_mode = False

        # 设置对话框标题
        self.titleLabel = SubtitleLabel('新增人员', self)

        # 创建带滚动的表单区域
        self.setup_scroll_form()

        # 设置按钮
        self.yesButton.setText('保存')
        self.cancelButton.setText('取消')

        # 设置对话框尺寸
        self.widget.setFixedSize(450, 550)

    def setup_scroll_form(self):
        """设置带滚动的表单区域"""
        scroll_area = ScrollArea()
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)

        # 设置滚动区域属性
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)

        # 创建表单控件
        self.setup_form_controls()

        # 将滚动区域添加到主布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(scroll_area)

    def setup_form_controls(self):
        """设置表单控件"""
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        # 姓名
        self.scroll_layout.addWidget(BodyLabel("姓名 *"))
        self.nameLineEdit = LineEdit()
        self.nameLineEdit.setPlaceholderText('请输入姓名')
        self.nameLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.nameLineEdit)

        # 出生日期
        self.scroll_layout.addWidget(BodyLabel("出生日期"))
        self.birthdateEdit = DateEdit()
        self.birthdateEdit.setDisplayFormat('yyyy-MM-dd')
        self.birthdateEdit.setDate(datetime.now().date())
        self.scroll_layout.addWidget(self.birthdateEdit)

        # 简介
        self.scroll_layout.addWidget(BodyLabel("简介"))
        self.bioTextEdit = TextEdit()
        self.bioTextEdit.setPlaceholderText('请输入简介（可选）')
        self.bioTextEdit.setMinimumHeight(80)
        self.bioTextEdit.setMaximumHeight(150)
        self.scroll_layout.addWidget(self.bioTextEdit)

        # 照片URL
        self.scroll_layout.addWidget(BodyLabel("照片URL"))
        self.photoUrlLineEdit = LineEdit()
        self.photoUrlLineEdit.setPlaceholderText('请输入照片URL（可选）')
        self.photoUrlLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.photoUrlLineEdit)

        # 添加弹性空间
        self.scroll_layout.addStretch(1)

        # 绑定回车键事件
        self.photoUrlLineEdit.returnPressed.connect(self.yesButton.click)

    def set_form_data(self, data: dict):
        """
        设置表单初始数据（用于编辑模式）
        :param data: 包含人员信息的字典
        """
        self.is_edit_mode = True
        self.titleLabel.setText('编辑人员')

        # 填充文本
        self.nameLineEdit.setText(data.get('name', ''))
        self.bioTextEdit.setText(data.get('bio', ''))
        self.photoUrlLineEdit.setText(data.get('photo_url', ''))

        # 填充日期 (字符串 -> QDate)
        date_str = data.get('birthdate', '')
        if date_str:
            qdate = QDate.fromString(date_str, 'yyyy-MM-dd')
            if qdate.isValid():
                self.birthdateEdit.setDate(qdate)

    def validate(self):
        """验证表单数据"""
        name = self.nameLineEdit.text().strip()

        # 必填字段验证
        if not name:
            self.show_error("姓名不能为空", self.nameLineEdit)
            return False

        # 收集表单数据
        self.form_data = {
            'name': name,
            'birthdate': self.birthdateEdit.date().toPython(),
            'bio': self.bioTextEdit.toPlainText().strip() or None,
            'photo_url': self.photoUrlLineEdit.text().strip() or None
        }

        return True

    def get_form_data(self):
        """获取表单数据"""
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
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, LineEdit, BodyLabel,
    InfoBarIcon, Flyout, FlyoutAnimationType, DateEdit,
    TextEdit
)
from datetime import datetime


class PersonFormDialog(MessageBoxBase):
    """新增/编辑人员表单对话框 - 使用与注册对话框一致的风格"""

    def __init__(self, parent=None, person=None):
        super().__init__(parent)
        self.person = person
        self.form_data = None

        # 设置对话框标题
        self.titleLabel = SubtitleLabel('新增人员' if not person else '编辑人员', self)

        # 创建表单控件
        self.setup_form_controls()

        # 设置布局
        self.setup_layout()

        # 设置按钮
        self.yesButton.setText('保存')
        self.cancelButton.setText('取消')

        # 设置对话框尺寸
        self.widget.setMinimumWidth(400)

    def setup_form_controls(self):
        """设置表单控件"""
        # 姓名
        self.nameLineEdit = LineEdit(self)
        self.nameLineEdit.setPlaceholderText('请输入姓名')
        self.nameLineEdit.setClearButtonEnabled(True)
        if self.person:
            self.nameLineEdit.setText(self.person.name)

        # 出生日期
        self.birthdateEdit = DateEdit(self)
        self.birthdateEdit.setDisplayFormat('yyyy-MM-dd')
        if self.person and self.person.birthdate:
            self.birthdateEdit.setDate(self.person.birthdate)
        else:
            self.birthdateEdit.setDate(datetime.now().date())

        # 简介
        self.bioTextEdit = TextEdit(self)
        self.bioTextEdit.setPlaceholderText('请输入简介（可选）')
        self.bioTextEdit.setMaximumHeight(100)
        if self.person:
            self.bioTextEdit.setText(self.person.bio or '')

        # 照片URL
        self.photoUrlLineEdit = LineEdit(self)
        self.photoUrlLineEdit.setPlaceholderText('请输入照片URL（可选）')
        self.photoUrlLineEdit.setClearButtonEnabled(True)
        if self.person:
            self.photoUrlLineEdit.setText(self.person.photo_url or '')

    def setup_layout(self):
        """设置布局"""
        self.viewLayout.addWidget(self.titleLabel)

        # 姓名
        self.viewLayout.addWidget(BodyLabel("姓名 *"))
        self.viewLayout.addWidget(self.nameLineEdit)

        # 出生日期
        self.viewLayout.addWidget(BodyLabel("出生日期"))
        self.viewLayout.addWidget(self.birthdateEdit)

        # 简介
        self.viewLayout.addWidget(BodyLabel("简介"))
        self.viewLayout.addWidget(self.bioTextEdit)

        # 照片URL
        self.viewLayout.addWidget(BodyLabel("照片URL"))
        self.viewLayout.addWidget(self.photoUrlLineEdit)

        # 绑定回车键事件
        self.photoUrlLineEdit.returnPressed.connect(self.yesButton.click)

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
        """获取表单数据（兼容原有代码）"""
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
from PySide6.QtWidgets import QVBoxLayout, QWidget, QCompleter
from PySide6.QtCore import Qt
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, LineEdit, BodyLabel,
    InfoBarIcon, Flyout, FlyoutAnimationType, ScrollArea,
    ComboBox
)


class UserFormDialog(MessageBoxBase):
    """新增/编辑用户表单对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_data = {}
        self.is_edit_mode = False

        # 设置对话框标题
        self.titleLabel = SubtitleLabel('新增用户', self)

        # 创建带滚动的表单区域
        self.setup_scroll_form()

        # 设置按钮
        self.yesButton.setText('保存')
        self.cancelButton.setText('取消')

        # 设置对话框尺寸
        self.widget.setFixedSize(450, 500)

    def setup_scroll_form(self):
        """设置带滚动的表单区域"""
        scroll_area = ScrollArea()
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)

        # 设置滚动区域属性
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        # 用户表单项较少，高度可以稍微设置小一点，或者自动适应
        scroll_area.setFixedHeight(350)

        # 创建表单控件
        self.setup_form_controls()

        # 将滚动区域添加到主布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(scroll_area)

    def setup_form_controls(self):
        """设置表单控件"""
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        # 用户名
        self.scroll_layout.addWidget(BodyLabel("用户名 *"))
        self.usernameLineEdit = LineEdit()
        self.usernameLineEdit.setPlaceholderText('请输入用户名')
        self.usernameLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.usernameLineEdit)

        # 邮箱
        self.scroll_layout.addWidget(BodyLabel("邮箱 *"))
        self.emailLineEdit = LineEdit()
        self.emailLineEdit.setPlaceholderText('请输入电子邮箱')
        self.emailLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.emailLineEdit)

        # 角色
        self.scroll_layout.addWidget(BodyLabel("角色 *"))
        self.roleComboBox = ComboBox()
        self.roleComboBox.addItems(['user', 'admin'])
        self.roleComboBox.setCurrentText('user')  # 默认为普通用户
        self.scroll_layout.addWidget(self.roleComboBox)

        # 密码
        self.passwordLabel = BodyLabel("密码 *")
        self.scroll_layout.addWidget(self.passwordLabel)

        self.passwordLineEdit = LineEdit()
        self.passwordLineEdit.setPlaceholderText('请输入密码')
        self.passwordLineEdit.setEchoMode(LineEdit.EchoMode.Password)
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.passwordLineEdit)

        # 确认密码 (仅简单的 UI 校验，可选)
        self.confirmPasswordLabel = BodyLabel("确认密码 *")
        self.scroll_layout.addWidget(self.confirmPasswordLabel)

        self.confirmPasswordLineEdit = LineEdit()
        self.confirmPasswordLineEdit.setPlaceholderText('请再次输入密码')
        self.confirmPasswordLineEdit.setEchoMode(LineEdit.EchoMode.Password)
        self.confirmPasswordLineEdit.setClearButtonEnabled(True)
        self.scroll_layout.addWidget(self.confirmPasswordLineEdit)

        # 添加弹性空间
        self.scroll_layout.addStretch(1)

        # 绑定回车键事件
        self.confirmPasswordLineEdit.returnPressed.connect(self.yesButton.click)

    def set_form_data(self, data: dict):
        """
        设置表单初始数据（用于编辑模式）
        :param data: 包含 username, email, role 的字典
        """
        self.is_edit_mode = True
        self.titleLabel.setText('编辑用户')

        # 填充数据
        self.usernameLineEdit.setText(data.get('username', ''))
        self.emailLineEdit.setText(data.get('email', ''))

        role = data.get('role', 'user')
        self.roleComboBox.setCurrentText(role)

        # 编辑模式下，密码为选填
        self.passwordLabel.setText("新密码 (留空保持不变)")
        self.passwordLineEdit.setPlaceholderText("若不修改密码请留空")

        self.confirmPasswordLabel.setText("确认新密码")
        self.confirmPasswordLineEdit.setPlaceholderText("若不修改密码请留空")

    def validate(self):
        """验证表单数据"""
        username = self.usernameLineEdit.text().strip()
        email = self.emailLineEdit.text().strip()
        role = self.roleComboBox.currentText()
        password = self.passwordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()

        # 1. 必填验证
        if not username:
            self.show_error("用户名不能为空", self.usernameLineEdit)
            return False

        if not email:
            self.show_error("邮箱不能为空", self.emailLineEdit)
            return False

        # 2. 密码逻辑验证
        if self.is_edit_mode:
            # 编辑模式：如果输入了密码，则必须验证一致性
            if password:
                if password != confirm_password:
                    self.show_error("两次输入的密码不一致", self.confirmPasswordLineEdit)
                    return False
        else:
            # 新增模式：密码必填
            if not password:
                self.show_error("初始密码不能为空", self.passwordLineEdit)
                return False
            if password != confirm_password:
                self.show_error("两次输入的密码不一致", self.confirmPasswordLineEdit)
                return False

        # 3. 收集数据
        self.form_data = {
            'username': username,
            'email': email,
            'role': role
        }

        # 只有在提供了密码时才加入数据字典
        if password:
            self.form_data['password'] = password

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
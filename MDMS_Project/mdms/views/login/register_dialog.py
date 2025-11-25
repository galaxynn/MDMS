import re

from qfluentwidgets import (MessageBoxBase, SubtitleLabel, LineEdit, PasswordLineEdit,
                            BodyLabel, InfoBarIcon, Flyout, FlyoutAnimationType, ComboBox)

from mdms.database.models import User
from mdms.database.session import SessionLocal


class RegisterDialog(MessageBoxBase):
    """ 自定义注册弹窗 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('注册新账户', self)

        # --- 用户名 ---
        self.usernameLineEdit = LineEdit(self)
        self.usernameLineEdit.setPlaceholderText('请输入用户名')
        self.usernameLineEdit.setClearButtonEnabled(True)

        # --- 邮箱 ---
        self.emailLineEdit = LineEdit(self)
        self.emailLineEdit.setPlaceholderText('请输入电子邮箱')
        self.emailLineEdit.setClearButtonEnabled(True)

        # --- 密码 ---
        self.passwordLineEdit = PasswordLineEdit(self)
        self.passwordLineEdit.setPlaceholderText('设置密码')

        self.confirmPasswordLineEdit = PasswordLineEdit(self)
        self.confirmPasswordLineEdit.setPlaceholderText('确认密码')

        # --- 用户角色选择 ---
        self.roleComboBox = ComboBox(self)
        self.roleComboBox.addItems(['普通用户', '管理员'])
        self.roleComboBox.setCurrentIndex(0)  # 默认选择普通用户
        self.roleComboBox.setToolTip('选择用户角色')

        # --- 布局设置 ---
        self.viewLayout.addWidget(self.titleLabel)

        self.viewLayout.addWidget(BodyLabel("用户名"))
        self.viewLayout.addWidget(self.usernameLineEdit)

        # 添加邮箱到布局
        self.viewLayout.addWidget(BodyLabel("邮箱"))
        self.viewLayout.addWidget(self.emailLineEdit)

        self.viewLayout.addWidget(BodyLabel("密码"))
        self.viewLayout.addWidget(self.passwordLineEdit)

        self.viewLayout.addWidget(BodyLabel("确认密码"))
        self.viewLayout.addWidget(self.confirmPasswordLineEdit)

        # 添加角色选择到布局
        self.viewLayout.addWidget(BodyLabel("用户角色"))
        self.viewLayout.addWidget(self.roleComboBox)

        # 设置按钮文字
        self.yesButton.setText('注册')
        self.cancelButton.setText('取消')

        # 设置最小宽度
        self.widget.setMinimumWidth(350)

        # 绑定输入回车事件到"注册"按钮的点击事件
        self.confirmPasswordLineEdit.returnPressed.connect(self.yesButton.click)
        self.passwordLineEdit.returnPressed.connect(self.yesButton.click)
        self.emailLineEdit.returnPressed.connect(self.yesButton.click)

    def validate(self):
        """ 重写验证逻辑，返回 True 则关闭弹窗，False 则保持开启 """
        username = self.usernameLineEdit.text().strip()
        email = self.emailLineEdit.text().strip()  # 获取邮箱
        password = self.passwordLineEdit.text().strip()
        confirm_pass = self.confirmPasswordLineEdit.text().strip()
        role = 'admin' if self.roleComboBox.currentText() == '管理员' else 'user'  # 获取角色

        # 1. 基础非空验证 (增加了 email)
        if not username or not password or not email:
            self.show_error("用户名、邮箱和密码不能为空", self.usernameLineEdit)
            return False

        # 2. 邮箱格式简单验证
        # 简单的正则检查，确保包含 @ 和 .
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            self.show_error("请输入有效的邮箱地址", self.emailLineEdit)
            return False

        # 3. 密码一致性验证
        if password != confirm_pass:
            self.show_error("两次输入的密码不一致", self.confirmPasswordLineEdit)
            return False

        # 4. 数据库验证与创建
        with SessionLocal() as session:
            # 4.1 检查用户名是否存在
            if session.query(User).filter_by(username=username).first():
                self.show_error("该用户名已被注册", self.usernameLineEdit)
                return False

            # 4.2 检查邮箱是否存在 (User模型要求 email 唯一)
            if session.query(User).filter_by(email=email).first():
                self.show_error("该邮箱已被注册", self.emailLineEdit)
                return False

            try:
                # 创建新用户 (传入 email 和 role)
                new_user = User(
                    username=username,
                    email=email,
                    role=role  # 设置用户角色
                )
                new_user.set_password(password)

                session.add(new_user)
                session.commit()
                return True  # 验证通过，关闭弹窗
            except Exception as e:
                session.rollback()
                # 打印详细错误以便调试
                print(f"Registration Error: {e}")
                self.show_error(f"注册失败: 数据库错误", self.yesButton)
                return False

    def show_error(self, text, target):
        """ 显示错误提示气泡 """
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title='注意',
            content=text,
            target=target,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
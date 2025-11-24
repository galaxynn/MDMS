from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTableWidgetItem
from PySide6.QtWidgets import QHeaderView
from qfluentwidgets import (
    PrimaryPushButton, TableWidget, MessageBox, InfoBar,
    InfoBarPosition
)

from mdms.database.models import User
from mdms.database.session import SessionLocal
from mdms.common.user_manager import user_manager


class UserManagementWidget(QFrame):
    """用户管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UserManagementWidget")
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        self.reset_password_button = PrimaryPushButton('重置密码')
        self.reset_password_button.setFixedWidth(120)
        self.reset_password_button.clicked.connect(self.reset_password)
        self.delete_button = PrimaryPushButton('删除用户')
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_user)

        button_layout.addWidget(self.reset_password_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 用户表格
        self.user_table = TableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            'ID', '用户名', '邮箱', '角色', '注册时间'
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.user_table)

    def load_users(self):
        """加载用户数据"""
        try:
            db = SessionLocal()
            users = db.query(User).order_by(User.created_at).all()

            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(user.user_id))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.email))
                self.user_table.setItem(row, 3, QTableWidgetItem(user.role))
                self.user_table.setItem(row, 4, QTableWidgetItem(
                    user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else ''
                ))

            db.close()
        except Exception as e:
            self.show_error(f"加载用户数据失败: {str(e)}")

    def reset_password(self):
        """重置用户密码"""
        current_row = self.user_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要重置密码的用户")
            return

        user_id = self.user_table.item(current_row, 0).text()
        username = self.user_table.item(current_row, 1).text()

        # 防止重置当前登录用户的密码
        if user_id == user_manager.current_user.user_id:
            self.show_warning("不能重置当前登录用户的密码")
            return

        # 确认重置
        result = MessageBox(
            '确认重置密码',
            f'确定要将用户 "{username}" 的密码重置为 "123456" 吗？',
            self
        ).exec()

        if result:
            try:
                db = SessionLocal()
                user = db.query(User).filter(User.user_id == user_id).first()
                if user:
                    user.set_password("123456")  # 默认密码
                    db.commit()

                db.close()
                self.show_success(f"用户 {username} 的密码已重置为 123456")

            except Exception as e:
                self.show_error(f"重置密码失败: {str(e)}")

    def delete_user(self):
        """删除选中的用户"""
        current_row = self.user_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要删除的用户")
            return

        user_id = self.user_table.item(current_row, 0).text()
        username = self.user_table.item(current_row, 1).text()

        # 防止删除当前登录用户
        if user_id == user_manager.current_user.user_id:
            self.show_warning("不能删除当前登录的用户")
            return

        # 确认删除
        result = MessageBox(
            '确认删除',
            f'确定要删除用户 "{username}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                db = SessionLocal()
                user = db.query(User).filter(User.user_id == user_id).first()
                if user:
                    db.delete(user)
                    db.commit()

                db.close()
                self.load_users()
                self.show_success("用户删除成功")

            except Exception as e:
                self.show_error(f"删除用户失败: {str(e)}")

    def show_success(self, message):
        """显示成功信息"""
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        """显示警告信息"""
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)
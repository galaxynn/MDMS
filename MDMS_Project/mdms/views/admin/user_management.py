from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from qfluentwidgets import (
    PrimaryPushButton, TableWidget, MessageBox, InfoBar,
    InfoBarPosition
)

from mdms.database.session import SessionLocal
from mdms.common.user_admin_manager import user_admin_manager
from mdms.common.user_manager import user_manager

# 假设你有一个 UserFormDialog 用于编辑用户信息（非仅密码）
# 如果没有，请参考 MovieFormDialog 创建一个
from mdms.views.admin.user_form_dialog import UserFormDialog


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

        # 新增：修改信息按钮
        self.edit_button = PrimaryPushButton('修改信息')
        self.edit_button.setFixedWidth(120)
        self.edit_button.clicked.connect(self.edit_user)

        self.delete_button = PrimaryPushButton('删除用户')
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_user)

        button_layout.addWidget(self.reset_password_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 用户表格
        self.user_table = TableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            'ID', '用户名', '邮箱', '角色', '注册时间'
        ])

        # 修复：PySide6 中 Stretch 枚举通常在 ResizeMode 下
        self.user_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.user_table)

    def load_users(self):
        """加载用户数据"""
        try:
            with SessionLocal() as session:
                users = user_admin_manager.get_all_users(session)

                self.user_table.setRowCount(len(users))
                for row, user in enumerate(users):
                    self.user_table.setItem(row, 0, QTableWidgetItem(str(user.user_id)))
                    self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
                    self.user_table.setItem(row, 2, QTableWidgetItem(user.email))
                    self.user_table.setItem(row, 3, QTableWidgetItem(user.role))
                    self.user_table.setItem(row, 4, QTableWidgetItem(
                        user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else ''
                    ))
        except Exception as e:
            self.show_error(f"加载用户数据失败: {str(e)}")

    def edit_user(self):
        """修改选中用户的信息（角色、邮箱等）"""
        current_row = self.user_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要修改的用户")
            return

        user_id = self.user_table.item(current_row, 0).text()

        # 构建回显数据
        initial_data = {
            'username': self.user_table.item(current_row, 1).text(),
            'email': self.user_table.item(current_row, 2).text(),
            'role': self.user_table.item(current_row, 3).text(),
        }

        # 打开弹窗
        try:
            dialog = UserFormDialog(self)

            # 需确保 UserFormDialog 有 set_form_data
            if hasattr(dialog, 'set_form_data'):
                dialog.set_form_data(initial_data)

            if dialog.exec():
                form_data = dialog.get_form_data()
                # 如果 UserFormDialog 返回了 password 字段，update_user_info 会自动 hash

                with SessionLocal() as session:
                    user_admin_manager.update_user_info(session, user_id, form_data)
                    session.commit()

                self.load_users()
                self.show_success("用户信息修改成功")
        except NameError:
            self.show_error("未找到 UserFormDialog，请先实现用户编辑弹窗类")
        except Exception as e:
            self.show_error(f"修改失败: {str(e)}")

    def reset_password(self):
        """重置用户密码"""
        current_row = self.user_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要重置密码的用户")
            return

        user_id = self.user_table.item(current_row, 0).text()
        username = self.user_table.item(current_row, 1).text()

        # 防止重置当前登录用户的密码
        if user_id == str(user_manager.current_user.user_id):
            self.show_warning("不能重置当前登录用户的密码")
            return

        result = MessageBox(
            '确认重置密码',
            f'确定要将用户 "{username}" 的密码重置为 "123456" 吗？',
            self
        ).exec()

        if result:
            try:
                with SessionLocal() as session:
                    user_admin_manager.reset_password(session, user_id, "123456")
                    session.commit()

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
        if user_id == str(user_manager.current_user.user_id):
            self.show_warning("不能删除当前登录的用户")
            return

        result = MessageBox(
            '确认删除',
            f'确定要删除用户 "{username}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                with SessionLocal() as session:
                    success = user_admin_manager.delete_user(session, user_id)
                    if success:
                        session.commit()
                        self.load_users()
                        self.show_success("用户删除成功")
                    else:
                        self.show_error("删除失败：用户不存在")

            except Exception as e:
                self.show_error(f"删除用户失败: {str(e)}")

    def show_success(self, message):
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)
# mdms/views/setting_interface.py

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout
from qfluentwidgets import SubtitleLabel, setFont, PrimaryPushButton, MessageBox, InfoBar, InfoBarPosition
from mdms.common.user_manager import user_manager


class SettingInterface(QFrame):
    """设置界面"""

    # 定义退出登录信号
    logoutRequested = Signal()

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)

        # 标题
        self.titleLabel = SubtitleLabel('设置', self)
        setFont(self.titleLabel, 24)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        # 用户信息区域
        self.userInfoLabel = SubtitleLabel('', self)
        setFont(self.userInfoLabel, 16)

        # 退出登录按钮
        self.logoutButton = PrimaryPushButton('退出登录', self)
        self.logoutButton.clicked.connect(self.on_logout_clicked)

        # 添加组件到布局
        self.vBoxLayout.addSpacing(30)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(50)
        self.vBoxLayout.addWidget(self.userInfoLabel)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.logoutButton)
        self.vBoxLayout.addStretch(1)

        # 更新用户信息显示
        self.update_user_info()

    def update_user_info(self):
        """更新用户信息显示"""
        if user_manager.is_logged_in:
            user = user_manager.current_user
            role_display = "管理员" if user.role == 'admin' else "普通用户"
            self.userInfoLabel.setText(f"当前用户: {user.username}\n用户角色: {role_display}")
            self.logoutButton.setEnabled(True)
        else:
            self.userInfoLabel.setText("未登录")
            self.logoutButton.setEnabled(False)

    def on_logout_clicked(self):
        """处理退出登录按钮点击"""
        if not user_manager.is_logged_in:
            return

        # 创建确认对话框
        title = '确认退出登录'
        content = f'确定要退出当前用户 ({user_manager.current_user.username}) 的登录状态吗？'
        w = MessageBox(title, content, self.window())

        if w.exec():
            # 用户确认退出登录
            user_manager.logout()

            # 显示退出成功提示
            InfoBar.success(
                title='退出登录成功',
                content='您已成功退出登录',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

            # 发射退出登录信号
            self.logoutRequested.emit()
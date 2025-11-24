# mdms/views/setting_interface.py

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QSizePolicy
from qfluentwidgets import (
    SmoothScrollArea,
    SettingCardGroup,
    PrimaryPushSettingCard,
    SettingCard,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    MessageBox,
    TitleLabel,
    ExpandLayout
)

from mdms.common.user_manager import user_manager


class SettingInterface(SmoothScrollArea):
    """
    设置界面 - 美化版
    采用 Windows 11 标准设置页风格
    """

    # 定义退出登录信号
    logoutRequested = Signal()

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        # 1. 基础设置
        self.setWidgetResizable(True)
        self.setStyleSheet("background-color: transparent;")

        # 2. 滚动区域的内容容器
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.scrollWidget.setStyleSheet("background-color: transparent;")
        self.setWidget(self.scrollWidget)

        # 3. 使用 ExpandLayout
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # --- 标题 ---
        self.settingLabel = TitleLabel("设置", self.scrollWidget)
        self.expandLayout.addWidget(self.settingLabel)

        # --- 账户组 ---
        self.accountGroup = SettingCardGroup("当前账户", self.scrollWidget)

        # 4. 用户信息卡片 (只读展示)
        self.profileCard = SettingCard(
            FluentIcon.PEOPLE,  # 图标
            "未登录",  # 标题 (用户名)
            "请先登录系统",  # 内容 (角色描述)
            self.accountGroup
        )

        # 5. 退出登录卡片 (带按钮的操作卡片)
        self.logoutCard = PrimaryPushSettingCard(
            "退出登录",  # 按钮文字
            FluentIcon.POWER_BUTTON,  # 左侧图标
            "账户操作",  # 卡片标题
            "退出当前账户并返回登录界面",  # 卡片说明
            self.accountGroup
        )
        self.logoutCard.clicked.connect(self.on_logout_clicked)

        # 将卡片添加到组中
        self.accountGroup.addSettingCard(self.profileCard)
        self.accountGroup.addSettingCard(self.logoutCard)

        # 将组添加到主布局
        self.expandLayout.addWidget(self.accountGroup)

        # --- 占位符 (替代 addStretch) ---
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.expandLayout.addWidget(self.spacer)

        # 初始化数据
        self.update_user_info()

    def update_user_info(self):
        """更新用户信息显示"""
        if user_manager.is_logged_in:
            user = user_manager.current_user
            role_display = "系统管理员" if user.role == 'admin' else "普通用户"

            # 更新 ProfileCard 的信息
            self.profileCard.setTitle(user.username)
            self.profileCard.setContent(f"角色权限: {role_display}")

            # 设置为可用状态
            self.logoutCard.setEnabled(True)

            # --- 修正点：通过 .button 访问内部按钮 ---
            self.logoutCard.button.setText("退出登录")
        else:
            self.profileCard.setTitle("未登录")
            self.profileCard.setContent("访客模式")

            # 设置为禁用状态
            self.logoutCard.setEnabled(False)

            # --- 修正点：通过 .button 访问内部按钮 ---
            self.logoutCard.button.setText("需登录")

    def on_logout_clicked(self):
        """处理退出登录按钮点击"""
        if not user_manager.is_logged_in:
            return

        # 创建确认对话框
        w = MessageBox(
            '确认退出',
            f'确定要退出当前用户 ({user_manager.current_user.username}) 吗？',
            self.window()
        )
        w.yesButton.setText('退出')
        w.cancelButton.setText('取消')

        if w.exec():
            # 用户确认退出登录
            user_manager.logout()

            # 显示退出成功提示
            InfoBar.success(
                title='已退出',
                content='您已成功安全退出系统',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self.window()
            )

            # 发射退出登录信号
            self.logoutRequested.emit()

            # 更新界面状态
            self.update_user_info()
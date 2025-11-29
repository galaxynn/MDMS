import sys

from PySide6.QtCore import Qt, QLocale, QRect, Signal, QSettings, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator, SplitTitleBar, isDarkTheme, Flyout, \
    InfoBarIcon, FlyoutAnimationType, CheckBox

from mdms.common.user_manager import user_manager
from mdms.database.models import User
from mdms.database.session import SessionLocal
from mdms.views.login.Ui_LoginWindow import Ui_Form
from mdms.views.login.register_dialog import RegisterDialog


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


class LoginWindow(Window, Ui_Form):
    loginSuccess = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # setTheme(Theme.DARK)
        setThemeColor('#28afe9')

        # 初始化配置存储 (Organization, Application)
        self.settings = QSettings("MDMS_Dev", "MDMS_Client")

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.image_label.setScaledContents(False)
        self.setWindowTitle('MDMS - Login')
        self.setWindowIcon(QIcon(":/images/logo.png"))
        self.resize(1000, 650)

        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=isDarkTheme())
        if not isWin11():
            color = QColor(25, 33, 42) if isDarkTheme() else QColor(240, 244, 249)
            self.setStyleSheet(f"LoginWindow{{background: {color.name()}}}")

        if sys.platform == "darwin":
            self.setSystemTitleBarButtonVisible(True)
            self.titleBar.minBtn.hide()
            self.titleBar.maxBtn.hide()
            self.titleBar.closeBtn.hide()

        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white
            }
        """)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # --- 新增：动态添加“记住密码”复选框 ---
        self.setup_remember_checkbox()

        # --- 新增：初始化时加载上次登录信息 ---
        self.load_saved_credentials()

        self.login_button.clicked.connect(self.on_clicked_login)
        self.register_button.clicked.connect(self.show_register_dialog)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        pixmap = QPixmap(":/images/background.jpg").scaled(
            self.image_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

    def systemTitleBarRect(self, size):
        """ Returns the system title bar rect, only works for macOS """
        return QRect(size.width() - 75, 0, 75, size.height())

    def setup_remember_checkbox(self):
        """ 在界面上动态插入记住密码复选框 """
        self.remember_checkBox = CheckBox("记住密码", self)

        # 尝试将它插入到 admin_checkBox 所在的布局中
        # 通常生成的 UI 中，checkBox 会放在一个 Layout 里
        parent_widget = self.admin_checkBox.parentWidget()
        if parent_widget and parent_widget.layout():
            layout = parent_widget.layout()
            # 获取管理员复选框的位置
            idx = layout.indexOf(self.admin_checkBox)
            if idx >= 0:
                # 插入到管理员复选框之前，并添加一点间距
                layout.insertWidget(idx, self.remember_checkBox)
                layout.insertSpacing(idx + 1, 15)
        else:
            # 如果找不到布局，使用绝对定位兜底 (不推荐，但作为 fallback)
            self.remember_checkBox.move(self.admin_checkBox.x() - 100, self.admin_checkBox.y())

    def load_saved_credentials(self):
        """ 从 QSettings 加载保存的用户名和密码 """
        username = self.settings.value("login/username", "")
        # 密码存储为 Base64 以避免明文显示，注意这只是简单的混淆
        password_b64 = self.settings.value("login/password", "")
        is_remember = self.settings.value("login/remember", False, type=bool)

        self.username_LineEdit.setText(username)
        self.remember_checkBox.setChecked(is_remember)

        if is_remember and password_b64:
            try:
                # 解码 Base64 密码
                password = QByteArray.fromBase64(password_b64.encode()).data().decode()
                self.password_LineEdit.setText(password)
            except Exception:
                pass

    def save_credentials(self, username, password):
        """ 保存登录凭据 """
        self.settings.setValue("login/username", username)

        is_remember = self.remember_checkBox.isChecked()
        self.settings.setValue("login/remember", is_remember)

        if is_remember:
            # 简单的 Base64 编码保存
            pwd_b64 = QByteArray(password.encode()).toBase64().data().decode()
            self.settings.setValue("login/password", pwd_b64)
        else:
            # 如果未勾选记住密码，清除已保存的密码
            self.settings.remove("login/password")

    def on_clicked_login(self):
        username = self.username_LineEdit.text().strip()
        password = self.password_LineEdit.text().strip()
        if not username or not password:
            self.show_error_message("请输入用户名和密码。", InfoBarIcon.WARNING)
            return

        with SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if user and user.check_password(password):
                # 检查管理员权限
                if self.admin_checkBox.isChecked() and user.role != 'admin':
                    self.show_error_message("该用户账号不是管理员，无法以管理员身份登录。", InfoBarIcon.WARNING)
                    return

                # 确定会话角色
                session_role = user.role
                if user.role == 'admin' and not self.admin_checkBox.isChecked():
                    session_role = 'user'

                # 登录成功
                user_manager.login(user, session_role)

                # --- 新增：保存账号密码 ---
                self.save_credentials(username, password)

                # 发射信号通知外部
                self.loginSuccess.emit()
            else:
                self.show_error_message("用户名或密码错误，请重试。", InfoBarIcon.ERROR)
                pass

    def show_error_message(self, message, icon):
        Flyout.create(
            icon=icon,
            title='出现问题',
            content=message,
            target=self.login_button,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def show_register_dialog(self):
        w = RegisterDialog(self)
        if w.exec():
            Flyout.create(
                icon=InfoBarIcon.SUCCESS,
                title='注册成功',
                content='账户创建成功，请登录。',
                target=self.login_button,
                parent=self,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)

    w = LoginWindow()
    w.show()
    app.exec()
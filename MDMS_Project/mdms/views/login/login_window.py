import sys

from PySide6.QtCore import Qt, QLocale, QRect, Signal
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator, SplitTitleBar, isDarkTheme, Flyout, \
    InfoBarIcon, FlyoutAnimationType

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
                # 如果是管理员账号但没有勾选管理员登录，则以普通用户身份登录
                session_role = user.role
                if user.role == 'admin' and not self.admin_checkBox.isChecked():
                    session_role = 'user'

                # 登录成功
                user_manager.login(user, session_role)

                # 发射信号通知外部
                self.loginSuccess.emit()

                # 注意：这里不再关闭窗口，由应用程序控制器处理
            else:
                # 显示错误信息
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
            # 注册成功后的回调
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
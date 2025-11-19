# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LoginWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

from qfluentwidgets import (BodyLabel, CheckBox, HyperlinkButton, LineEdit,
    PrimaryPushButton)
import mdms.views.login.resource_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1203, 809)
        Form.setMinimumSize(QSize(700, 500))
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel(Form)
        self.image_label.setObjectName(u"image_label")
        self.image_label.setPixmap(QPixmap(u":/images/background.jpg"))
        self.image_label.setScaledContents(True)

        self.horizontalLayout.addWidget(self.image_label)

        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QSize(360, 0))
        self.widget.setMaximumSize(QSize(360, 16777215))
        self.widget.setStyleSheet(u"QLabel{\n"
"	font: 13px 'Microsoft YaHei'\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(9)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.logo_label = QLabel(self.widget)
        self.logo_label.setObjectName(u"logo_label")
        self.logo_label.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.logo_label.sizePolicy().hasHeightForWidth())
        self.logo_label.setSizePolicy(sizePolicy1)
        self.logo_label.setMinimumSize(QSize(100, 100))
        self.logo_label.setMaximumSize(QSize(100, 100))
        self.logo_label.setPixmap(QPixmap(u":/images/logo.png"))
        self.logo_label.setScaledContents(True)

        self.verticalLayout_2.addWidget(self.logo_label, 0, Qt.AlignHCenter)

        self.verticalSpacer_3 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(9)

        self.verticalLayout_2.addLayout(self.gridLayout)

        self.username_label = BodyLabel(self.widget)
        self.username_label.setObjectName(u"username_label")

        self.verticalLayout_2.addWidget(self.username_label)

        self.username_LineEdit = LineEdit(self.widget)
        self.username_LineEdit.setObjectName(u"username_LineEdit")
        self.username_LineEdit.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.username_LineEdit)

        self.password_label = BodyLabel(self.widget)
        self.password_label.setObjectName(u"password_label")

        self.verticalLayout_2.addWidget(self.password_label)

        self.password_LineEdit = LineEdit(self.widget)
        self.password_LineEdit.setObjectName(u"password_LineEdit")
        self.password_LineEdit.setEchoMode(QLineEdit.Password)
        self.password_LineEdit.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.password_LineEdit)

        self.verticalSpacer_5 = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_5)

        self.admin_checkBox = CheckBox(self.widget)
        self.admin_checkBox.setObjectName(u"admin_checkBox")
        self.admin_checkBox.setChecked(False)

        self.verticalLayout_2.addWidget(self.admin_checkBox)

        self.verticalSpacer_4 = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.login_button = PrimaryPushButton(self.widget)
        self.login_button.setObjectName(u"login_button")

        self.verticalLayout_2.addWidget(self.login_button)

        self.verticalSpacer_6 = QSpacerItem(20, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_6)

        self.register_button = HyperlinkButton(self.widget)
        self.register_button.setObjectName(u"register_button")

        self.verticalLayout_2.addWidget(self.register_button)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addWidget(self.widget)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.image_label.setText("")
        self.logo_label.setText("")
        self.username_label.setText(QCoreApplication.translate("Form", u"\u7528\u6237\u540d", None))
        self.username_LineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u8bf7\u8f93\u5165\u7528\u6237\u540d", None))
        self.password_label.setText(QCoreApplication.translate("Form", u"\u5bc6\u7801", None))
        self.password_LineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u8bf7\u8f93\u5165\u5bc6\u7801", None))
        self.admin_checkBox.setText(QCoreApplication.translate("Form", u"\u7ba1\u7406\u5458\u767b\u5f55", None))
        self.login_button.setText(QCoreApplication.translate("Form", u"\u767b\u5f55", None))
        self.register_button.setText(QCoreApplication.translate("Form", u"\u6ce8\u518c", None))
    # retranslateUi


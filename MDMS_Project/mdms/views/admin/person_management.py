from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTableWidgetItem
from PySide6.QtWidgets import QHeaderView
from qfluentwidgets import (
    PrimaryPushButton, TableWidget, MessageBox, InfoBar,
    InfoBarPosition
)

from mdms.database.models import Person
from mdms.database.session import SessionLocal
from mdms.views.admin.person_form_dialog import PersonFormDialog


class PersonManagementWidget(QFrame):
    """人员管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PersonManagementWidget")
        self.setup_ui()
        self.load_people()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        self.add_button = PrimaryPushButton('新增人员')
        self.add_button.setFixedWidth(120)
        self.add_button.clicked.connect(self.add_person)
        self.delete_button = PrimaryPushButton('删除选中')
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_person)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 人员表格
        self.person_table = TableWidget()
        self.person_table.setColumnCount(4)
        self.person_table.setHorizontalHeaderLabels([
            'ID', '姓名', '出生日期', '简介'
        ])
        self.person_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.person_table)

    def load_people(self):
        """加载人员数据"""
        try:
            db = SessionLocal()
            people = db.query(Person).order_by(Person.name).all()

            self.person_table.setRowCount(len(people))
            for row, person in enumerate(people):
                self.person_table.setItem(row, 0, QTableWidgetItem(person.person_id))
                self.person_table.setItem(row, 1, QTableWidgetItem(person.name))
                self.person_table.setItem(row, 2, QTableWidgetItem(
                    person.birthdate.strftime('%Y-%m-%d') if person.birthdate else ''
                ))
                self.person_table.setItem(row, 3, QTableWidgetItem(
                    (person.bio[:100] + '...') if person.bio and len(person.bio) > 100 else (person.bio or '')
                ))

            db.close()
        except Exception as e:
            self.show_error(f"加载人员数据失败: {str(e)}")

    def add_person(self):
        """新增人员"""
        dialog = PersonFormDialog(self)
        if dialog.exec():
            try:
                form_data = dialog.get_form_data()
                db = SessionLocal()

                person = Person(**form_data)
                db.add(person)
                db.commit()

                db.close()
                self.load_people()
                self.show_success("人员添加成功")

            except Exception as e:
                self.show_error(f"添加人员失败: {str(e)}")

    def delete_person(self):
        """删除选中的人员"""
        current_row = self.person_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要删除的人员")
            return

        person_id = self.person_table.item(current_row, 0).text()
        person_name = self.person_table.item(current_row, 1).text()

        # 确认删除
        result = MessageBox(
            '确认删除',
            f'确定要删除人员 "{person_name}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                db = SessionLocal()
                person = db.query(Person).filter(Person.person_id == person_id).first()
                if person:
                    db.delete(person)
                    db.commit()

                db.close()
                self.load_people()
                self.show_success("人员删除成功")

            except Exception as e:
                self.show_error(f"删除人员失败: {str(e)}")

    def show_success(self, message):
        """显示成功信息"""
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        """显示警告信息"""
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)
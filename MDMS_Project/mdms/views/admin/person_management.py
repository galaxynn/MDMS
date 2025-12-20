from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from qfluentwidgets import (
    PrimaryPushButton, TableWidget, MessageBox, InfoBar,
    InfoBarPosition
)

from mdms.database.session import SessionLocal
from mdms.common.person_manager import person_manager
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

        # 新增：修改按钮
        self.edit_button = PrimaryPushButton('修改选中')
        self.edit_button.setFixedWidth(120)
        self.edit_button.clicked.connect(self.edit_person)

        self.delete_button = PrimaryPushButton('删除选中')
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_person)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 人员表格
        self.person_table = TableWidget()
        self.person_table.setColumnCount(4)
        self.person_table.setHorizontalHeaderLabels([
            'ID', '姓名', '出生日期', '简介'
        ])

        # 修复：PySide6 中 Stretch 枚举通常在 ResizeMode 下
        self.person_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.person_table)

    def load_people(self):
        """加载人员数据"""
        try:
            with SessionLocal() as session:
                people = person_manager.get_all_people(session)

                self.person_table.setRowCount(len(people))
                for row, person in enumerate(people):
                    self.person_table.setItem(row, 0, QTableWidgetItem(str(person.person_id)))
                    self.person_table.setItem(row, 1, QTableWidgetItem(person.name))
                    self.person_table.setItem(row, 2, QTableWidgetItem(
                        person.birthdate.strftime('%Y-%m-%d') if person.birthdate else ''
                    ))
                    # 简介只显示前100个字
                    self.person_table.setItem(row, 3, QTableWidgetItem(
                        (person.bio[:100] + '...') if person.bio and len(person.bio) > 100 else (person.bio or '')
                    ))
                    # 存储完整简介在 ToolTip 中，或者你可以在编辑时重新查询数据库
                    self.person_table.item(row, 3).setToolTip(person.bio or '')

        except Exception as e:
            self.show_error(f"加载人员数据失败: {str(e)}")

    def add_person(self):
        """新增人员"""
        dialog = PersonFormDialog(self)
        if dialog.exec():
            try:
                form_data = dialog.get_form_data()
                with SessionLocal() as session:
                    person_manager.add_person(session, form_data)
                    session.commit()
                self.load_people()
                self.show_success("人员添加成功")
            except Exception as e:
                self.show_error(f"添加人员失败: {str(e)}")

    def edit_person(self):
        """修改选中的人员"""
        current_row = self.person_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要修改的人员")
            return

        person_id = self.person_table.item(current_row, 0).text()

        # 构建初始数据。注意：表格里简介可能是截断的。
        # 最好在 update 逻辑里通过 ID 重新查一遍（可选），或者如果 ToolTip 里存了完整的就用 ToolTip
        full_bio = self.person_table.item(current_row, 3).toolTip()
        if not full_bio:  # 如果没有 tooltip，回退到表格文本
            full_bio = self.person_table.item(current_row, 3).text().replace('...', '')

        initial_data = {
            'name': self.person_table.item(current_row, 1).text(),
            'birthdate': self.person_table.item(current_row, 2).text(),
            'bio': full_bio
        }

        dialog = PersonFormDialog(self)

        # 需确保 PersonFormDialog 有 set_form_data
        if hasattr(dialog, 'set_form_data'):
            dialog.set_form_data(initial_data)

        if dialog.exec():
            try:
                form_data = dialog.get_form_data()
                with SessionLocal() as session:
                    person_manager.update_person(session, person_id, form_data)
                    session.commit()
                self.load_people()
                self.show_success("人员修改成功")
            except Exception as e:
                self.show_error(f"修改人员失败: {str(e)}")

    def delete_person(self):
        """删除选中的人员"""
        current_row = self.person_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要删除的人员")
            return

        person_id = self.person_table.item(current_row, 0).text()
        person_name = self.person_table.item(current_row, 1).text()

        result = MessageBox(
            '确认删除',
            f'确定要删除人员 "{person_name}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                with SessionLocal() as session:
                    success = person_manager.delete_person(session, person_id)
                    if success:
                        session.commit()
                        self.load_people()
                        self.show_success("人员删除成功")
                    else:
                        self.show_error("人员不存在或已被删除")
            except Exception as e:
                self.show_error(f"删除人员失败: {str(e)}")

    def show_success(self, message):
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)
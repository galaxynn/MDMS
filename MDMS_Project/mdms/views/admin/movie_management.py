from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from qfluentwidgets import (
    PrimaryPushButton, TableWidget, MessageBox, InfoBar,
    InfoBarPosition
)

# 引入数据库会话
from mdms.database.session import SessionLocal
# 引入 MovieManager
from mdms.common.movie_manager import movie_manager
from mdms.views.admin.movie_form_dialog import MovieFormDialog


class MovieManagementWidget(QFrame):
    """电影管理页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MovieManagementWidget")
        self.setup_ui()
        self.load_movies()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        self.add_button = PrimaryPushButton('新增电影')
        self.add_button.setFixedWidth(120)
        self.add_button.clicked.connect(self.add_movie)

        # 新增：修改按钮
        self.edit_button = PrimaryPushButton('修改选中')
        self.edit_button.setFixedWidth(120)
        self.edit_button.clicked.connect(self.edit_movie)

        self.delete_button = PrimaryPushButton('删除选中')
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_movie)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 电影表格
        self.movie_table = TableWidget()
        self.movie_table.setColumnCount(6)
        self.movie_table.setHorizontalHeaderLabels([
            'ID', '标题', '上映日期', '片长', '国家', '平均评分'
        ])

        # 修复：PySide6 中 Stretch 枚举通常在 ResizeMode 下
        self.movie_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.movie_table)

    def load_movies(self):
        """加载电影数据"""
        try:
            with SessionLocal() as session:
                movies = movie_manager.get_all_movies(session)

                self.movie_table.setRowCount(len(movies))
                for row, movie in enumerate(movies):
                    self.movie_table.setItem(row, 0, QTableWidgetItem(str(movie.movie_id)))
                    self.movie_table.setItem(row, 1, QTableWidgetItem(movie.title))
                    self.movie_table.setItem(row, 2, QTableWidgetItem(
                        movie.release_date.strftime('%Y-%m-%d') if movie.release_date else ''
                    ))
                    self.movie_table.setItem(row, 3, QTableWidgetItem(
                        str(movie.runtime_minutes) if movie.runtime_minutes else ''
                    ))
                    self.movie_table.setItem(row, 4, QTableWidgetItem(movie.country or ''))
                    self.movie_table.setItem(row, 5, QTableWidgetItem(
                        str(movie.average_rating) if movie.average_rating else '0.00'
                    ))
        except Exception as e:
            self.show_error(f"加载电影数据失败: {str(e)}")

    def add_movie(self):
        """新增电影"""
        dialog = MovieFormDialog(self)
        if dialog.exec():
            try:
                form_data = dialog.get_form_data()
                with SessionLocal() as session:
                    movie_manager.add_movie(session, form_data)
                    session.commit()
                self.load_movies()
                self.show_success("电影添加成功")
            except Exception as e:
                self.show_error(f"添加电影失败: {str(e)}")

    def edit_movie(self):
        """修改选中的电影"""
        current_row = self.movie_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要修改的电影")
            return

        # 1. 获取当前行数据
        movie_id = self.movie_table.item(current_row, 0).text()

        # 构建初始数据字典 (用于回显)
        initial_data = {
            'title': self.movie_table.item(current_row, 1).text(),
            'release_date': self.movie_table.item(current_row, 2).text(),
            'runtime_minutes': self.movie_table.item(current_row, 3).text(),
            'country': self.movie_table.item(current_row, 4).text(),
            'average_rating': self.movie_table.item(current_row, 5).text(),
        }

        # 2. 打开弹窗
        dialog = MovieFormDialog(self)

        # 注意：你需要确保 MovieFormDialog 有 set_form_data 方法来填充数据
        if hasattr(dialog, 'set_form_data'):
            dialog.set_form_data(initial_data)

        if dialog.exec():
            try:
                # 3. 获取修改后的数据
                form_data = dialog.get_form_data()

                with SessionLocal() as session:
                    # 调用上一轮增加的 update_movie
                    movie_manager.update_movie(session, movie_id, form_data)
                    session.commit()

                self.load_movies()
                self.show_success("电影修改成功")
            except Exception as e:
                self.show_error(f"修改电影失败: {str(e)}")

    def delete_movie(self):
        """删除选中的电影"""
        current_row = self.movie_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要删除的电影")
            return

        movie_id = self.movie_table.item(current_row, 0).text()
        movie_title = self.movie_table.item(current_row, 1).text()

        result = MessageBox(
            '确认删除',
            f'确定要删除电影 "{movie_title}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                with SessionLocal() as session:
                    success = movie_manager.delete_movie(session, movie_id)
                    if success:
                        session.commit()
                        self.load_movies()
                        self.show_success("电影删除成功")
                    else:
                        self.show_error("删除失败：电影可能已被删除")
            except Exception as e:
                self.show_error(f"删除电影失败: {str(e)}")

    def show_success(self, message):
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)
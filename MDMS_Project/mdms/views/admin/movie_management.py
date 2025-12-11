from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from qfluentwidgets import (
    PrimaryPushButton, TableWidget, MessageBox, InfoBar,
    InfoBarPosition
)

# 引入数据库会话
from mdms.database.session import SessionLocal
#  引入 MovieManager
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
        """设置界面 (保持不变)"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        self.add_button = PrimaryPushButton('新增电影')
        self.add_button.setFixedWidth(120)
        self.add_button.clicked.connect(self.add_movie)
        self.delete_button = PrimaryPushButton('删除选中')
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_movie)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 电影表格
        self.movie_table = TableWidget()
        self.movie_table.setColumnCount(6)
        self.movie_table.setHorizontalHeaderLabels([
            'ID', '标题', '上映日期', '片长', '国家', '平均评分'
        ])
        self.movie_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.movie_table)

    def load_movies(self):
        """加载电影数据"""
        try:
            # 使用 with 语法自动管理 session 关闭
            with SessionLocal() as session:
                # 调用 manager 获取数据
                movies = movie_manager.get_all_movies(session)

                self.movie_table.setRowCount(len(movies))
                for row, movie in enumerate(movies):
                    self.movie_table.setItem(row, 0, QTableWidgetItem(movie.movie_id))
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

                # 使用 manager 添加
                with SessionLocal() as session:
                    movie_manager.add_movie(session, form_data)
                    session.commit()  # 确认提交事务

                self.load_movies()
                self.show_success("电影添加成功")

            except Exception as e:
                self.show_error(f"添加电影失败: {str(e)}")

    def delete_movie(self):
        """删除选中的电影"""
        current_row = self.movie_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要删除的电影")
            return

        movie_id = self.movie_table.item(current_row, 0).text()
        movie_title = self.movie_table.item(current_row, 1).text()

        # 确认删除
        result = MessageBox(
            '确认删除',
            f'确定要删除电影 "{movie_title}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                # 使用 manager 删除
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
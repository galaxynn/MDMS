from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QStackedWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialog, QDialogButtonBox)
from qfluentwidgets import (Pivot, PrimaryPushButton, TableWidget, MessageBox,
                            setFont, InfoBar, InfoBarPosition, LineEdit, TextEdit,
                            DateEdit, SpinBox, BodyLabel, CardWidget, ScrollArea,
                            SubtitleLabel, Dialog)
from sqlalchemy.orm import Session
from datetime import datetime

# 导入模型和数据库会话
from mdms.database.models import Movie, Person, User, Genre, MoviePerson
from mdms.database.session import SessionLocal
from mdms.common.user_manager import user_manager


class MovieFormDialog(QDialog):
    """新增/编辑电影表单对话框 - 使用 QFluentWidgets 组件"""

    def __init__(self, parent=None, movie=None):
        super().__init__(parent)
        self.movie = movie
        self.setWindowTitle('新增电影' if not movie else '编辑电影')
        self.resize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        """设置表单界面"""
        layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll_area = ScrollArea()
        scroll_widget = QFrame()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 创建表单卡片
        form_card = CardWidget()
        form_layout = QVBoxLayout(form_card)

        # 电影标题
        title_label = BodyLabel('电影标题')
        self.title_edit = LineEdit()
        self.title_edit.setPlaceholderText('请输入电影标题')
        if self.movie:
            self.title_edit.setText(self.movie.title)
        form_layout.addWidget(title_label)
        form_layout.addWidget(self.title_edit)
        form_layout.addSpacing(10)

        # 上映日期
        release_date_label = BodyLabel('上映日期')
        self.release_date_edit = DateEdit()
        self.release_date_edit.setDisplayFormat('yyyy-MM-dd')
        if self.movie and self.movie.release_date:
            self.release_date_edit.setDate(self.movie.release_date)
        else:
            self.release_date_edit.setDate(datetime.now().date())
        form_layout.addWidget(release_date_label)
        form_layout.addWidget(self.release_date_edit)
        form_layout.addSpacing(10)

        # 片长（分钟）
        runtime_label = BodyLabel('片长（分钟）')
        self.runtime_edit = SpinBox()
        self.runtime_edit.setRange(1, 500)
        self.runtime_edit.setSuffix(' 分钟')
        if self.movie:
            self.runtime_edit.setValue(self.movie.runtime_minutes or 120)
        form_layout.addWidget(runtime_label)
        form_layout.addWidget(self.runtime_edit)
        form_layout.addSpacing(10)

        # 国家
        country_label = BodyLabel('国家')
        self.country_edit = LineEdit()
        self.country_edit.setPlaceholderText('请输入国家')
        if self.movie:
            self.country_edit.setText(self.movie.country or '')
        form_layout.addWidget(country_label)
        form_layout.addWidget(self.country_edit)
        form_layout.addSpacing(10)

        # 语言
        language_label = BodyLabel('语言')
        self.language_edit = LineEdit()
        self.language_edit.setPlaceholderText('请输入语言')
        if self.movie:
            self.language_edit.setText(self.movie.language or '')
        form_layout.addWidget(language_label)
        form_layout.addWidget(self.language_edit)
        form_layout.addSpacing(10)

        # 剧情简介
        synopsis_label = BodyLabel('剧情简介')
        self.synopsis_edit = TextEdit()
        self.synopsis_edit.setPlaceholderText('请输入剧情简介')
        self.synopsis_edit.setMaximumHeight(120)
        if self.movie:
            self.synopsis_edit.setText(self.movie.synopsis or '')
        form_layout.addWidget(synopsis_label)
        form_layout.addWidget(self.synopsis_edit)
        form_layout.addSpacing(10)

        # 海报URL
        poster_url_label = BodyLabel('海报URL')
        self.poster_url_edit = LineEdit()
        self.poster_url_edit.setPlaceholderText('请输入海报URL（可选）')
        if self.movie:
            self.poster_url_edit.setText(self.movie.poster_url or '')
        form_layout.addWidget(poster_url_label)
        form_layout.addWidget(self.poster_url_edit)

        # 将卡片添加到滚动布局
        scroll_layout.addWidget(form_card)
        scroll_layout.addStretch(1)

        # 设置滚动区域
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 添加到主布局
        layout.addWidget(scroll_area)
        layout.addWidget(button_box)

    def get_form_data(self):
        """获取表单数据"""
        return {
            'title': self.title_edit.text().strip(),
            'release_date': self.release_date_edit.date().toPython(),
            'runtime_minutes': self.runtime_edit.value(),
            'country': self.country_edit.text().strip() or None,
            'language': self.language_edit.text().strip() or None,
            'synopsis': self.synopsis_edit.toPlainText().strip() or None,
            'poster_url': self.poster_url_edit.text().strip() or None
        }


class PersonFormDialog(QDialog):
    """新增/编辑人员表单对话框 - 使用 QFluentWidgets 组件"""

    def __init__(self, parent=None, person=None):
        super().__init__(parent)
        self.person = person
        self.setWindowTitle('新增人员' if not person else '编辑人员')
        self.resize(500, 500)
        self.setup_ui()

    def setup_ui(self):
        """设置表单界面"""
        layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll_area = ScrollArea()
        scroll_widget = QFrame()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 创建表单卡片
        form_card = CardWidget()
        form_layout = QVBoxLayout(form_card)

        # 姓名
        name_label = BodyLabel('姓名')
        self.name_edit = LineEdit()
        self.name_edit.setPlaceholderText('请输入姓名')
        if self.person:
            self.name_edit.setText(self.person.name)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_edit)
        form_layout.addSpacing(10)

        # 出生日期
        birthdate_label = BodyLabel('出生日期')
        self.birthdate_edit = DateEdit()
        self.birthdate_edit.setDisplayFormat('yyyy-MM-dd')
        if self.person and self.person.birthdate:
            self.birthdate_edit.setDate(self.person.birthdate)
        else:
            self.birthdate_edit.setDate(datetime.now().date())
        form_layout.addWidget(birthdate_label)
        form_layout.addWidget(self.birthdate_edit)
        form_layout.addSpacing(10)

        # 简介
        bio_label = BodyLabel('简介')
        self.bio_edit = TextEdit()
        self.bio_edit.setPlaceholderText('请输入简介')
        self.bio_edit.setMaximumHeight(120)
        if self.person:
            self.bio_edit.setText(self.person.bio or '')
        form_layout.addWidget(bio_label)
        form_layout.addWidget(self.bio_edit)
        form_layout.addSpacing(10)

        # 照片URL
        photo_url_label = BodyLabel('照片URL')
        self.photo_url_edit = LineEdit()
        self.photo_url_edit.setPlaceholderText('请输入照片URL（可选）')
        if self.person:
            self.photo_url_edit.setText(self.person.photo_url or '')
        form_layout.addWidget(photo_url_label)
        form_layout.addWidget(self.photo_url_edit)

        # 将卡片添加到滚动布局
        scroll_layout.addWidget(form_card)
        scroll_layout.addStretch(1)

        # 设置滚动区域
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(350)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # 添加到主布局
        layout.addWidget(scroll_area)
        layout.addWidget(button_box)

    def get_form_data(self):
        """获取表单数据"""
        return {
            'name': self.name_edit.text().strip(),
            'birthdate': self.birthdate_edit.date().toPython(),
            'bio': self.bio_edit.toPlainText().strip() or None,
            'photo_url': self.photo_url_edit.text().strip() or None
        }


# 其余代码保持不变...
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
        self.add_button.setFixedWidth(120)  # 设置固定宽度
        self.add_button.clicked.connect(self.add_movie)
        self.delete_button = PrimaryPushButton('删除选中')
        self.delete_button.setFixedWidth(120)  # 设置固定宽度
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
            db = SessionLocal()
            movies = db.query(Movie).order_by(Movie.title).all()

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

            db.close()
        except Exception as e:
            self.show_error(f"加载电影数据失败: {str(e)}")

    def add_movie(self):
        """新增电影"""
        dialog = MovieFormDialog(self)
        if dialog.exec():
            try:
                form_data = dialog.get_form_data()
                db = SessionLocal()

                movie = Movie(**form_data)
                db.add(movie)
                db.commit()

                db.close()
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
                db = SessionLocal()
                movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
                if movie:
                    db.delete(movie)
                    db.commit()

                db.close()
                self.load_movies()
                self.show_success("电影删除成功")

            except Exception as e:
                self.show_error(f"删除电影失败: {str(e)}")

    def show_success(self, message):
        """显示成功信息"""
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        """显示警告信息"""
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)


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
        self.add_button.setFixedWidth(120)  # 设置固定宽度
        self.add_button.clicked.connect(self.add_person)
        self.delete_button = PrimaryPushButton('删除选中')
        self.delete_button.setFixedWidth(120)  # 设置固定宽度
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
        self.reset_password_button.setFixedWidth(120)  # 设置固定宽度
        self.reset_password_button.clicked.connect(self.reset_password)
        self.delete_button = PrimaryPushButton('删除用户')
        self.delete_button.setFixedWidth(120)  # 设置固定宽度
        self.delete_button.clicked.connect(self.delete_user)

        button_layout.addWidget(self.reset_password_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        # 用户表格
        self.user_table = TableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            'ID', '用户名', '邮箱', '角色', '注册时间'
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addLayout(button_layout)
        layout.addWidget(self.user_table)

    def load_users(self):
        """加载用户数据"""
        try:
            db = SessionLocal()
            users = db.query(User).order_by(User.created_at).all()

            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(user.user_id))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.email))
                self.user_table.setItem(row, 3, QTableWidgetItem(user.role))
                self.user_table.setItem(row, 4, QTableWidgetItem(
                    user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else ''
                ))

            db.close()
        except Exception as e:
            self.show_error(f"加载用户数据失败: {str(e)}")

    def reset_password(self):
        """重置用户密码"""
        current_row = self.user_table.currentRow()
        if current_row == -1:
            self.show_warning("请先选择要重置密码的用户")
            return

        user_id = self.user_table.item(current_row, 0).text()
        username = self.user_table.item(current_row, 1).text()

        # 防止重置当前登录用户的密码
        if user_id == user_manager.current_user.user_id:
            self.show_warning("不能重置当前登录用户的密码")
            return

        # 确认重置
        result = MessageBox(
            '确认重置密码',
            f'确定要将用户 "{username}" 的密码重置为 "123456" 吗？',
            self
        ).exec()

        if result:
            try:
                db = SessionLocal()
                user = db.query(User).filter(User.user_id == user_id).first()
                if user:
                    user.set_password("123456")  # 默认密码
                    db.commit()

                db.close()
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
        if user_id == user_manager.current_user.user_id:
            self.show_warning("不能删除当前登录的用户")
            return

        # 确认删除
        result = MessageBox(
            '确认删除',
            f'确定要删除用户 "{username}" 吗？此操作不可恢复！',
            self
        ).exec()

        if result:
            try:
                db = SessionLocal()
                user = db.query(User).filter(User.user_id == user_id).first()
                if user:
                    db.delete(user)
                    db.commit()

                db.close()
                self.load_users()
                self.show_success("用户删除成功")

            except Exception as e:
                self.show_error(f"删除用户失败: {str(e)}")

    def show_success(self, message):
        """显示成功信息"""
        InfoBar.success('成功', message, parent=self, duration=2000, position=InfoBarPosition.TOP)

    def show_warning(self, message):
        """显示警告信息"""
        InfoBar.warning('警告', message, parent=self, duration=3000, position=InfoBarPosition.TOP)

    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error('错误', message, parent=self, duration=4000, position=InfoBarPosition.TOP)


class AdminInterface(QFrame):
    """管理员界面"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.pivot = None
        self.stacked_widget = None
        # 设置 objectName，这是修复错误的关键
        self.setObjectName(text.replace(' ', '-'))
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 创建标签页
        self.pivot = Pivot(self)
        self.stacked_widget = QStackedWidget(self)

        # 创建三个管理页面
        self.movie_management = MovieManagementWidget()
        self.person_management = PersonManagementWidget()
        self.user_management = UserManagementWidget()

        # 添加页面到堆叠窗口
        self.stacked_widget.addWidget(self.movie_management)
        self.stacked_widget.addWidget(self.person_management)
        self.stacked_widget.addWidget(self.user_management)

        # 添加标签页
        self.pivot.addItem(
            routeKey='movie_management',
            text='电影管理',
            onClick=lambda: self.stacked_widget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey='person_management',
            text='人员管理',
            onClick=lambda: self.stacked_widget.setCurrentIndex(1)
        )
        self.pivot.addItem(
            routeKey='user_management',
            text='用户管理',
            onClick=lambda: self.stacked_widget.setCurrentIndex(2)
        )

        # 设置布局
        layout.addWidget(self.pivot)
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # 连接信号
        self.stacked_widget.currentChanged.connect(self.on_current_index_changed)
        self.stacked_widget.setCurrentIndex(0)
        self.pivot.setCurrentItem('movie_management')

    def on_current_index_changed(self, index):
        """当前页面改变时的处理"""
        self.pivot.setCurrentItem(list(self.pivot.items.keys())[index])
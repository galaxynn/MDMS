from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHeaderView, QWidget, QHBoxLayout,
                               QTableWidgetItem)
from qfluentwidgets import (SubtitleLabel, TableWidget, TransparentToolButton, FluentIcon, MessageBox,
                            MessageBoxBase, Slider, TextEdit, StrongBodyLabel,
                            BodyLabel)

from mdms.common.review_manager import review_manager
from mdms.common.user_manager import user_manager
from mdms.database.models import Review
from mdms.database.session import SessionLocal


# 编辑评论的弹窗类
class EditReviewDialog(MessageBoxBase):
    """ 编辑评论的弹窗 """

    def __init__(self, old_rating, old_content, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('修改影评', self)

        # 评分滑块
        self.ratingLabel = StrongBodyLabel(f"评分: {old_rating} / 10", self)
        self.ratingSlider = Slider(Qt.Horizontal, self)
        self.ratingSlider.setRange(1, 10)
        self.ratingSlider.setValue(old_rating)
        self.ratingSlider.valueChanged.connect(lambda v: self.ratingLabel.setText(f"评分: {v} / 10"))

        # 评论内容框
        self.contentLabel = BodyLabel("评论内容:", self)
        self.contentEdit = TextEdit(self)
        self.contentEdit.setPlainText(old_content)
        self.contentEdit.setFixedHeight(100)

        # 布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.ratingLabel)
        self.viewLayout.addWidget(self.ratingSlider)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.contentEdit)

        self.yesButton.setText("保存")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(400)

    def get_data(self):
        return self.ratingSlider.value(), self.contentEdit.toPlainText()


# 主界面类
class MyReviewInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)
        self.mainLayout.setSpacing(20)

        # 1. 标题
        self.titleLabel = SubtitleLabel("我的影评记录", self)
        self.mainLayout.addWidget(self.titleLabel)

        # 2. 表格初始化
        self.table = TableWidget(self)
        self.init_table()
        self.mainLayout.addWidget(self.table)

        # 3. 加载数据
        # 注意：在实际应用中，最好在界面显示时刷新数据 (override showEvent)
        self.load_reviews()

    def init_table(self):
        """ 配置表格列和样式 """
        # 设置列：ID(隐藏), 电影名, 评分, 评论内容, 时间, 操作
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', '电影名称', '评分', '评论内容', '发布时间', '操作'])

        # 隐藏 ID 列
        self.table.setColumnHidden(0, True)

        # 设置列宽模式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # 默认拉伸
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 电影名自适应
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 评分固定宽度
        self.table.setColumnWidth(2, 80)
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 操作列固定宽度
        self.table.setColumnWidth(5, 150)

        # 开启斑马纹
        self.table.setAlternatingRowColors(True)
        # 垂直表头隐藏
        self.table.verticalHeader().hide()

    def showEvent(self, event):
        """ 每次切换到这个界面时，自动刷新数据 """
        super().showEvent(event)
        self.load_reviews()

    def load_reviews(self):
        """ 从数据库读取当前用户的评论 """
        if not user_manager.is_logged_in:
            return

        self.table.setRowCount(0)  # 清空旧数据
        user_id = user_manager.current_user.user_id

        with SessionLocal() as session:
            # 查询 Review 并关联 Movie 表获取电影标题
            reviews = session.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()

            for review in reviews:
                # 获取电影标题 (处理关联可能为空的情况)
                movie_title = review.movie.title if review.movie else "未知电影"
                self.add_review_row(review, movie_title)

    def add_review_row(self, review, movie_title):
        """ 向表格添加一行数据 """
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        # 0. ID (Hidden)
        self.table.setItem(row_idx, 0, QTableWidgetItem(str(review.review_id)))

        # 1. Movie Title
        self.table.setItem(row_idx, 1, QTableWidgetItem(movie_title))

        # 2. Rating
        self.table.setItem(row_idx, 2, QTableWidgetItem(f"{review.rating} / 10"))

        # 3. Content
        # 截取过长的评论
        content_display = review.comment[:50] + "..." if len(review.comment) > 50 else review.comment
        item_content = QTableWidgetItem(content_display)
        item_content.setToolTip(review.comment)  # 鼠标悬停显示全文
        self.table.setItem(row_idx, 3, item_content)

        # 4. Time
        time_str = review.created_at.strftime("%Y-%m-%d %H:%M") if review.created_at else ""
        self.table.setItem(row_idx, 4, QTableWidgetItem(time_str))

        # 5. Operations (Buttons)
        self.setup_operation_buttons(row_idx, review)

    def setup_operation_buttons(self, row_idx, review):
        """ 在单元格中放置操作按钮 """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # 编辑按钮
        edit_btn = TransparentToolButton(FluentIcon.EDIT, self)
        edit_btn.setToolTip("修改影评")
        edit_btn.clicked.connect(lambda: self.on_edit_clicked(review.review_id))

        # 删除按钮
        delete_btn = TransparentToolButton(FluentIcon.DELETE, self)
        delete_btn.setToolTip("删除影评")
        # 设置红色样式提示危险操作
        # delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(lambda: self.on_delete_clicked(review.review_id))

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.setAlignment(Qt.AlignCenter)

        self.table.setCellWidget(row_idx, 5, widget)

    @Slot()
    def on_edit_clicked(self, review_id):
        """ 处理编辑逻辑 """
        # 开启 session
        with SessionLocal() as session:
            # 注意：这里最好重新查询获取对象，或者直接传 ID 给 manager
            # 为了获取弹窗初始值，先查一次
            review = session.query(Review).get(review_id)
            if not review:
                return

            dialog = EditReviewDialog(review.rating, review.comment, self)
            if dialog.exec():
                new_rating, new_content = dialog.get_data()

                try:
                    # 使用 Manager 进行更新
                    # 传入当前的 session，Manager 会处理更新逻辑和评分重算
                    review_manager.update_review(
                        session,
                        review_id,
                        new_rating,
                        new_content
                    )

                    # 提交事务
                    session.commit()

                    # 刷新界面
                    self.load_reviews()
                    self.show_success("修改成功")

                except Exception as e:
                    session.rollback()
                    print(f"Edit error: {e}")
                    # 可以加个 show_error_message

    @Slot()
    def on_delete_clicked(self, review_id):
        """ 处理删除逻辑 """
        w = MessageBox("确认删除", "确定要删除这条影评吗？此操作不可恢复。", self)
        w.yesButton.setText("删除")
        w.cancelButton.setText("取消")

        if w.exec():
            with SessionLocal() as session:
                try:
                    # 使用 Manager 进行删除
                    review_manager.delete_review(session, review_id)

                    session.commit()

                    self.load_reviews()
                    self.show_success("删除成功")
                except Exception as e:
                    session.rollback()
                    print(f"Delete error: {e}")

    def show_success(self, text):
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.success(
            title='成功',
            content=text,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
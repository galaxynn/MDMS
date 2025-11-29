from sqlalchemy import func
from mdms.database.models import Review, Movie

class ReviewManager:
    """
    影评管理服务类
    负责处理影评的增删改查，并自动维护电影的统计数据（评分、评分人数）。
    """

    def create_review(self, session, user_id, movie_id, rating, comment=None):
        """
        创建新影评
        """
        # 1. 检查是否存在 (虽然数据库有唯一约束，但应用层检查更友好)
        existing = session.query(Review).filter_by(user_id=user_id, movie_id=movie_id).first()
        if existing:
            raise ValueError("您已经评价过该电影，请使用修改功能。")

        # 2. 创建对象
        new_review = Review(
            user_id=user_id,
            movie_id=movie_id,
            rating=rating,
            comment=comment
        )
        session.add(new_review)

        # 3. 刷新以获取 ID 并确保写入
        session.flush()

        # 4. 触发统计更新 - 修复：这里调用了错误的方法名
        self.update_movie_stats(session, movie_id)  # 原来是 self._update_movie_stats

        return new_review

    def update_review(self, session, review_id, new_rating, new_comment):
        """
        修改影评
        """
        review = session.query(Review).get(review_id)
        if not review:
            raise ValueError("影评不存在")

        # 记录旧的 movie_id 以防万一（虽然通常不会改 movie_id）
        movie_id = review.movie_id

        # 更新字段
        review.rating = new_rating
        review.comment = new_comment
        # review.created_at = datetime.now() # 如果需要更新时间字段

        # 刷新
        session.flush()

        # 触发统计更新
        self.update_movie_stats(session, movie_id)

        return review

    def delete_review(self, session, review_id):
        """
        删除影评
        """
        review = session.query(Review).get(review_id)
        if not review:
            return

        movie_id = review.movie_id

        # 删除
        session.delete(review)

        # 刷新 (必须先 flush 让删除生效，统计才会准确)
        session.flush()

        # 触发统计更新
        self.update_movie_stats(session, movie_id)

    def update_movie_stats(self, session, movie_id):
        """
        [核心逻辑] 重新计算并更新电影的平均分和评分人数
        类似于数据库触发器
        """
        # 使用 SQL 聚合函数直接计算，性能最高
        stats = session.query(
            func.count(Review.rating).label('count'),
            func.avg(Review.rating).label('average')
        ).filter(Review.movie_id == movie_id).one()

        count = stats.count
        average = stats.average

        # 处理没有评论的情况
        if count is None or count == 0:
            count = 0
            average = 0.0
        else:
            # 确保转换为浮点数并保留2位小数 (根据你的 Numeric(4,2) 定义)
            average = float(average)

        # 更新电影表
        movie = session.query(Movie).get(movie_id)
        if movie:
            movie.rating_count = count
            movie.average_rating = average
            # 注意：这里不需要 commit，由调用者统一 commit


# 实例化一个单例对象方便调用
review_manager = ReviewManager()
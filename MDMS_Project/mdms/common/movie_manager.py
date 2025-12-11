from mdms.database.models import Movie

class MovieManager:
    """
    电影数据管理服务类
    负责电影数据的增删改查操作
    """

    def get_all_movies(self, session):
        """
        获取所有电影列表，按标题排序
        """
        return session.query(Movie).order_by(Movie.title).all()

    def add_movie(self, session, movie_data: dict):
        """
        新增电影
        :param movie_data: 包含电影信息的字典 (form_data)
        """
        # 利用字典解包直接创建对象
        new_movie = Movie(**movie_data)
        session.add(new_movie)
        # flush 确保数据写入并生成 ID，但不提交事务（由调用者提交）
        session.flush()
        return new_movie

    def delete_movie(self, session, movie_id):
        """
        根据 ID 删除电影
        """
        movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
        if movie:
            session.delete(movie)
            session.flush()
            return True
        return False

# 单例实例
movie_manager = MovieManager()
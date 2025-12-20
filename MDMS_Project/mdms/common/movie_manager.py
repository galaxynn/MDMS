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
        new_movie = Movie(**movie_data)
        session.add(new_movie)
        session.flush()
        return new_movie

    def update_movie(self, session, movie_id, movie_data: dict):
        """
        更新电影信息
        :param movie_id: 电影 ID
        :param movie_data: 包含需要修改的字段的字典
        """
        movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            return None

        # 遍历字典更新属性
        for key, value in movie_data.items():
            if hasattr(movie, key):
                setattr(movie, key, value)

        session.flush()
        return movie

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
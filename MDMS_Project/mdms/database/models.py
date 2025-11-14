# mdms/database/models.py

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, String, Integer, Date, ForeignKey, Text, Table,
    DateTime, Enum, Numeric, CheckConstraint, UniqueConstraint,
    Index
)
from sqlalchemy.sql import func, desc  # 导入 desc 函数

import uuid

# 所有数据模型的基类
Base = declarative_base()

# --- 关联表 (多对多) ---

# Movies 和 Genres 之间的多对多关联表
# 这是一个没有额外数据的纯关联表，所以我们使用 Table 对象
movies_genres_table = Table(
    'movies_genres',
    Base.metadata,
    # MODIFIED: 为每个外键添加了 index=True，以优化单向 JOIN 查询
    Column('movie_id', String(36), ForeignKey('movies.movie_id'), primary_key=True, index=True),
    Column('genre_id', Integer, ForeignKey('genres.genre_id'), primary_key=True, index=True)
)


# --- 模型类 ---

class User(Base):
    """
    用户表 (User)
    保存系统用户的相关信息。
    """
    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('user', 'admin', name='user_role_enum'), nullable=False, server_default='user')
    created_at = Column(DateTime, server_default=func.now())

    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class Person(Base):
    """
    参与人表 (People)
    保存电影参与人（如导演、演员）的信息。
    """
    __tablename__ = 'people'

    person_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # `index=True` 已经正确实现了按姓名搜索的优化
    name = Column(String(255), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    birthdate = Column(Date, nullable=True)
    photo_url = Column(String(1024), nullable=True)

    movie_associations = relationship('MoviePerson', back_populates='person', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Person(name='{self.name}')>"


class Genre(Base):
    """
    电影类型表 (Genres)
    保存电影的分类，如“喜剧”、“剧情”等。
    """
    __tablename__ = 'genres'

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

    movies = relationship('Movie', secondary=movies_genres_table, back_populates='genres')

    def __repr__(self):
        return f"<Genre(name='{self.name}')>"


class Movie(Base):
    """
    电影表 (Movies)
    保存电影的核心信息。
    """
    __tablename__ = 'movies'

    movie_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # `index=True` 已经正确实现了按标题搜索的优化
    title = Column(String(255), nullable=False, index=True)
    synopsis = Column(Text, nullable=True)
    release_date = Column(Date, nullable=True)
    runtime_minutes = Column(Integer, nullable=True)
    country = Column(String(50), nullable=True)
    language = Column(String(50), nullable=True)
    poster_url = Column(String(1024), nullable=True)
    average_rating = Column(Numeric(4, 2), nullable=False, server_default='0.00')
    rating_count = Column(Integer, nullable=False, server_default='0')

    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')
    genres = relationship('Genre', secondary=movies_genres_table, back_populates='movies')
    people_associations = relationship('MoviePerson', back_populates='movie', cascade='all, delete-orphan')

    # ADDED: 使用 __table_args__ 来定义需要降序的索引
    __table_args__ = (
        # 优化“Top 10”或“按评分排序”查询 (ORDER BY average_rating DESC)
        Index('idx_movies_average_rating', desc('average_rating')),
        # 优化“最新上映”查询 (ORDER BY release_date DESC)
        Index('idx_movies_release_date', desc('release_date')),
    )

    def __repr__(self):
        return f"<Movie(title='{self.title}', release_date='{self.release_date}')>"


class Review(Base):
    """
    影评表 (Reviews)
    保存用户对电影的评分和评论。
    """
    __tablename__ = 'reviews'

    review_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # `index=True` 已经正确实现了外键索引
    movie_id = Column(String(36), ForeignKey('movies.movie_id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    movie = relationship('Movie', back_populates='reviews')
    user = relationship('User', back_populates='reviews')

    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_review'),
        CheckConstraint('rating >= 1 AND rating <= 10', name='ck_rating_range')
    )

    def __repr__(self):
        return f"<Review(user_id='{self.user_id}', movie_id='{self.movie_id}', rating={self.rating})>"


class MoviePerson(Base):
    """
    电影-参与人关联表 (Movies_People)
    """
    __tablename__ = 'movies_people'

    crew_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # `index=True` 已经正确实现了外键索引
    movie_id = Column(String(36), ForeignKey('movies.movie_id'), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey('people.person_id'), nullable=False, index=True)
    role = Column(Enum('Director', 'Actor', 'Writer', 'Producer', name='crew_role_enum'), nullable=False)
    character_name = Column(String(255), nullable=True)

    movie = relationship('Movie', back_populates='people_associations')
    person = relationship('Person', back_populates='movie_associations')

    def __repr__(self):
        return f"<MoviePerson(movie_id='{self.movie_id}', person_id='{self.person_id}', role='{self.role}')>"
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, String, Integer, Date, ForeignKey, Text, Table,
    DateTime, Enum, Numeric, CheckConstraint, UniqueConstraint
)
from sqlalchemy.sql import func
import uuid

# 所有数据模型的基类
Base = declarative_base()

# --- 关联表 (多对多) ---

# Movies 和 Genres 之间的多对多关联表
# 这是一个没有额外数据的纯关联表，所以我们使用 Table 对象
movies_genres_table = Table(
    'movies_genres',
    Base.metadata,
    Column('movie_id', String(36), ForeignKey('movies.movie_id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.genre_id'), primary_key=True)
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

    # 关系：一个用户可以有多条影评
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
    name = Column(String(255), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    birthdate = Column(Date, nullable=True)
    photo_url = Column(String(1024), nullable=True)

    # 关系：一个人可以在多部电影中担任多种角色（通过 MoviePerson 关联）
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

    # 关系：一个类型可以包含多部电影（通过 movies_genres_table 多对多）
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
    title = Column(String(255), nullable=False, index=True)
    synopsis = Column(Text, nullable=True)
    release_date = Column(Date, nullable=True)
    runtime_minutes = Column(Integer, nullable=True)
    country = Column(String(50), nullable=True)
    language = Column(String(50), nullable=True)
    poster_url = Column(String(1024), nullable=True)
    # 使用 Numeric(3, 2) 来精确存储 0.00 到 9.99 之间的评分 (假设最高10.0，则需 4, 2)
    # 按照表2设计 DECIMAL(3, 2) (即 0.00 ~ 9.99)
    average_rating = Column(Numeric(4, 2), nullable=False, server_default='0.00')
    rating_count = Column(Integer, nullable=False, server_default='0')

    # 关系：一部电影可以有多条影评
    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')

    # 关系：一部电影可以有多个类型（通过 movies_genres_table 多对多）
    genres = relationship('Genre', secondary=movies_genres_table, back_populates='movies')

    # 关系：一部电影有多位参与人（通过 MoviePerson 关联）
    people_associations = relationship('MoviePerson', back_populates='movie', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Movie(title='{self.title}', release_date='{self.release_date}')>"


class Review(Base):
    """
    影评表 (Reviews)
    保存用户对电影的评分和评论。
    """
    __tablename__ = 'reviews'

    review_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    movie_id = Column(String(36), ForeignKey('movies.movie_id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关系：一条影评属于一部电影
    movie = relationship('Movie', back_populates='reviews')
    # 关系：一条影评属于一个用户
    user = relationship('User', back_populates='reviews')

    __table_args__ = (
        # 复合唯一约束：一个用户只能对一部电影发表一次评论
        UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_review'),
        # 检查约束：评分必须在 1 到 10 之间
        CheckConstraint('rating >= 1 AND rating <= 10', name='ck_rating_range')
    )

    def __repr__(self):
        return f"<Review(user_id='{self.user_id}', movie_id='{self.movie_id}', rating={self.rating})>"


class MoviePerson(Base):
    """
    电影-参与人关联表 (Movies_People)
    这是一个“关联对象”，因为它不仅连接了 Movie 和 Person，还包含了额外的职责信息。
    """
    __tablename__ = 'movies_people'

    crew_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    movie_id = Column(String(36), ForeignKey('movies.movie_id'), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey('people.person_id'), nullable=False, index=True)
    role = Column(Enum('Director', 'Actor', 'Writer', 'Producer', name='crew_role_enum'), nullable=False)
    character_name = Column(String(255), nullable=True) # 仅当 role='Actor' 时

    # 关系：此条记录关联到一部电影
    movie = relationship('Movie', back_populates='people_associations')
    # 关系：此条记录关联到一个参与人
    person = relationship('Person', back_populates='movie_associations')

    __table_args__ = (
        # 也许需要一个复合唯一约束，防止同一个人在同一部电影中重复出现（除非允许一人多角）
        # UniqueConstraint('movie_id', 'person_id', 'role', 'character_name', name='uq_movie_person_role')
        # 暂时遵循表设计，不添加额外约束
    )

    def __repr__(self):
        return f"<MoviePerson(movie_id='{self.movie_id}', person_id='{self.person_id}', role='{self.role}')>"
# mdms/database/models.py

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, String, Integer, Date, ForeignKey, Text, Table,
    DateTime, Enum, Numeric, CheckConstraint, UniqueConstraint,
    Index
)
from sqlalchemy.sql import func, desc
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# 所有数据模型的基类
Base = declarative_base()

# 关联表 (多对多)
# Movies 和 Genres 之间的多对多关联表
# 这是一个没有额外数据的“纯关联表”。
# 因为只需要存储 movie_id 和 genre_id 的对应关系，不需要记录额外信息（如关联时间等），
# 所以直接使用 Table 对象定义，而不需要定义成一个类。
movies_genres_table = Table(
    'movies_genres',
    Base.metadata,
    # movie_id 是外键，指向 movies 表。index=True 用于优化查询，例如查找某部电影的所有类型。
    Column('movie_id', String(36), ForeignKey('movies.movie_id'), primary_key=True, index=True),
    # genre_id 是外键，指向 genres 表。index=True 用于优化查询，例如查找属于某种类型的所有电影。
    Column('genre_id', Integer, ForeignKey('genres.genre_id'), primary_key=True, index=True)
)


# 模型类定义

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

    # 关系定义：用户与影评 (One-to-Many)
    # 这是一个“一对多”关系：一个用户可以发布多条影评。
    # back_populates='user': 指示 SQLAlchemy 在 Review 类中寻找名为 'user' 的属性，以同步关系。
    # 当你在 User.reviews 中添加一个 Review 对象时，该 Review 对象的 .user 属性会自动指向当前 User。
    # cascade='all, delete-orphan': 级联操作配置。
    # 'all' 表示将添加、合并等操作级联到子对象。
    # 'delete-orphan' 表示如果从这个列表中移除了一个 Review 对象，或者删除了这个 User，
    # 那么对应的 Review 记录也会从数据库中物理删除（防止出现没有所属用户的孤儿数据）。
    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Person(Base):
    """
    参与人表 (People)
    保存电影参与人（如导演、演员、编剧）的信息。
    这是一个实体表，它不直接连接 Movie，而是通过 MoviePerson 关联表连接。
    """
    __tablename__ = 'people'

    person_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    birthdate = Column(Date, nullable=True)
    photo_url = Column(String(1024), nullable=True)

    # 关系定义：参与人与电影关联记录
    # 这里使用的是“关联对象模式”。
    # 也是一个“一对多”关系，指向中间表 MoviePerson。
    # Person 是“一”，MoviePerson 是“多”。
    # 这意味着一个 Person 可以在多部电影中担任角色（产生多条关联记录）。
    # back_populates='person': 与 MoviePerson 类中的 person 属性对应。
    # cascade='all, delete-orphan': 如果删除了这个 Person，数据库会自动删除所有涉及这个人的参演记录。
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

    # 关系定义：类型与电影 (Many-to-Many)
    # 这是一个“多对多”关系：一个类型包含多部电影，一部电影属于多个类型。
    # secondary=movies_genres_table: 指定用于连接的中间表（纯关联表）。
    # SQLAlchemy 会自动处理中间表的插入和删除。
    # back_populates='genres': 与 Movie 类中的 genres 属性对应。
    # 这里不需要 cascade='delete-orphan'，因为删除一个类型通常不应该删除属于该类型的电影。
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
    average_rating = Column(Numeric(4, 2), nullable=False, server_default='0.00')
    rating_count = Column(Integer, nullable=False, server_default='0')

    # 关系定义：电影与影评 (One-to-Many)
    # 类似于 User.reviews。
    # Movie 是“一”，Review 是“多”。
    # back_populates='movie': 与 Review 类中的 movie 属性对应。
    # cascade='all, delete-orphan': 删除电影时，该电影下的所有影评也会被删除。
    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')

    # 关系定义：电影与类型 (Many-to-Many)
    # 对应 Genre.movies。
    # secondary=movies_genres_table: 指定同一个中间表。
    # back_populates='movies': 与 Genre 类中的 movies 属性对应，实现双向绑定。
    genres = relationship('Genre', secondary=movies_genres_table, back_populates='movies')

    # 关系定义：电影与演职员关联记录 (One-to-Many)
    # 对应 Person.movie_associations。
    # 指向中间表对象 MoviePerson。
    # 这是一个“一对多”关系：一部电影有多个演职员记录（导演、主角、配角等）。
    # back_populates='movie': 与 MoviePerson 类中的 movie 属性对应。
    # cascade='all, delete-orphan': 删除电影时，所有与该电影相关的参演记录都会被删除。
    people_associations = relationship('MoviePerson', back_populates='movie', cascade='all, delete-orphan')

    # 使用 __table_args__ 来定义需要降序的索引
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
    这是 User 和 Movie 之间的一对多关系的“多”端。
    """
    __tablename__ = 'reviews'

    review_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # 外键：指向 movies 表。定义了这篇影评属于哪部电影。
    movie_id = Column(String(36), ForeignKey('movies.movie_id'), nullable=False, index=True)
    # 外键：指向 users 表。定义了这篇影评是谁写的。
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关系定义：影评所属的电影 (Many-to-One)
    # 这里的 relationship 定义了从 Review 对象访问其父对象 Movie 的路径。
    # back_populates='reviews': 指向 Movie 类中的 reviews 列表。
    movie = relationship('Movie', back_populates='reviews')

    # 关系定义：影评所属的用户 (Many-to-One)
    # 定义了从 Review 对象访问其作者 User 的路径。
    # back_populates='reviews': 指向 User 类中的 reviews 列表。
    user = relationship('User', back_populates='reviews')

    __table_args__ = (
        # 复合唯一约束：确保一个用户对同一部电影只能发一篇影评。
        UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_review'),
        # 检查约束：确保评分在 1 到 10 之间。
        CheckConstraint('rating >= 1 AND rating <= 10', name='ck_rating_range')
    )

    def __repr__(self):
        return f"<Review(user_id='{self.user_id}', movie_id='{self.movie_id}', rating={self.rating})>"


class MoviePerson(Base):
    """
    电影-参与人关联表 (Movies_People)
    这是一个“关联对象 (Association Object)”。
    它不仅仅连接 Movie 和 Person（实现多对多），还存储了关于这个连接的额外信息：
    role (担任的角色：导演、演员等) 和 character_name (饰演的角色名)。
    """
    __tablename__ = 'movies_people'

    crew_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # 外键：指向 movies 表。
    movie_id = Column(String(36), ForeignKey('movies.movie_id'), nullable=False, index=True)
    # 外键：指向 people 表。
    person_id = Column(String(36), ForeignKey('people.person_id'), nullable=False, index=True)

    # 额外数据：这两个字段是我们在纯关联表（如 movies_genres）中无法存储的。
    role = Column(Enum('Director', 'Actor', 'Writer', 'Producer', name='crew_role_enum'), nullable=False)
    character_name = Column(String(255), nullable=True)

    # 关系定义：关联对象所属的电影 (Many-to-One)
    # 对应 Movie.people_associations。
    # 当通过 MoviePerson 对象访问 .movie 时，会得到对应的 Movie 实例。
    movie = relationship('Movie', back_populates='people_associations')

    # 关系定义：关联对象所属的人员 (Many-to-One)
    # 对应 Person.movie_associations。
    # 当通过 MoviePerson 对象访问 .person 时，会得到对应的 Person 实例。
    person = relationship('Person', back_populates='movie_associations')

    def __repr__(self):
        return f"<MoviePerson(movie_id='{self.movie_id}', person_id='{self.person_id}', role='{self.role}')>"
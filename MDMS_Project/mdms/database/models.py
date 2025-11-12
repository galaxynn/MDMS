# mdms/database/models.py
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text
import uuid

# 所有数据模型的基类
Base = declarative_base()

# 示例：电影表
class Movie(Base):
    __tablename__ = 'movies'
    
    # 使用 UUID 作为主键，更适合分布式系统
    movie_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    release_date = Column(Date)
    country = Column(String(100))
    
    test_string = Column(String(100))
    test_date = Column(Date)
    
    # 在这里定义其他字段...
    
    def __repr__(self):
        return f"<Movie(title='{self.title}')>"

# 在这里继续定义 Users, People, Reviews 等所有其他模型...
# 例如：
# class User(Base):
#     __tablename__ = 'users'
#     ...
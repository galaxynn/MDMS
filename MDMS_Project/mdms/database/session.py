# mdms/database/session.py
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 读取配置文件
config = configparser.ConfigParser()
# 注意路径是相对于项目根目录的
config.read('config.ini') 
db_config = config['database']

# 构建数据库连接 URL
DATABASE_URL = (
    f"{db_config['type']}://"
    f"{db_config['username']}:{db_config['password']}@"
    f"{db_config['host']}:{db_config['port']}/"
    f"{db_config['db_name']}?charset=utf8mb4"
)

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True) # echo=True 会打印执行的 SQL 语句，方便调试

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 提供一个简单的函数来获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
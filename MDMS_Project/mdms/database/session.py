# mdms/database/session.py
import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 获取当前文件(session.py)的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件所在的目录 (d:\...\MDMS_Project\mdms\database)
database_dir = os.path.dirname(current_file_path)

# 从 database 目录往上走两级，到达项目根目录 (d:\...\MDMS_Project)
project_root = os.path.dirname(os.path.dirname(database_dir))

# 构造 config.ini 的完整绝对路径
config_path = os.path.join(project_root, 'config.ini')

# 读取配置文件
config = configparser.ConfigParser()

# 使用绝对路径来读取文件
files_read = config.read(config_path, encoding='utf-8') # 增加 encoding 防止中文乱码

# 添加一个检查，如果文件没读到就报错，方便调试
if not files_read:
    raise FileNotFoundError(f"配置文件未找到或读取失败: {config_path}")

db_config = config['database']

# 构建数据库连接 URL
DATABASE_URL = (
    f"{db_config['type']}://"
    f"{db_config['username']}:{db_config['password']}@"
    f"{db_config['host']}:{db_config['port']}/"
    f"{db_config['db_name']}?charset=utf8mb4"
)

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 提供一个简单的函数来获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
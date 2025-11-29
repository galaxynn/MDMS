import sys
import os

# ==========================================
# 1. 环境配置
# ==========================================
# 将当前目录添加到 python 路径，确保能找到 mdms 包
sys.path.append(os.getcwd())

from mdms.database.session import engine
from mdms.database.models import Base


def reset_database():
    print("==========================================")
    print("!!! 危险操作警报 !!!")
    print("==========================================")
    print(f"即将针对以下数据库执行重置操作：")
    print(f"{engine.url}")
    print("\n此操作将：")
    print("1. 删除数据库中的【所有表】")
    print("2. 【永久清空】所有数据")
    print("3. 重新创建空表结构")
    print("==========================================")

    confirm = input("你确定要继续吗？(输入 'yes' 确认): ")

    if confirm.lower() != 'yes':
        print("\n操作已取消。")
        return

    try:
        print("\n[1/2] 正在删除所有表...")
        # drop_all 会自动处理外键依赖顺序
        Base.metadata.drop_all(bind=engine)
        print("  -> 所有表已删除。")

        print("\n[2/2] 正在重新创建表结构...")
        # create_all 根据 models.py 重新建表
        Base.metadata.create_all(bind=engine)
        print("  -> 表结构已重建。")

        print("\nSUCCESS: 数据库已成功重置！现在是空的了。")
        print("提示: 你可以运行 'python import_movies_data.py' 来导入初始数据。")

    except Exception as e:
        print(f"\n[错误] 重置过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    reset_database()
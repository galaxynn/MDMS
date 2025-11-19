# mdms/common/user_manager.py
from PySide6.QtCore import QObject, Signal

class UserManager(QObject):
    """
    用户状态管理器（单例模式）
    """
    # 信号：当用户登录状态改变时触发
    # 发送当前 User 对象，如果是注销则发送 None
    userChanged = Signal(object)

    _instance = None

    def __init__(self):
        super().__init__()
        self._current_user = None

    @classmethod
    def instance(cls):
        """ 获取单例实例 """
        if cls._instance is None:
            cls._instance = UserManager()
        return cls._instance

    @property
    def current_user(self):
        """ 获取当前用户 """
        return self._current_user

    @property
    def is_logged_in(self):
        """ 判断是否已登录 """
        return self._current_user is not None

    def login(self, user_obj):
        """ 登录逻辑：设置用户并发送信号 """
        self._current_user = user_obj
        print(f"用户 {user_obj.username} 已登录")
        self.userChanged.emit(user_obj)

    def logout(self):
        """ 注销逻辑：清空用户并发送信号 """
        print(f"用户 {self._current_user.username} 已注销")
        self._current_user = None
        self.userChanged.emit(None)

# 为了方便导入，直接实例化一个全局对象（可选，或者总是调用 UserManager.instance()）
user_manager = UserManager.instance()
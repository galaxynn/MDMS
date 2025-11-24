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
        self._session_role = None  # 存储会话中的角色

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
    def session_role(self):
        """ 获取会话角色 """
        return self._session_role

    @property
    def is_logged_in(self):
        """ 判断是否已登录 """
        return self._current_user is not None

    def login(self, user_obj, session_role=None):
        """ 登录逻辑：设置用户并发送信号 """
        self._current_user = user_obj
        # 如果指定了会话角色，使用它；否则使用用户的实际角色
        self._session_role = session_role if session_role is not None else user_obj.role
        print(f"用户 {user_obj.username} 已登录，会话角色: {self._session_role}")
        self.userChanged.emit(user_obj)

    def logout(self):
        """ 注销逻辑：清空用户并发送信号 """
        if self._current_user:
            print(f"用户 {self._current_user.username} 已注销")
        self._current_user = None
        self._session_role = None
        self.userChanged.emit(None)

# 为了方便导入，直接实例化一个全局对象（可选，或者总是调用 UserManager.instance()）
user_manager = UserManager.instance()
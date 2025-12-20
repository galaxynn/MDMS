from mdms.database.models import User


class UserAdminManager:
    """
    用户后台管理服务类
    专供管理员管理所有用户数据（查询、修改信息、重置密码、删除）
    """

    def get_all_users(self, session):
        """
        获取所有用户列表，按注册时间排序
        """
        return session.query(User).order_by(User.created_at).all()

    def update_user_info(self, session, user_id, user_data: dict):
        """
        更新用户信息（支持基本信息修改，若包含 password 字段会自动哈希）
        :param user_id: 用户 ID
        :param user_data: 包含变更信息的字典
        """
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None

        for key, value in user_data.items():
            # 特殊处理密码字段，确保通过 set_password 进行哈希
            if key == 'password' and value:
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)

        session.flush()
        return user

    def reset_password(self, session, user_id, new_password):
        """
        重置指定用户的密码
        """
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 调用 Model 中定义的 set_password 方法进行哈希处理
        user.set_password(new_password)
        session.flush()
        return user

    def delete_user(self, session, user_id):
        """
        删除指定用户
        """
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            session.delete(user)
            session.flush()
            return True
        return False


# 单例实例
user_admin_manager = UserAdminManager()
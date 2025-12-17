from mdms.database.models import Person

class PersonManager:
    """
    人员数据管理服务类
    负责演职人员数据的增删改查操作
    """

    def get_all_people(self, session):
        """
        获取所有人员列表，按姓名排序
        """
        return session.query(Person).order_by(Person.name).all()

    def add_person(self, session, person_data: dict):
        """
        新增人员
        :param person_data: 包含人员信息的字典
        """
        new_person = Person(**person_data)
        session.add(new_person)
        session.flush()
        return new_person

    def delete_person(self, session, person_id):
        """
        根据 ID 删除人员
        """
        person = session.query(Person).filter(Person.person_id == person_id).first()
        if person:
            session.delete(person)
            session.flush()
            return True
        return False

# 单例实例
person_manager = PersonManager()
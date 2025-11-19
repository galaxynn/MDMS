# init_test_data.py
import sys
import os
from datetime import date
from sqlalchemy.exc import IntegrityError

# 确保能找到 mdms 模块
sys.path.append(os.getcwd())

from mdms.database.session import SessionLocal, engine
from mdms.database.models import Base, User, Movie, Genre, Person, MoviePerson, Review


def init_data():
    print("--- 开始初始化测试数据 ---")

    # 1. 确保表结构已创建
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    try:
        # ==========================================
        # 1. 创建类型 (Genres)
        # ==========================================
        print("正在创建电影类型...")
        genres_data = ["科幻", "动作", "剧情", "犯罪", "动画", "奇幻"]
        genres = {}  # 用于后续查找

        for name in genres_data:
            # 检查是否存在，防止重复
            g = session.query(Genre).filter_by(name=name).first()
            if not g:
                g = Genre(name=name)
                session.add(g)
            genres[name] = g

        session.flush()  # 刷新以获取 ID

        # ==========================================
        # 2. 创建演职人员 (People)
        # ==========================================
        print("正在创建演职人员...")

        people_list = [
            Person(name="克里斯托弗·诺兰", bio="著名导演，以非线性叙事闻名。", birthdate=date(1970, 7, 30)),
            Person(name="莱昂纳多·迪卡普里奥", bio="奥斯卡影帝。", birthdate=date(1974, 11, 11)),
            Person(name="蒂姆·罗宾斯", bio="《肖申克的救赎》安迪。", birthdate=date(1958, 10, 16)),
            Person(name="摩根·弗里曼", bio="上帝之声。", birthdate=date(1937, 6, 1)),
            Person(name="荒木飞吕彦", bio="不老的漫画家。", birthdate=date(1960, 6, 7))
        ]

        # 简单排重逻辑
        created_people = {}
        for p in people_list:
            exist = session.query(Person).filter_by(name=p.name).first()
            if not exist:
                session.add(p)
                created_people[p.name] = p
            else:
                created_people[p.name] = exist

        session.flush()

        # ==========================================
        # 3. 创建电影 (Movies)
        # ==========================================
        print("正在创建电影...")

        # 暂时使用 qfluentwidgets 的 logo 作为占位符，或者使用网络图片 URL
        # 如果你有本地图片，改为本地绝对路径
        placeholder_img = ":/qfluentwidgets/images/logo.png"

        movies_data = [
            Movie(
                title="盗梦空间 (Inception)",
                synopsis="柯布是一名经验丰富的窃贼，他在人们精神最为脆弱的时候，潜入他们的潜意识中盗取机密。这一次，他接到了一个相反的任务：不是偷窃思想，而是植入思想。",
                release_date=date(2010, 7, 16),
                runtime_minutes=148,
                country="美国",
                language="英语",
                poster_url=placeholder_img,
                average_rating=9.3,
                rating_count=1000
            ),
            Movie(
                title="肖申克的救赎",
                synopsis="银行家安迪被指控杀害妻子及其情人，被判无期徒刑。在肖申克监狱，他用二十年的时间，完成了灵魂的救赎。",
                release_date=date(1994, 9, 10),
                runtime_minutes=142,
                country="美国",
                language="英语",
                poster_url=placeholder_img,
                average_rating=9.7,
                rating_count=2500
            ),
            Movie(
                title="JoJo的奇妙冒险：不灭钻石",
                synopsis="在平静的杜王町，由于“弓与箭”的作用，替身使者数量不断增加。东方仗助与伙伴们为了守护小镇，挺身而出。",
                release_date=date(2017, 8, 4),
                runtime_minutes=119,
                country="日本",
                language="日语",
                poster_url=placeholder_img,
                average_rating=8.5,
                rating_count=500
            )
        ]

        created_movies = []
        for m in movies_data:
            exist = session.query(Movie).filter_by(title=m.title).first()
            if not exist:
                session.add(m)
                created_movies.append(m)
            else:
                created_movies.append(exist)

        session.flush()

        # ==========================================
        # 4. 建立关联关系 (Movies <-> Genres, Movies <-> People)
        # ==========================================
        print("正在建立关联关系...")

        # 4.1 盗梦空间
        m_inception = created_movies[0]
        # 关联类型
        if "科幻" in genres: m_inception.genres.append(genres["科幻"])
        if "动作" in genres: m_inception.genres.append(genres["动作"])
        # 关联人员 (MoviePerson)
        mp1 = MoviePerson(movie=m_inception, person=created_people["克里斯托弗·诺兰"], role='Director')
        mp2 = MoviePerson(movie=m_inception, person=created_people["莱昂纳多·迪卡普里奥"], role='Actor',
                          character_name="Cobb")
        session.add_all([mp1, mp2])

        # 4.2 肖申克的救赎
        m_shawshank = created_movies[1]
        if "剧情" in genres: m_shawshank.genres.append(genres["剧情"])
        if "犯罪" in genres: m_shawshank.genres.append(genres["犯罪"])

        mp3 = MoviePerson(movie=m_shawshank, person=created_people["蒂姆·罗宾斯"], role='Actor',
                          character_name="Andy Dufresne")
        mp4 = MoviePerson(movie=m_shawshank, person=created_people["摩根·弗里曼"], role='Actor', character_name="Red")
        session.add_all([mp3, mp4])

        # 4.3 JoJo
        m_jojo = created_movies[2]
        if "动作" in genres: m_jojo.genres.append(genres["动作"])
        if "奇幻" in genres: m_jojo.genres.append(genres["奇幻"])
        # 原作者作为 Writer
        mp5 = MoviePerson(movie=m_jojo, person=created_people["荒木飞吕彦"], role='Writer')
        session.add(mp5)

        # ==========================================
        # 5. 创建用户和评论 (User & Review)
        # ==========================================
        print("正在创建用户和评论...")

        user_admin = User(
            username="admin",
            email="admin@example.com",
            password_hash="hashed_secret",
            role="admin"
        )
        user_normal = User(
            username="movie_fan",
            email="fan@example.com",
            password_hash="hashed_123456",
            role="user"
        )

        # 检查用户是否存在
        if not session.query(User).filter_by(username="admin").first():
            session.add(user_admin)
        if not session.query(User).filter_by(username="movie_fan").first():
            session.add(user_normal)

        session.flush()

        # 添加评论 (需要获取刚才添加的用户对象，确保有 ID)
        u1 = session.query(User).filter_by(username="admin").first()
        u2 = session.query(User).filter_by(username="movie_fan").first()

        # 检查是否已有评论，防止重复运行报错
        if not session.query(Review).filter_by(user_id=u1.user_id, movie_id=m_inception.movie_id).first():
            review1 = Review(user=u1, movie=m_inception, rating=10, comment="诺兰的神作，逻辑严密！")
            session.add(review1)

        if not session.query(Review).filter_by(user_id=u2.user_id, movie_id=m_shawshank.movie_id).first():
            review2 = Review(user=u2, movie=m_shawshank, rating=9, comment="经典的越狱故事，希望就在心中。")
            session.add(review2)

        # ==========================================
        # 6. 提交事务
        # ==========================================
        session.commit()
        print("--- 测试数据初始化成功！ ---")

    except Exception as e:
        session.rollback()
        print(f"初始化失败，已回滚。错误信息: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    init_data()
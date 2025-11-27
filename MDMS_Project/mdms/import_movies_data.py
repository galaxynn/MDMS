import sys
import os
import json
import random
from datetime import datetime

# ==========================================
# 1. 环境配置 (确保能找到 mdms 模块)
# ==========================================
sys.path.append(os.getcwd())

from mdms.database.session import SessionLocal, engine
# [新增] 引入 User 和 Review 模型
from mdms.database.models import Base, Movie, Genre, Person, MoviePerson, User, Review

# ==========================================
# 2. 配置参数
# ==========================================
JSON_FILE = 'movies_data.json'


def clean_text(text: str) -> str:
    """
    清洗文本工具函数：
    1. 去除全角空格 (\u3000) 和 不换行空格 (\u00a0)
    2. 去除多余的空行
    3. 去除每行首尾的缩进
    """
    if not text:
        return ""

    # 1. 替换特殊空白字符为普通空格或空字符
    text = text.replace('\u3000', ' ').replace('\u00a0', ' ')

    # 2. 按换行符分割
    lines = text.split('\n')

    # 3. 清理每一行
    clean_lines = [line.strip() for line in lines if line.strip()]

    # 4. 重新拼接
    return "\n".join(clean_lines)


def main():
    print("--- 开始导入爬虫数据 (带用户和评论生成) ---")

    # 1. 检查数据文件
    if not os.path.exists(JSON_FILE):
        print(f"[错误] 找不到文件: {JSON_FILE}")
        print("请先运行 spider_v2.py 获取数据。")
        return

    # 2. 确保表结构存在
    Base.metadata.create_all(bind=engine)

    # 3. 获取数据库会话
    session = SessionLocal()

    try:
        print("正在读取 JSON 数据...")
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            movies_data = json.load(f)

        # ==========================================
        # 4. 构建内存缓存
        # ==========================================
        print("正在构建缓存 (Genre/Person)...")

        genre_cache = {g.name: g for g in session.query(Genre).all()}
        person_cache = {p.name: p for p in session.query(Person).all()}
        existing_movie_titles = {m.title for m in session.query(Movie.title).all()}

        print(f"准备处理 {len(movies_data)} 部电影...")
        new_count = 0
        skip_count = 0

        # ==========================================
        # 5. 遍历并插入电影数据
        # ==========================================
        for m_data in movies_data:
            title = m_data['title']

            if title in existing_movie_titles:
                print(f"  [跳过] 已存在: {title}")
                skip_count += 1
                continue

            # 数据清洗
            raw_synopsis = m_data.get('synopsis', '')
            cleaned_synopsis = clean_text(raw_synopsis)

            release_date = None
            if m_data.get('release_date'):
                try:
                    release_date = datetime.strptime(m_data['release_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass

                    # 创建 Movie
            movie = Movie(
                title=title,
                synopsis=cleaned_synopsis,
                release_date=release_date,
                runtime_minutes=m_data.get('runtime', 0),
                country=m_data.get('country', '')[:50],
                language=m_data.get('language', '')[:50],
                poster_url=m_data.get('poster_path', ''),
                average_rating=m_data.get('rating', 0),
                rating_count=m_data.get('rating_count', 0)
            )
            session.add(movie)
            session.flush()

            # 处理 Genre
            for g_name in m_data.get('genres', []):
                if not g_name: continue
                if g_name not in genre_cache:
                    new_genre = Genre(name=g_name)
                    session.add(new_genre)
                    session.flush()
                    genre_cache[g_name] = new_genre
                movie.genres.append(genre_cache[g_name])

            # 处理 Person
            added_person_keys = set()
            for p_data in m_data.get('people', []):
                p_name = p_data['name']
                p_role = p_data['role']
                p_char = p_data.get('character_name')
                p_photo = p_data.get('photo_path')

                if p_name not in person_cache:
                    new_person = Person(name=p_name, photo_url=p_photo)
                    session.add(new_person)
                    session.flush()
                    person_cache[p_name] = new_person
                else:
                    existing_person = person_cache[p_name]
                    if not existing_person.photo_url and p_photo:
                        existing_person.photo_url = p_photo
                        session.add(existing_person)

                person_obj = person_cache[p_name]
                unique_key = (person_obj.person_id, p_role)
                if unique_key not in added_person_keys:
                    assoc = MoviePerson(
                        movie_id=movie.movie_id,
                        person_id=person_obj.person_id,
                        role=p_role,
                        character_name=p_char
                    )
                    session.add(assoc)
                    added_person_keys.add(unique_key)

            new_count += 1
            print(f"  [新增电影] {title}")

        # ==========================================
        # 6. 生成测试用户和随机评论
        # ==========================================
        print("\n正在检查并生成测试用户...")
        user_list = []

        # 6.1 创建管理员账号 (admin/admin)
        admin_user = session.query(User).filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@mdms.com', role='admin')
            admin_user.set_password('admin')
            session.add(admin_user)
            print("  [新增用户] admin (密码: admin)")
        user_list.append(admin_user)

        # 6.2 创建普通测试用户 (密码默认 123456)
        dummy_names = ['alice', 'bob', 'charlie', 'david', 'movie_fan']
        for name in dummy_names:
            u = session.query(User).filter_by(username=name).first()
            if not u:
                u = User(username=name, email=f'{name}@test.com', role='user')
                u.set_password('123456')
                session.add(u)
                print(f"  [新增用户] {name} (密码: 123456)")
            user_list.append(u)

        session.flush()  # 确保新用户有 ID

        # 6.3 为电影生成随机评论
        print("正在为电影生成随机评论数据...")

        all_movies = session.query(Movie).all()
        comments_pool = [
            "非常精彩的电影，强烈推荐！",
            "剧情跌宕起伏，演员演技在线。",
            "画面太美了，每一帧都是壁纸。",
            "虽然是老片，但经典咏流传。",
            "结局有点意难平，但总体不错。",
            "导演功力深厚，配乐也是满分。",
            "前面稍微有点慢热，后面很燃。",
            "不愧是高分神作，值得二刷。",
            "特效一般，但故事讲得很好。",
            "看哭了，太感人了。"
        ]

        review_count = 0
        for movie in all_movies:
            # 如果该电影已经有评论，就跳过（避免重复运行导致评论爆炸）
            if session.query(Review).filter_by(movie_id=movie.movie_id).count() > 0:
                continue

            # 80% 的概率为这部电影生成评论
            if random.random() < 0.8:
                # 随机挑选 1 到 4 个用户来评论
                reviewers = random.sample(user_list, k=random.randint(1, min(len(user_list), 4)))

                for reviewer in reviewers:
                    # 随机生成 7-10 分的评价 (Top250嘛，分数高点正常)
                    rating = random.randint(7, 10)
                    comment = random.choice(comments_pool)

                    review = Review(
                        user_id=reviewer.user_id,
                        movie_id=movie.movie_id,
                        rating=rating,
                        comment=comment
                    )
                    session.add(review)
                    review_count += 1

        print(f"  [新增评论] 共生成 {review_count} 条随机评论")

        # ==========================================
        # 7. 提交事务
        # ==========================================
        session.commit()
        print("-" * 30)
        print(f"导入全部完成！新增电影: {new_count}, 新增评论: {review_count}")

    except Exception as e:
        session.rollback()
        print(f"\n[严重错误] 导入失败，已回滚。错误信息: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
### **MDMS 数据字典 (Data Dictionary)**

#### **1. D1: Users (用户表)**

存储系统用户的基本信息、凭证和角色。

| 字段名 (Field Name) | 数据类型 (Data Type)  | 约束 (Constraints)        | 描述 (Description)                                         | 别名 (Alias) | 示例值 (Example Value)                   |
| :------------------ | :-------------------- | :------------------------ | :--------------------------------------------------------- | :----------- | :--------------------------------------- |
| `user_id`           | UUID                  | PK (Primary Key)          | 用户的全局唯一标识符，使用 UUID 以避免分布式系统中的冲突。 | 用户ID       | `'123e4567-e89b-12d3-a456-426614174000'` |
| `username`          | VARCHAR(100)          | UNIQUE, NOT NULL          | 用户公开显示的昵称，必须唯一。                             | 用户名       | `'john_doe'`                             |
| `email`             | VARCHAR(255)          | UNIQUE, NOT NULL          | 用于登录和接收通知的电子邮箱，必须唯一。                   | 邮箱         | `'john.doe@example.com'`                 |
| `password_hash`     | VARCHAR(255)          | NOT NULL                  | 用户密码经过哈希和加盐处理后的字符串，绝不存储明文密码。   | 哈希密码     | `'...'` (哈希值)                         |
| `role`              | ENUM('user', 'admin') | NOT NULL, DEFAULT 'user'  | 定义用户权限级别。`user`为普通用户，`admin`为管理员。      | 角色         | `'user'`                                 |
| `created_at`        | TIMESTAMP             | DEFAULT CURRENT_TIMESTAMP | 记录用户账户创建的时间戳。                                 | 创建时间     | `'2025-11-04 12:30:00'`                  |

#### **2. D2: People (参与人表)**

存储所有电影行业从业者（如演员、导演）的个人资料。

| 字段名 (Field Name) | 数据类型 (Data Type) | 约束 (Constraints) | 描述 (Description)               | 别名 (Alias) | 示例值 (Example Value)                   |
| :------------------ | :------------------- | :----------------- | :------------------------------- | :----------- | :--------------------------------------- |
| `person_id`         | UUID                 | PK                 | 参与人的全局唯一标识符。         | 参与人ID     | `'a1b2c3d4-e5f6-7890-1234-567890abcdef'` |
| `name`              | VARCHAR(255)         | NOT NULL           | 参与人的全名。                   | 姓名         | `'克里斯托弗·诺兰'`                      |
| `bio`               | TEXT                 |                    | 参与人的生平简介或职业生涯概述。 | 简介         | `'一位著名的英美电影导演...'`            |
| `birthdate`         | DATE                 |                    | 参与人的出生日期。               | 出生日期     | `'1970-07-30'`                           |
| `photo_url`         | VARCHAR(1024)        |                    | 指向参与人肖像照片的 URL 链接。  | 照片链接     | `'https://example.com/photos/nolan.jpg'` |

#### **3. D3: Genres (类型表)**

存储预定义的电影类型标签。

| 字段名 (Field Name) | 数据类型 (Data Type) | 约束 (Constraints) | 描述 (Description)               | 别名 (Alias) | 示例值 (Example Value) |
| :------------------ | :------------------- | :----------------- | :------------------------------- | :----------- | :--------------------- |
| `genre_id`          | INT                  | PK, AUTO_INCREMENT | 类型的数字唯一标识符，自动增长。 | 类型ID       | `1`                    |
| `name`              | VARCHAR(100)         | UNIQUE, NOT NULL   | 类型的名称，必须唯一。           | 类型名称     | `'科幻'`               |

#### **4. D4: Movies (电影表)**

存储电影的核心信息。

| 字段名 (Field Name) | 数据类型 (Data Type) | 约束 (Constraints)     | 描述 (Description)                                           | 别名 (Alias) | 示例值 (Example Value)                        |
| :------------------ | :------------------- | :--------------------- | :----------------------------------------------------------- | :----------- | :-------------------------------------------- |
| `movie_id`          | UUID                 | PK                     | 电影的全局唯一标识符。                                       | 电影ID       | `'f0e9d8c7-b6a5-4321-fedc-ba9876543210'`      |
| `title`             | VARCHAR(255)         | NOT NULL               | 电影的官方标题。                                             | 标题         | `'盗梦空间'`                                  |
| `synopsis`          | TEXT                 |                        | 电影的剧情梗概。                                             | 剧情简介     | `'一个关于进入他人梦境窃取秘密的故事...'`     |
| `release_date`      | DATE                 |                        | 电影的首次公映日期。                                         | 上映日期     | `'2010-07-16'`                                |
| `runtime_minutes`   | INT                  |                        | 电影的总时长，以分钟为单位。                                 | 时长         | `148`                                         |
| `country`           | VARCHAR(50)          |                        | 电影的主要制片国家或地区。                                   | 制片国家     | `'美国'`                                      |
| `language`          | VARCHAR(50)          |                        | 电影的主要对白语言。                                         | 语言         | `'英语'`                                      |
| `poster_url`        | VARCHAR(1024)        |                        | 指向电影海报图片的 URL 链接。                                | 海报链接     | `'https://example.com/posters/inception.jpg'` |
| `average_rating`    | DECIMAL(3, 2)        | NOT NULL, DEFAULT 0.00 | 所有用户评分的算术平均值。这是一个冗余字段，用于优化读取性能。 | 平均分       | `8.80`                                        |
| `rating_count`      | INT                  | NOT NULL, DEFAULT 0    | 对该电影进行评分的用户总数。这是一个冗余字段。               | 评分人数     | `15000`                                       |

#### **5. D5: Reviews (影评表)**

存储用户对电影的评分和评论。

| 字段名 (Field Name)    | 数据类型 (Data Type)           | 约束 (Constraints)                                       | 描述 (Description)                         | 别名 (Alias) | 示例值 (Example Value)                   |
| :--------------------- | :----------------------------- | :------------------------------------------------------- | :----------------------------------------- | :----------- | :--------------------------------------- |
| `review_id`            | UUID                           | PK                                                       | 影评的全局唯一标识符。                     | 影评ID       | `'b1c2d3e4-f5a6-b7c8-d9e0-f1a2b3c4d5e6'` |
| `movie_id`             | UUID                           | FK -> Movies(movie_id)                                   | 关联的电影ID，指明这条影评是针对哪部电影。 | 电影ID       | `'f0e9d8c7-b6a5-4321-fedc-ba9876543210'` |
| `user_id`              | UUID                           | FK -> Users(user_id)                                     | 发布该影评的用户ID。                       | 用户ID       | `'123e4567-e89b-12d3-a456-426614174000'` |
| `rating`               | INT                            | NOT NULL (CHECK 1-10)                                    | 用户给出的整数评分，范围是1到10。          | 评分         | `9`                                      |
| `comment`              | TEXT                           |                                                          | 用户的详细评论内容，可以为空。             | 评论         | `'结构精巧，思想深刻，年度最佳！'`       |
| `created_at`           | TIMESTAMP                      | DEFAULT CURRENT_TIMESTAMP                                | 影评的发布时间戳。                         | 发布时间     | `'2025-11-05 18:00:00'`                  |
| `uq_user_movie_review` | UNIQUE (`user_id`, `movie_id`) | 复合唯一约束，确保一个用户对同一部电影只能发布一条影评。 | 用户电影唯一评论约束                       | N/A          | (`'user_id_val'`, `'movie_id_val'`)      |

#### **6. D6: Movie_Genres (电影-类型 连接表)**

用于建立 `Movies` 和 `Genres` 之间的多对多关系。

| 字段名 (Field Name) | 数据类型 (Data Type) | 约束 (Constraints)         | 描述 (Description) | 别名 (Alias) | 示例值 (Example Value)                   |
| :------------------ | :------------------- | :------------------------- | :----------------- | :----------- | :--------------------------------------- |
| `movie_id`          | UUID                 | FK -> Movies(movie_id), PK | 关联的电影ID。     | 电影ID       | `'f0e9d8c7-b6a5-4321-fedc-ba9876543210'` |
| `genre_id`          | INT                  | FK -> Genres(genre_id), PK | 关联的类型ID。     | 类型ID       | `1`                                      |

#### **7. D7: Movie_Crew (电影-参与人 连接表)**

用于建立 `Movies` 和 `People` 之间的多对多关系，并定义参与人在特定电影中的具体角色。

| 字段名 (Field Name) | 数据类型 (Data Type) | 约束 (Constraints)      | 描述 (Description)                                     | 别名 (Alias) | 示例值 (Example Value)                   |
| :------------------ | :------------------- | :---------------------- | :----------------------------------------------------- | :----------- | :--------------------------------------- |
| `crew_id`           | UUID                 | PK                      | 这条关联记录的唯一标识符。                             | 演职员记录ID | `'c1d2e3f4-a5b6-c7d8-e9f0-a1b2c3d4e5f6'` |
| `movie_id`          | UUID                 | FK -> Movies(movie_id)  | 关联的电影ID。                                         | 电影ID       | `'f0e9d8c7-b6a5-4321-fedc-ba9876543210'` |
| `person_id`         | UUID                 | FK -> People(person_id) | 关联的参与人ID。                                       | 参与人ID     | `'a1b2c3d4-e5f6-7890-1234-567890abcdef'` |
| `role`              | ENUM(...)            | NOT NULL                | 定义参与人在这部电影中的职责，如 'Director', 'Actor'。 | 职责/角色    | `'Actor'`                                |
| `character_name`    | VARCHAR(255)         |                         | 如果 `role` 是 'Actor'，此字段记录其扮演的角色名称。   | 角色名       | `'Cobb'`                                 |
"""
用户数据模型 — 所有数据库操作都在这里
======================================
这个文件是"数据访问层"（Data Access Layer），只负责跟 MySQL 打交道。
app.py 不写任何 SQL，全部调这里的函数。

面试可以说：
  - 数据库操作和接口逻辑分离
  - 更换数据库（MySQL → PostgreSQL）只需改这个文件
  - 单独 run 这个文件可以自测所有数据库操作
"""
import pymysql
from pymysql.cursors import DictCursor
from app.config import Config


def get_connection():
    """
    获取数据库连接
    --------------
    把 pymysql.connect() 想象成"给 MySQL 拨电话"：
      - 你要告诉它打给谁（host）、用什么账号（user/password）、进哪个库（database）
      - 它返回一个"连接对象"（conn），相当于电话接通了
      - 拿着 conn 才能执行 SQL

    返回值：连接对象，后面用 conn.cursor() 来执行 SQL
    """
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,          # ← 别忘了 port，之前漏了
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
    )
    return conn


def init_db():
    """
    创建 users 表，如果表已经存在就跳过
    -------------------------------------
    CREATE TABLE IF NOT EXISTS = 表不存在才建，存在就什么都不做
    所以反复调用不会报错
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ 数据库表 users 创建成功")
    finally:
        conn.close()


def get_all_users():
    """查全部用户，按 ID 倒序排列（最新添加的在最上面）"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conn.close()


def get_user_by_id(user_id):
    #                ↑ 不叫 id，避免覆盖 Python 内置的 id() 函数
    """
    按 ID 查单个用户
    用 %s 占位符传参，防止 SQL 注入攻击
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def create_user(name, email, phone=None):
    """
    新增用户
    返回新插入记录的自增 ID（lastrowid）
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)",
            (name, email, phone),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_user(user_id, name=None, email=None, phone=None):
    #               ↑ user_id 而不是 id
    """
    修改用户
    只更新传了值的字段，没传的不改
    返回 True（修改成功）或 False（用户不存在 / 没有字段要改）
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 第 1 步：检查哪些字段传了值，拼装 SQL 片段
        fields = []
        values = []
        if name is not None:
            fields.append("name = %s")
            values.append(name)
        if email is not None:
            fields.append("email = %s")
            values.append(email)
        if phone is not None:
            fields.append("phone = %s")
            values.append(phone)

        # 第 2 步：如果什么都没传，直接返回 False
        if not fields:
            return False

        # 第 3 步：把 user_id 放到 values 最后（对应 WHERE 里的 %s）
        values.append(user_id)

        # 第 4 步：拼 SQL
        # SET 后面的字段名是自己代码生成的，用 f-string 安全
        # WHERE 后面的 user_id 是外部传入的，必须用 %s 占位符
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"

        # 第 5 步：执行
        # 例：sql = "UPDATE users SET name = %s, phone = %s WHERE id = %s"
        #     values = ["张三丰", "13800138000", 1]
        cursor.execute(sql, values)
        conn.commit()

        # 第 6 步：判断是否修改成功
        # rowcount = 影响了多少行，>0 说明改到了，=0 说明 id 不存在
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_user(user_id):
    """删除用户，返回 True（删除成功）或 False（用户不存在）"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ===== 自测：直接运行 python app/models.py 执行下面的测试 =====
if __name__ == "__main__":
    # 先清旧表再建新表（保证测试环境干净）
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    conn.close()

    init_db()

    print("测试插入...")
    new_id = create_user("张三", "zhangsan@test.com", "13800138000")
    print(f"  新增用户 ID: {new_id}")

    print("测试查询全部...")
    users = get_all_users()
    print(f"  共 {len(users)} 条")

    print("测试查询单个...")
    user = get_user_by_id(new_id)
    print(f"  {user}")

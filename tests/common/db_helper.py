"""
数据库校验工具（测试专用）
========================
这个模块是测试框架的"第三只眼"——不依赖被测应用的 models.py，
而是独立直连 MySQL 做数据落地校验。

面试可以说：绕过被测应用，直接查数据库确认数据真实写入，
不以接口返回为准，以数据库状态为准。
"""
import logging
import pymysql
from pymysql.cursors import DictCursor
from tests.common.config import DB_CONFIG

logger = logging.getLogger(__name__)


class DatabaseChecker:
    """数据库校验器 — 每次操作独立建立/关闭连接"""

    def __init__(self):
        self.config = DB_CONFIG

    def get_connection(self):
        """建立数据库连接"""
        try:
            conn = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset=self.config["charset"],
                cursorclass=DictCursor,
            )
            logger.debug("MySQL 连接成功: %s:%s/%s",
                         self.config["host"], self.config["port"],
                         self.config["database"])
            return conn
        except Exception:
            # 连不上数据库是测试环境的大问题，值得记一条 ERROR
            logger.error("MySQL 连接失败: %s:%s — 请确认 MySQL 已启动",
                         self.config["host"], self.config["port"])
            raise

    # ────────── 查询操作 ──────────

    def get_user_by_id(self, user_id):
        """按 ID 查用户，返回字典或 None"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_all_users(self):
        """查全部用户，按 ID 倒序"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY id DESC")
            return cursor.fetchall()
        finally:
            conn.close()

    def user_exists(self, user_id):
        """判断用户是否存在"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM users WHERE id = %s",
                (user_id,),
            )
            result = cursor.fetchone()
            return result["cnt"] > 0
        finally:
            conn.close()

    def count_users(self):
        """统计用户总数"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cnt FROM users")
            result = cursor.fetchone()
            return result["cnt"]
        finally:
            conn.close()

    # ────────── 清理操作 ──────────

    def delete_user_by_id(self, user_id):
        """物理删除用户（测试清理用，不走 API）"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def cleanup_by_email_keyword(self, keyword):
        """按邮箱关键字批量清理测试数据"""
        logger.info("批量清理测试数据，关键字: '%s'", keyword)
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM users WHERE email LIKE %s",
                (f"%{keyword}%",),
            )
            conn.commit()
            count = cursor.rowcount
            logger.info("共删除 %s 条数据", count)
            return count
        finally:
            conn.close()

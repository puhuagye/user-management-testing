"""
共享 fixtures — 所有测试目录都能用
====================================
放在 tests/ 目录下，pytest 会把这里的 fixture 提供给
tests/api/ 和 tests/ui/ 两个子目录的测试用例。

面试可以说：公共 fixture 放在父级 conftest.py，
子目录各自放自己特有的 fixture，避免重复定义。
"""
import logging
import pytest
import requests
from tests.common.db_helper import DatabaseChecker

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """pytest 启动时执行：关掉 selenium 和 urllib3 的 DEBUG 日志"""
    for name in ['selenium', 'urllib3', 'websocket']:
        logging.getLogger(name).setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def db():
    """
    数据库校验器 — session 级别，整个测试只创建一次
    API 测试和 UI 测试共用同一个 DatabaseChecker 实例
    """
    checker = DatabaseChecker()
    yield checker


@pytest.fixture(scope="function")
def api_session():
    """
    HTTP 请求会话 — function 级别，每个用例独立
    用 Session 复用 TCP 连接、统一 headers
    """
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="function")
def base_url():
    """被测地址 fixture — API 和 UI 测试共用"""
    from tests.common.config import TEST_BASE_URL
    return TEST_BASE_URL


@pytest.fixture(scope="function")
def created_ids(db):
    """
    测试数据自动清理 fixture
    ------------------------
    用法：用例里 created_ids.append(new_id)，跑完自动从数据库删除。
    即使用例中途 assert 失败，只要登记了就能清理。
    """
    ids = []
    yield ids
    # ── 清理阶段（yield 之后）──
    if ids:
        logger.info("清理测试数据: %s", ids)
        for user_id in ids:
            try:
                db.delete_user_by_id(user_id)
            except Exception:
                logger.warning("清理 ID=%s 失败（可能已被手动删除）", user_id)

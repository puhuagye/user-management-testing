"""
测试环境配置
============
和 app/config.py 一样从 config.yaml 读取配置。
环境变量可以覆盖 YAML 里的值。

面试可以说：
  测试配置和被测应用配置共用同一个 config.yaml，
  切换环境（比如换一台服务器跑测试）只需改一个文件。
"""
import os
import yaml
from pathlib import Path

# ── 定位 config.yaml（项目根目录） ──
# Path(__file__)     = tests/common/config.py
# .parent             = tests/common/
# .parent             = tests/
# .parent             = 项目根目录
_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def _load_yaml_config(path):
    """加载 YAML 配置文件，返回字典。文件不存在返回空字典。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"⚠️ 配置文件 {path} 不存在，使用默认值")
        return {}


_yaml_config = _load_yaml_config(_CONFIG_PATH)


def _get(key_path, env_name, default=None):
    """
    按优先级取值：环境变量 > YAML > 默认值
    和 app/config.py 里是同一套逻辑。
    """
    # 第一优先级：环境变量
    env_val = os.getenv(env_name)
    if env_val is not None:
        return env_val

    # 第二优先级：YAML 配置文件
    keys = key_path.split(".")
    val = _yaml_config
    try:
        for k in keys:
            val = val[k]
        return val
    except (KeyError, TypeError):
        pass

    # 第三优先级：默认值
    return default


# ===== 被测系统地址 =====
TEST_BASE_URL = _get("test.base_url", "TEST_BASE_URL", "http://127.0.0.1:5000")

# ===== 数据库连接信息 =====
# 供 DatabaseChecker 使用（db_helper.py 里 import 这个字典）
DB_CONFIG = {
    "host": _get("database.host", "DB_HOST", "127.0.0.1"),
    "port": int(_get("database.port", "DB_PORT", 3307)),
    "user": _get("database.user", "DB_USER", "root"),
    "password": _get("database.password", "DB_PASSWORD", "1111"),
    "database": _get("database.database", "DB_NAME", "user_management"),
    "charset": "utf8mb4",
}

# ===== 自测：直接运行查看当前配置 =====
if __name__ == "__main__":
    print(f"配置文件: {_CONFIG_PATH}")
    print(f"   文件存在: {_CONFIG_PATH.exists()}")
    print(f"被测地址: {TEST_BASE_URL}")
    print(f"数据库: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

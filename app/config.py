"""
应用配置模块
============
从项目根目录的 config.yaml 读取配置，环境变量可以覆盖。
优先级：环境变量 > config.yaml > 代码默认值（最低）

面试可以说：
  配置集中管理在 config.yaml，app 和测试两边共用同一份。
  切换环境只需改一个文件，环境变量覆盖机制保证了安全性（密码不放 yaml）。
"""
import os
import yaml
from pathlib import Path

# ── 定位 config.yaml（项目根目录下） ──
# Path(__file__) = 当前文件的路径（app/config.py）
# .parent          = 上一级目录（app/）
# .parent          = 再上一级（项目根目录）
# / "config.yaml"  = 拼接路径
_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def _load_yaml_config(path):
    """
    加载 YAML 配置文件，返回字典。
    文件不存在时返回空字典（不抛异常，保证程序能启动）。
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"⚠️ 配置文件 {path} 不存在，使用默认值")
        return {}


# 加载配置（模块级别，只读一次）
_yaml_config = _load_yaml_config(_CONFIG_PATH)


def _get(key_path, env_name, default=None):
    """
    按优先级取配置值：环境变量 > YAML > 默认值
    -----------------------------------------
    key_path: YAML 里的路径，比如 "database.host"
    env_name: 环境变量名，比如 "DB_HOST"
    default:  兜底默认值

    示例：_get("database.host", "DB_HOST", "127.0.0.1")
          → 先查 os.environ["DB_HOST"]
          → 没有就查 yaml["database"]["host"]
          → 还没有就用 "127.0.0.1"
    """
    # 第一优先级：环境变量
    env_val = os.getenv(env_name)
    if env_val is not None:
        return env_val

    # 第二优先级：YAML 配置文件
    keys = key_path.split(".")  # "database.host" → ["database", "host"]
    val = _yaml_config
    try:
        for k in keys:
            val = val[k]  # 逐层取值：yaml["database"]["host"]
        return val
    except (KeyError, TypeError):
        pass

    # 第三优先级：代码默认值
    return default


class Config:
    """
    Flask 应用配置类
    ================
    所有配置项通过 _get() 取值，支持三层优先级：
      环境变量 > config.yaml > 代码默认值
    """

    # ── 数据库连接 ──
    DB_HOST = _get("database.host", "DB_HOST", "127.0.0.1")
    DB_PORT = int(_get("database.port", "DB_PORT", 3307))
    DB_USER = _get("database.user", "DB_USER", "root")
    DB_PASSWORD = _get("database.password", "DB_PASSWORD", "1111")
    DB_NAME = _get("database.database", "DB_NAME", "user_management")

    # ── Flask 自身配置 ──
    SECRET_KEY = _get("app.secret_key", "SECRET_KEY", "dev-secret-key-2024")
    HOST = _get("app.host", "FLASK_HOST", "0.0.0.0")
    PORT = int(_get("app.port", "FLASK_PORT", 5000))
    # YAML 会把 true 解析成 Python 布尔值，env 返回字符串
    # str() 统一转成字符串再比较，两种情况都能处理
    DEBUG = str(_get("app.debug", "FLASK_DEBUG", True)).lower() == "true"


# ── 自测：直接运行查看当前配置 ──
if __name__ == "__main__":
    c = Config()
    print(f"配置文件: {_CONFIG_PATH}")
    print(f"   文件存在: {_CONFIG_PATH.exists()}")
    print(f"数据库: {c.DB_USER}@{c.DB_HOST}:{c.DB_PORT}/{c.DB_NAME}")
    print(f"服务地址: {c.HOST}:{c.PORT}")
    print(f"调试模式: {c.DEBUG}")

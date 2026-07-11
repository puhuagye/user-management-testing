import logging  # Python 自带的日志模块，不用 pip 安装
import os  # 用来创建目录

from app.app import app
from app.models import init_db

# ===== 日志配置 =====
# 确保 logs 目录存在（不存在就创建）
os.makedirs("logs", exist_ok=True)
#  ↑ makedirs = 创建目录 | exist_ok=True = 目录已存在也不报错

# basicConfig = 一键配置，设置一次，整个项目都能用
logging.basicConfig(
    level=logging.DEBUG,  # 记录 DEBUG 及以上所有级别
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    #        ↑ 时间        ↑ 级别(左对齐占8格)  ↑ 日志内容
    datefmt="%H:%M:%S",  # 时间只显示 时:分:秒，简洁
    handlers=[
        logging.StreamHandler(),  # 输出到终端（跟之前一样）
        logging.FileHandler("logs/app.log", encoding="utf-8"),  # 写到 logs 目录
    ],
)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

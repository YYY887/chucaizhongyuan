import logging
from pathlib import Path

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志格式
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# 配置根日志
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format
)

# 运行日志
file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# 错误日志
error_handler = logging.FileHandler(log_dir / "error.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))

# 获取logger
logger = logging.getLogger("app")
logger.addHandler(file_handler)
logger.addHandler(error_handler)

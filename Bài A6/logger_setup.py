"""Cấu hình ghi log: vừa in ra màn hình, vừa ghi vào file trong thư mục logs/."""
import logging
import sys
from datetime import datetime
from pathlib import Path

LOGGER_NAME = "bangdiem"


def setup_logging(log_dir: Path) -> Path:
    """Tạo logger, trả về đường dẫn file log của lần chạy này."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # tránh in trùng nếu gọi setup nhiều lần

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return log_file

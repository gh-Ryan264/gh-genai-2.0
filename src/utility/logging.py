import logging
import time
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent  # src/utility/logging.py -> src/
LOG_DIR = BASE_DIR / "Logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_path = LOG_DIR / filename
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.propagate = False

    return logger

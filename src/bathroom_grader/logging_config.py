"""App-wide logging setup: plain text, to both the console and a rotating log file.

Call configure_logging() once, early (main.py does this at import time). Elsewhere in the
app, just do `logger = logging.getLogger(__name__)` and log normally - it inherits this
config since it's set on the root logger.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from bathroom_grader.config import settings

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
MAX_LOG_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # keep app.log + app.log.1/.2/.3, then rotate the oldest out


def configure_logging() -> None:
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_path, maxBytes=MAX_LOG_FILE_BYTES, backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    root_logger.handlers = [console_handler, file_handler]

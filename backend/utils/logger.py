import logging
import os
from datetime import datetime
from options import *

# Create a logger instance
logger = logging.getLogger("nhentai_archiver")

# --- add custom FRONTEND level between DEBUG (10) and INFO (20)
FRONTEND_LEVEL = 15
logging.addLevelName(FRONTEND_LEVEL, "FRONTEND")

def frontend(self, msg, *args, **kwargs):
    """
    Log a message with FRONTEND level; only emitted when logger level is DEBUG.
    """
    # Only log if overall level is DEBUG (to hide during INFO/WARNING)
    if self.level <= logging.DEBUG:
        self._log(FRONTEND_LEVEL, msg, args, **kwargs)
# attach to Logger
logging.Logger.frontend = frontend

# --- Configure base logger level from env ---
level_map = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARNING}
logger.setLevel(level_map.get(LOG_LVL, logging.DEBUG))

# --- Determine handler levels ---
log_file_lvl    = level_map.get(LOG_FILE_LVL,    logging.DEBUG)
log_console_lvl = level_map.get(LOG_CONSOLE_LVL, logging.DEBUG)

# Only configure handlers once
if not logger.handlers:

    # Formatter for log messages
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Ensure logs directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    log_filename = datetime.now().strftime(f"{LOG_DIR}/log_%Y%m%d_%H%M%S.log")

    # File handler: logs written to file at file-level
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(log_file_lvl)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler: printed to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_console_lvl)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional: mute excessive logging from other libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger.propagate = False

# Example usage
if __name__ == "__main__":
    logger.info("Logger initialized.")
    logger.debug("Debug message for troubleshooting.")
    logger.frontend("Frontend-specific log shown only in DEBUG mode.")
    logger.warning("Something might be off...")
    logger.error("This is an error message.")

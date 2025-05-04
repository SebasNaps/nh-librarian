# backend/logger_listener.py
from eventbus import emitter
from backend.utils.logger import logger  # your existing logger


def on_frontend_log(entry):
    logger.frontend(f"[FRONTEND] {entry}")

def on_frontend_log_warning(entry):
    logger.warning(f"[FRONTEND] {entry}")

def on_frontend_log_error(entry):
    logger.error(f"[FRONTEND] {entry}")

# Subscribe
emitter.on('frontend.log', on_frontend_log)
emitter.on('frontend.log.warning', on_frontend_log_warning)
emitter.on('frontend.log.error', on_frontend_log_error)


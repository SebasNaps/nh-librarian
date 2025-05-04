# app/__init__.py

import options

### Has to be here, otherwise there will be a recursion depth but!!!
# https://stackoverflow.com/questions/76449394/eventlet-monkey-patch-cause-maximum-recursion-depth-exceeded-in-ssl-py
if not options.RUN_AS_STANDALONE_PYTHON:
    import eventlet  # important!
    eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
import os


app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

if options.RUN_AS_STANDALONE_PYTHON:
    socketio = SocketIO(app, cors_allowed_origins="*")
else:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

def create_app():
    

    # configure upload folder, etc.
    from .routes import init_routes
    from .sockets import init_sockets

    import backend.logger_listener
    # import backend.progress_manager
    # import backend.task_controller

    os.makedirs(options.DATA_DIR, exist_ok=True)
    os.makedirs(options.CBZ_DIR, exist_ok=True)
    os.makedirs(options.DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(options.LOG_DIR, exist_ok=True)
    os.makedirs(options.CONFIG_DIR, exist_ok=True)

    init_routes(app)
    socketio.init_app(app)
    init_sockets(socketio)

    return app

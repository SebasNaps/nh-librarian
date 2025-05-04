import options
from app import create_app, socketio

app = create_app()
app.secret_key = "change_this_to_a_real_secret"  # for flash messages


if __name__ == '__main__':
    
    if options.RUN_AS_STANDALONE_PYTHON:
        port = 5002
    else:
        port = 5000
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)


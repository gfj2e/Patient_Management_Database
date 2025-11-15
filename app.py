from app import create_app
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO(app, cors_allowed_origins = '*')

from app.socketio_events import init_socketio_events
init_socketio_events(socketio)

if __name__== "__main__":
    socketio.run(app, debug = True)

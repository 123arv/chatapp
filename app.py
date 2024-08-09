from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send
import gevent
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    return render_template('chat.html', username=username, room=room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    app.logger.debug(f'{username} has joined the room: {room}')
    send(f'{username} has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    app.logger.debug(f'{username} has left the room: {room}')
    send(f'{username} has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    username = data['username']
    app.logger.debug(f"Received message from {username} in room {room}: {msg}")
    send(f'{username}: {msg}', to=room)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

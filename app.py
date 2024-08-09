from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, send
import eventlet
import os

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    return render_template('chat.html', username=username, room=room)

@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(f'{username} has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    username = data['username']
    send(f'{username}: {msg}', to=room)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

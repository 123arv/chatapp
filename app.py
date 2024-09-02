from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
import gevent

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
    
    # Redirect to home if username or room is missing
    if not username or not room:
        return redirect(url_for('index'))

    return render_template('chat.html', username=username, room=room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    
    join_room(room)
    send({'msg': f'{username} has entered the room.', 'username': 'System', 'type': 'system'}, to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    
    leave_room(room)
    send({'msg': f'{username} has left the room.', 'username': 'System', 'type': 'system'}, to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    username = data['username']
    msg_type = data.get('type', 'text')  # default to 'text' if 'type' is not provided

    # Broadcast the message to the room
    send({'msg': msg, 'username': username, 'type': msg_type}, to=room)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

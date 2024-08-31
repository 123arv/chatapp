from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, send
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
socketio = SocketIO(app, async_mode='gevent')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    return render_template('chat.html', username=username, room=room)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = f'/uploads/{filename}'
        return jsonify({'success': True, 'file_url': file_url})
    return jsonify({'success': False, 'error': 'File type not allowed'}), 400

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
    send({'username': username, 'msg': msg, 'type': 'text'}, to=room)

@socketio.on('file')
def handle_file(data):
    room = data['room']
    file_url = data['file_url']
    username = data['username']
    send({'username': username, 'file_url': file_url, 'type': 'file'}, to=room)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

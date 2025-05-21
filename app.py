from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins='*')

clients = {}
rooms = {}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@socketio.on('register')
def handle_register(data):
    username = data['username']
    clients[username] = request.sid
    emit('system_message', {'message': f"{username} registered."}, broadcast=True)

@socketio.on('host_room')
def handle_host(data):
    room = data['room']
    username = data['username']
    if room not in rooms:
        rooms[room] = []
    if username not in rooms[room]:
        rooms[room].append(username)
    join_room(room)
    emit('system_message', {'message': f"{username} created and joined {room}"}, to=room)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    if room not in rooms:
        rooms[room] = []
    if username not in rooms[room]:
        rooms[room].append(username)
    join_room(room)
    emit('system_message', {'message': f"{username} joined {room}"}, to=room)

@socketio.on('leave_room')
def handle_leave(data):
    room = data['room']
    username = data['username']
    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
        leave_room(room)
        emit('system_message', {'message': f"{username} left {room}"}, to=room)

@socketio.on('send_message')
def handle_send(data):
    room = data['room']
    message = data['message']
    sender = data['sender']
    emit('receive_message', {'message': message, 'sender': sender}, to=room)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    print(f"TuxChat is running at http://localhost:{port} 🚀")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

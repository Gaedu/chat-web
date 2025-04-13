from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit  # type: ignore

app = Flask(__name__)
socketio = SocketIO(app)

connected_users = {}

@app.route('/')
def index():
    return render_template('index.html')

def get_real_ip():
    # Render 등의 프록시 환경에서 클라이언트 IP 가져오기
    forwarded_for = request.headers.get('X-Forwarded-For', None)
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'

@socketio.on('connect')
def handle_connect():
    ip = get_real_ip()
    connected_users[request.sid] = ip
    emit('update_user_count', {'user_count': len(connected_users)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)
    emit('update_user_count', {'user_count': len(connected_users)}, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    nickname = data.get('nickname') or 'ㅇㅇ'
    message = data.get('message') or ''
    ip = get_real_ip()
    ip_prefix = '.'.join(ip.split('.')[:2])
    formatted = f"{nickname}({ip_prefix}): {message}"
    emit('receive_message', {'message': formatted}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=590, debug=True)

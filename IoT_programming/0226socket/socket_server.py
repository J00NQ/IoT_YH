import socket
import threading
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
data_history = []
last_command = "OFF" # LED 상태 저장용

# 소켓 서버 함수
def run_socket_server():
    host = '0.0.0.0'
    port = 5001
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    while True:
        client_soc, addr = server_socket.accept()
        try:
            # 1. ESP32로부터 데이터 받기 (온습도)
            data = client_soc.recv(1024).decode('utf-8')
            if data:
                temp, hum = data.split(',')
                data_history.append({"temperature": temp, "humidity": hum})
                if len(data_history) > 20: data_history.pop(0)

            # 2. ESP32에게 명령 보내기 (LED 상태)
            # 수신 직후 응답으로 명령을 보냅니다.
            client_soc.send(last_command.encode('utf-8'))
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_soc.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    return jsonify(data_history)

# LED 제어를 위한 API 경로
@app.route('/control_led', methods=['POST'])
def control_led():
    global last_command
    status = request.json.get('status') # 'ON' 또는 'OFF'
    last_command = status
    return jsonify({"result": "success", "status": last_command})

if __name__ == '__main__':
    threading.Thread(target=run_socket_server, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
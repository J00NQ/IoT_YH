from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
data_history = []
MQTT_BROKER = "localhost" # 라즈베리 파이 자신
MQTT_TOPIC_DATA = "room/data"
MQTT_TOPIC_LED = "room/light"

# MQTT 메시지를 받았을 때 실행되는 콜백 함수
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        # 데이터가 "온도,습도" 형태라고 가정
        temp, hum = payload.split(',')
        data_history.append({"temperature": temp, "humidity": hum})
        if len(data_history) > 20: data_history.pop(0)
        print(f"MQTT Received: {temp}, {hum}")
    except Exception as e:
        print(f"Error parsing MQTT: {e}")

# MQTT 클라이언트 설정
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.subscribe(MQTT_TOPIC_DATA)
mqtt_client.loop_start() # 별도 쓰레드 없이 배경에서 계속 작동함

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    return jsonify(data_history)

@app.route('/control_led', methods=['POST'])
def control_led():
    status = request.json.get('status').lower() # 'on' 또는 'off'
    # Flask 서버가 MQTT 발행자(Publisher)가 되어 ESP32에게 명령 전송
    mqtt_client.publish(MQTT_TOPIC_LED, status)
    return jsonify({"result": "success", "status": status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
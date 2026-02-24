from flask import Flask, render_template, jsonify, request

from datetime import datetime

app = Flask(__name__)

latest_sensor = {"temperature": None, "humidity": None}

@app.route('/')

def index():

    now = datetime.now().strftime("%Y년%m월%d일 %H:%M")

    return render_template("index.html", sensor=latest_sensor, now=now)

@app.route('/api/sensor', methods=['POST'])

def receive_sensor():

    global latest_sensor

    data = request.get_json()

    latest_sensor = {

        "temperature": data.get("temperature"),

        "humidity": data.get("humidity")

    }

    print(f"수신: 온도={latest_sensor['temperature']}, 습도={latest_sensor['humidity']}")

    return jsonify({"status": "ok"})

@app.route('/api/sensor', methods=['GET'])

def get_sensor():

    return jsonify(latest_sensor)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, jsonify
from datetime import datetime
import serial
import time

app = Flask(__name__)

def read_sensor():

    """Arduino에서 센서 데이터 1개를 읽어 딕셔너리로 반환"""

    try:

        ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=2)

        time.sleep(2)

        line = ser.readline().decode("utf-8").strip()

        ser.close()

        humidity, celsius = line.split(',')

        return {

            "temperature": float(celsius),

            "humidity":    float(humidity)

        }

    except Exception as e:

        print("센서 오류:", e)

        return {"temperature": None, "humidity": None}


@app.route('/')

def index():
    data = read_sensor()

    return render_template("index.html", sensor=data)

    # data = {"temperature": 28.1, "humidity": 60.5}
    # return render_template("index.html", sensor=data)
    # records = [

    #     # {"temperature": 25.3, "humidity": 60.5},

    #     # {"temperature": 27.1, "humidity": 58.2},

    #     # {"temperature": 29.4, "humidity": 55.0},

    #     # {"temperature": 23.8, "humidity": 65.3},

    #     # {"temperature": 21, "humidity": 60}

    # ]
    # now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

    # return render_template("index.html", records=records, now=now)


@app.route('/api/sensor')

def api_sensor():

    data = {"temperature": 25.3, "humidity": 60.5}

    return jsonify(data)

if __name__ == '__main__':

    app.run(debug=True)

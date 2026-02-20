import pymysql

from flask import Flask, render_template

app = Flask(__name__)

def get_connection():

    """MariaDB 연결 객체를 반환하는 함수"""

    return pymysql.connect(
        host="localhost",
        user="pi",
        password="test1234",
        database="sensor_db",
        charset="utf8mb4"
    )

@app.route('/')

def index():

    conn   = get_connection()

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM sensor_data ORDER BY recorded_at DESC LIMIT 10")

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return render_template("index.html", records=rows)

@app.route('/save')

def save():

    """가짜 센서 데이터를 DB에 저장 (나중에 실제 Serial 데이터로 교체)"""

    temperature = 25.3

    humidity    = 60.5

    conn   = get_connection()

    cursor = conn.cursor()

    sql = "INSERT INTO sensor_data (temperature, humidity) VALUES (%s, %s)"

    cursor.execute(sql, (temperature, humidity))

    conn.commit()   # ← INSERT/UPDATE/DELETE 후 반드시 필요

    cursor.close()

    conn.close()

    return "저장 완료!"

if __name__ == '__main__':

    app.run(host="0.0.0.0", debug=True)   # host="0.0.0.0"

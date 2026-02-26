from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 데이터를 저장할 리스트 (실제 운영 시 DB 사용 권장)
data_history = []

@app.route('/')
def index():
    # 차트를 보여줄 메인 페이지
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    # ESP32로부터 데이터를 받음
    data = request.get_json()
    if data:
        data_history.append(data)
        # 메모리 관리를 위해 최근 20개만 유지
        if len(data_history) > 20:
            data_history.pop(0)
        return {"status": "success"}, 200
    return {"status": "fail"}, 400

@app.route('/get_data', methods=['GET'])
def get_data():
    # 웹 브라우저가 차트 업데이트를 위해 데이터를 요청할 때 사용
    return jsonify(data_history)

if __name__ == '__main__':
    # 외부 접속 허용을 위해 0.0.0.0으로 실행
    app.run(host='0.0.0.0', port=5000)
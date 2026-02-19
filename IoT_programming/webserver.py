from flask import Flask
from flask import request
from markupsafe import escape 

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route("/hello")
def hello():
    name = request.args.get("name", "Flask")
    return f"Hello, {escape(name)}!"

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True )
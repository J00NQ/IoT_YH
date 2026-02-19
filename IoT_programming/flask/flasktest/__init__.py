from flask import Flask, url_for, request 

app = Flask(__name__)

@app.route('/')
@app.route('/hello/<name>')
def hello_world(name):
    return 'Hello %s!' % name

@app.route('/object/<int:id>')
def callback(id):
    assert isinstance(id, int)
    return url_for('callback', id=id)

with app.test_request_context():
    print(url_for('callback', id=1))

@app.route('/login', methods=['GET'])
def show_loginform():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''
def check_login(username, password):
    if username=="pi" and password=="raspberry":
        return True
    else :
        return False 

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if check_login(username, password):
        return "<p>Your login information was correct.</p>"
    else:
        return "<p>Login failed.</p>"
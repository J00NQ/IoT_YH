#-*- coding: utf-8 -*-
from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit, join_room
import json, time, os

app = Flask(__name__, template_folder="./templates")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', engineio_logger=True)

@socketio.on('join_web')
def join_web(message):
    print('on_join_web');
    join_room('WEB');

@socketio.on('join_dev')
def join_dev(message):
    print('on_join_dev');
    join_room('DEV');

@socketio.on('led')
def controlled(message):
    l = message['data']
    if l == "ON":
        emit('led_control', {'data': 'on'}, room='DEV');
    elif l == "OFF":
        emit('led_control', {'data': 'off'}, room='DEV');
    
@socketio.on('events')
def getevents(message):
    print(f'>>> Received from ESP32: {message}')
    emit('dht_chart', {'data': message}, room='WEB');

@socketio.on_error()
def chat_error_handler(e):
    print('An error has occurred: ' + str(e))

@app.route('/dhtchart')
def dht11chart():
    return render_template("dhtchart.html")

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
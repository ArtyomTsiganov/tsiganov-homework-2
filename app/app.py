from flask import Flask, abort
from modules import ShannonFano
import os

import time

APP_TOKEN = os.environ.get('APP_TOKEN')
APP_MESSAGE = os.environ.get('APP_MESSAGE')
FLASK_HOST = os.environ.get('FLASK_HOST') 
FLASK_PORT =  os.environ.get('FLASK_PORT')

POD_NAME = os.environ.get('POD_NAME');

app = Flask(__name__)

start_time = time.perf_counter()
is_alive = True
is_ready = True

@app.get("/")
def hello():
    return f"Pod Name: {POD_NAME} Version: v1.5"
    f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Shannon Fano</title>
</head>
<body>
    <h2>Shannon Fano Decrypter</h2>
    <ul>
        <li><b>Author:</b> Artyom Tsiganov</li>
        <li><b>Project:</b> Shannon Fano decrypter</li>
        <li><b>Token Configured:</b> {len(APP_TOKEN) == 32}</li>
        <li><b>App Message:</b> {APP_MESSAGE}</li>
        <li><b>Pod Name:</b> {POD_NAME}</li>
    </ul>
</body>
</html>"""


@app.get("/live")
def live_proba():
    execution_time = time.perf_counter() - start_time
    if (execution_time > 10 and is_alive):
        return f"live: {is_alive}"

    abort(503, description=f"i am so dead!")


@app.get("/ready")
def ready_proba():
    execution_time = time.perf_counter() - start_time
    if (execution_time > 10 and is_ready):
        return f"ready: {is_ready}"

    abort(503, description=f"not ready")

@app.get("/you-are-death")
def death_proba():
    global is_alive
    is_alive = False
    return "you are no longer alive"

@app.get("/not-ready")
def not_ready_proba():
    global is_ready
    is_ready = False
    return "you are no longer ready"

@app.get("/ready-again")
def ready_again_proba():
    global is_ready
    is_ready = True
    return "you are ready again !";

@app.post('/encode-data')
def encode_bytes():
    try:
        data = request.get_data()
        result = ShannonFano.encode(data) # encode(string: bytes) -> bytes:
        return result
    except Exception as e:
        abort(400, description=f"Encoding error: {e}")

@app.post('/decode-data')
def decode_bytes():
    try:
        data = request.get_data()
        result = ShannonFano.decode(data) # decode(string: bytes) -> bytes:
        return result
    except Exception as e:
        abort(400, description=f"Encoding error: {e}")


app.run(host=FLASK_HOST, port=FLASK_PORT)

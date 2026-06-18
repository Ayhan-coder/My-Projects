import os
from flask import Flask, request, jsonify, make_response
import redis
import time

app = Flask(__name__)

SERVER_ID = os.environ.get('SERVER_ID', 'unknown')
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

local_count = 0

def add_headers(response):
    """Add required headers to every response."""
    response.headers['X-Server-Id'] = SERVER_ID
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
def root():
    global local_count
    local_count += 1
    global_count = r.incr('global_count')
    resp = jsonify({
        "server_id": SERVER_ID,
        "local_count": local_count,
        "global_count": global_count
    })
    return add_headers(resp)

@app.route('/health')
def health():
    resp = jsonify({"status": "ok", "server_id": SERVER_ID})
    return add_headers(resp)

@app.route('/store')
def store():
    key = request.args.get('key')
    value = request.args.get('value')
    if not key or not value:
        resp = jsonify({"error": "missing key or value"})
        return add_headers(resp), 400
    r.set(key, value)
    resp = jsonify({
        "stored": True,
        "key": key,
        "value": value,
        "server_id": SERVER_ID
    })
    return add_headers(resp)

@app.route('/get')
def get_val():
    key = request.args.get('key')
    if not key:
        resp = jsonify({"error": "missing key"})
        return add_headers(resp), 400
    value = r.get(key)
    resp = jsonify({
        "key": key,
        "value": value,
        "server_id": SERVER_ID
    })
    return add_headers(resp)

@app.route('/slow')
def slow():
    seconds_str = request.args.get('seconds')
    if not seconds_str:
        resp = jsonify({"error": "missing seconds"})
        return add_headers(resp), 400
    try:
        seconds = int(seconds_str)
    except ValueError:
        resp = jsonify({"error": "invalid seconds"})
        return add_headers(resp), 400
    if seconds < 0:
        seconds = 0
    elif seconds > 10:
        seconds = 10
    time.sleep(seconds)
    resp = jsonify({
        "server_id": SERVER_ID,
        "slept": seconds
    })
    return add_headers(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

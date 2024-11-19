from flask import Flask, request, jsonify, render_template, send_from_directory, Response
import datetime
import os
from dotenv import load_dotenv
import sqlite3
import json
app = Flask(__name__)
load_dotenv()
# 요청을 저장할 리스트
request_log = []
# 접근 비밀번호 설정
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD")
DATABASE = 'logs.db'
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            path TEXT,
            cookies TEXT,
            headers TEXT,
            body TEXT,
            timestamp TEXT,
            ip TEXT,
            query_string TEXT
        )
    ''')
    conn.commit()
    conn.close()
with app.app_context():
    init_db()
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
# 모든 요청을 기록하는 미들웨어
@app.before_request
def log_request_info():
    log_entry = {
        "method": request.method,
        "path": request.path,
        "cookies": str(request.cookies.to_dict()),
        "headers": json.dumps(dict(request.headers)),  # JSON 문자열로 변환
        "body": request.get_data(as_text=True),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "query_string": "&".join([f"{key}={value}" for key, value in request.args.items()])
    }
    #requests와 favicon.ico로 오는 요청은 무시함(아마 이건쓸대없을듯)
    if log_entry['path'] != '/requests' and log_entry['path'] != '/favicon.ico':
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO request_log (method, path, cookies, headers, body, timestamp, ip, query_string)
            VALUES (:method, :path, :cookies, :headers, :body, :timestamp, :ip, :query_string)
        ''', log_entry)
        conn.commit()
        conn.close()


# 요청 기록을 조회하는 엔드포인트
@app.route('/requests', methods=['GET'])
def get_requests():
    # 비밀번호 확인
    auth = request.authorization
    if not auth or auth.password != ACCESS_PASSWORD:
        return Response(
            "Could not verify your access level for that URL.\n"
            "You have to login with proper credentials", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM request_log ORDER BY id DESC')
    logs = c.fetchall()
    conn.close()
    keys = ['id', 'method', 'path', 'cookies', 'headers', 'body', 'timestamp', 'ip', 'query_string']
    logs = [dict(zip(keys, log)) for log in logs]
    return render_template('requests.html', logs=logs)


@app.route('/reset', methods=['POST'])
def reset_requests():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # 모든 로그 삭제
    c.execute('DELETE FROM request_log')
    conn.commit()
    conn.close()
    return jsonify({"message": "All request logs have been reset."}), 200


# 기본 엔드포인트 (리퀘스트 빈으로 동작)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    return jsonify({
        "message": "Request received and logged",
        "method": request.method,
        "path": request.path
    }), 200
    

from flask import Flask, request, jsonify, render_template, send_from_directory, Response
import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
# 요청을 저장할 리스트
request_log = []

# 접근 비밀번호 설정
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD")

# 모든 요청을 기록하는 미들웨어
@app.before_request
def log_request_info():
    log_entry = {
        "method": request.method,
        "path": request.path,
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "query_string": "&".join([f"{key}={value}" for key, value in request.args.items()])
    }
    #requests와 favicon.ico로 오는 요청은 무시함(아마 이건쓸대없을듯)
    if log_entry['path'] != '/requests' and log_entry['path'] != '/favicon.ico':
        request_log.append(log_entry)
    print(f"Logged Request: {log_entry}")

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
    return render_template('requests.html', logs=request_log)
@app.route('/reset', methods=['POST'])
def reset_requests():
    global request_log
    request_log = []
    return jsonify({"message": "Request log has been reset."}), 200


# 기본 엔드포인트 (리퀘스트 빈으로 동작)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    return jsonify({
        "message": "Request received and logged",
        "method": request.method,
        "path": request.path
    }), 200
    


if __name__ == '__main__':
    app.run()
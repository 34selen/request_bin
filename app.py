from flask import Flask, request, jsonify,render_template
import datetime

app = Flask(__name__)

# 요청을 저장할 리스트
request_log = []

# 모든 요청을 기록하는 미들웨어
@app.before_request
def log_request_info():
    log_entry = {
        "method": request.method,
        "path": request.path,
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if(log_entry['path'] !='/requests' and log_entry['path'] !='/favicon.ico'):
        request_log.append(log_entry)
    print(f"Logged Request: {log_entry}")

# 요청 기록을 조회하는 엔드포인트
@app.route('/requests', methods=['GET'])
def get_requests():
    return  render_template('requests.html', logs=request_log)

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
    app.run(debug=True)

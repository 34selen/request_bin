# 베이스 이미지
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt requirements.txt
COPY . .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn 실행 (포트 5000)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

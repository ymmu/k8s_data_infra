# Alpine Linux 기반의 Python 이미지를 사용
FROM python:3.10-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 필요할 경우 requirements.txt를 복사하고 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 파이썬 스크립트를 복사
COPY data_crud.py .

# 환경 변수 설정
ENV MYSQL_USER=admin
ENV MYSQL_PASSWORD=admin
ENV MYSQL_HOST=mysql
ENV MYSQL_DATABASE=my_database
ENV MYSQL_PORT=3306

# 컨테이너가 시작될 때 실행할 명령어
CMD ["python", "data_crud.py"]
import pymysql
import random
import time
import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
import sys
import traceback

# 로깅 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, 'data_crud.log')
logger = logging.getLogger('data_crud')
logger.setLevel(logging.INFO)

# 파일 핸들러 설정
file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# 스트림 핸들러 설정 (표준 출력용)
stream_handler = logging.StreamHandler(sys.stdout)
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)


class DataCrud:

    def __init__(self):
        # MySQL 데이터베이스에 연결
        db_config = {
        'user': os.environ['MYSQL_USER'],
        'password': os.environ['MYSQL_PASSWORD'],
        'host': os.environ['MYSQL_HOST'],
        'database': os.environ['MYSQL_DATABASE'],
        # 'port': int(os.environ['MYSQL_PORT'])
    }
        self.connection = pymysql.connect(**db_config)
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        self.crud_functions = {
            'insert': self.insert_data,
            'update': self.update_data,
            'delete': self.delete_data
        }
    
    def close(self):
        self.cursor.close()
        self.connection.close()

    # 데이터 생성 함수 
    def generate_random_data(self):
        created_at = datetime.datetime.now()
        updated_at = created_at
        user_num = random.randint(1, 10**10)
        return { # 새로운 데이터 생성
            'name': f'User{user_num}',
            'email': f'user{user_num}@example.com',
            'comment': f'업데이트 횟수:{0}',
            'created_at': created_at,
            'updated_at': updated_at
        }

    def select_data(self):
        self.cursor.execute("""SELECT * FROM users ORDER BY RAND() LIMIT 1;""")
        return self.cursor.fetchall()

    def insert_data(self):
        data = self.generate_random_data()
        self.cursor.execute("INSERT INTO users (name, email, comment, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)", (data['name'], data['email'], data['comment'], data['created_at'], data['updated_at']))
        self.connection.commit()
        logger.info(f"데이터 삽입: {data['name']}")

    def update_data(self):
        data = self.select_data()
        logger.info(f"업데이트할 데이터: {data}")
        if data:
            data = data[0]
            comment = f"업데이트 횟수:{int(data['comment'].split(':')[1]) + 1}"
            self.cursor.execute("UPDATE users SET comment = %s, updated_at = %s WHERE id = %s", (comment, data['updated_at'], data['id']))
            self.connection.commit()
            logger.info(f"데이터 업데이트: ID {data['id']}, 새 코멘트: {comment}")
        else:
            logger.info("데이터가 없습니다.")

    def delete_data(self):
        data = self.select_data()
        logger.info(f"삭제할 데이터: {data}")
        if data:
            data = data[0]
            self.cursor.execute("DELETE FROM users WHERE id = %s", (data['id'],))
            self.connection.commit()
            logger.info(f"데이터 삭제: ID {data['id']}")
        else:
            logger.info("데이터가 없습니다.")

    def get_random_crud_function(self):
        weights = [0.3, 0.5, 0.2]  # 각각의 숫자에 대한 가중치
        return random.choices(list(self.crud_functions.values()), weights=weights)[0]


if __name__ == "__main__":

    data_crud = DataCrud()

    try:

        while True:
            function = data_crud.get_random_crud_function()
            logger.info(f"실행할 함수: {function.__name__}")
            function()
            time.sleep(5)  # 5초 대기

    except KeyboardInterrupt:
        logger.info("프로그램 중지...")
    except Exception as e:
        error_msg = f"예기치 않은 오류 발생: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
    finally:
        data_crud.close()
        sys.exit(0)

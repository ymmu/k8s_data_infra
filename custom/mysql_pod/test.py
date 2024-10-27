# test_calculator.py
import unittest
from data_crud import DataCrud
import os

class TestCalculator(unittest.TestCase):

    def setUp(self):
        # 환경 변수에서 MySQL 설정
        os.environ['MYSQL_USER'] = 'admin'
        os.environ['MYSQL_PASSWORD'] = 'admin'
        os.environ['MYSQL_HOST'] = 'localhost'
        os.environ['MYSQL_DATABASE'] = 'my_database'
        os.environ['MYSQL_PORT'] = '3306'
        self.data_crud = DataCrud()

    def test_insert_data(self):
        try:
            self.data_crud.insert_data()
        except Exception as e:
            self.fail(f"예기치 않은 오류 발생: {str(e)}")

    def test_update_data(self):
        try:
            self.data_crud.update_data()
        except Exception as e:
            self.fail(f"예기치 않은 오류 발생: {str(e)}")

    def test_delete_data(self):
        
        try:
            self.data_crud.delete_data()
        except Exception as e:
            self.fail(f"예기치 않은 오류 발생: {str(e)}")

    def test_select_data(self):
        try:
            self.data_crud.select_data()
        except Exception as e:
            self.fail(f"예기치 않은 오류 발생: {str(e)}")

if __name__ == '__main__':
    unittest.main()

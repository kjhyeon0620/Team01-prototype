

import os
from tinydb import TinyDB,Query


# src/db.json 으로 데이터베이스 파일 위치 고정 
__current_dir = os.path.dirname(os.path.abspath(__file__))
database_file_path = os.path.join(__current_dir, "db.json")

db = TinyDB(database_file_path)


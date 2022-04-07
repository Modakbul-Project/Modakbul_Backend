from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.users

# db 테스트
db.users.insert_one({'name': '홍길동', 'gender': 'M', 'email':'hong@google.com'})

from flask import Flask, render_template, jsonify, request, redirect, session, url_for, json
from pymongo import MongoClient
from bson.json_util import ObjectId
from authlib.integrations.flask_client import OAuth
import os
app = Flask(__name__)

# json 시리얼 오류 처리용 인코더
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

client = MongoClient('localhost',27017)
db = client.capston
app.json_encoder = MyEncoder


# 페이지 라우팅
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/manage')
def manage():
    return render_template('manage.html')

@app.route('/meeting')
def meeting():
    return render_template('meeting.html')

@app.route('/myPage')
def myPage():
    return render_template('myPage.html')

# POST API(참여 요청)
@app.route('/join', methods=['POST'])
def join():
    data = request.get_json()
    print(data)
    print(type(data))
    # json_convert = json.loads(data,ensure_ascii=False)
    # print(json_convert)
    # print(type(json_convert))
    db.users.insert_one(data)
    print(data)
    print(type(data))
    # json_convert = json.loads(data)
    # print('json_convert : ' + json_convert)

    return jsonify(result = "success", result2 = data)

@app.route('/member', methods=['POST'])
def member():
    data = request.get_json()
    print(data)

    return jsonify(result = "success", result2= data)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

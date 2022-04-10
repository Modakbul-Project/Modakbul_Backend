from flask import Flask, render_template, redirect, request, url_for, json
from pymongo import MongoClient
from bson.json_util import ObjectId


# json 시리얼 오류 처리용 인코더
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


# db 연동
conn = MongoClient('127.0.0.1')
# db 생성
db = conn.Test
app = Flask(__name__)


@app.route('/',  methods=['GET'])
def main():
    # collection 생성
    collect = db.mongoKakao

    # select 쿼리값 results에 저장
    results = collect.find()
    return render_template('main.html', data=results)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        # collection 생성
        collect = db.mongoUser

        #form에서 가져온 데이터들
        username = request.form["username"]
        userid = request.form["userid"]
        password = request.form["password1"]
        gender = request.form["gender"]
        birth = request.form["birth"]
        email = request.form["email"]
        phone = request.form["phone"]

        # document 생성
        doc = {
            "username": username,
            "userid": userid,
            "password": password,
            "gender": gender,
            "birth": birth,
            "email": email,
            "phone": phone,
            "meeting": "",
            "role": ""
        }
        #userid가 db에 있는지 검색
        result = list(collect.find({'userid': userid}))

        # userid가 db에 없으면(중복되지 않는다면) insert쿼리 실행
        if not result:
            # document 삽입
            collect.insert_one(doc)
            return redirect(url_for('main'))
        # userid가 중복될 경우 다시 signup페이지로 이동
        else:
            return redirect(url_for('signup'))
    else: #메소드가 GET일 경우
        return render_template('signup.html')


@app.route('/login')
def login():
    # collection 생성
    collect = db.mongoUser
    return render_template('login.html')


@app.route('/input')
@app.route('/input<int:num>')
def inputTest(num=None):
    return render_template('input.html', num=num)


@app.route('/calculate', methods=['POST'])
def calculate(num=None):
    if request.method == 'POST':
        temp = request.form['num']
    else:
        temp = None
    return redirect(url_for('inputTest', num=temp))


@app.route('/mongo', methods=['GET'])
def mongoTest():
    # collection 생성
    collect = db.mongoTest
    results = collect.find()
    return render_template('mongo.html', data=results)


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == "POST":
        # collection 생성
        collect = db.mongoTest

        name = request.form["name"]
        contents = request.form["contents"]

        # document 생성
        doc = {
            "name": name,
            "contents": contents
        }
        # document 삽입
        collect.insert_one(doc)
        return redirect(url_for('write'))
    else:
        return render_template('write.html')


@app.route('/kakao2db', methods=['GET', 'POST'])
def kakao2db():
    if request.method == "POST":
        # collection 생성
        collect = db.mongoKakao

        address = request.form["address"]
        title = request.form["title"]
        topic = request.form["topic"]
        recruit_num = request.form["recruit_num"]
        contents = request.form["contents"]
        lat = request.form["lat"]
        lng = request.form["lng"]

        # document 생성
        doc = {
            "address": address,
            "title": title,
            "topic": topic,
            "recruit_num": recruit_num,
            "contents": contents,
            "lat": lat,
            "lng": lng
        }
        # document 삽입
        collect.insert_one(doc)
        return redirect(url_for('kakao2db'))
    else:
        return render_template('kakao2db.html')


@app.route('/kakao',  methods=['GET'])
def kakao():
    # collection 생성
    collect = db.mongoKakao

    # select 쿼리값 results에 저장
    results = collect.find()
    return render_template('kakao.html', data=results)


if __name__ == '__main__':
    app.run(debug=True)

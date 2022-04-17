from flask import Flask, render_template, redirect, request, url_for, json, session, flash
from pymongo import MongoClient
from bson.json_util import ObjectId
from markupsafe import escape
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'secretkey'  # secret_key는 서버상에 동작하는 어플리케이션 구분하기 위해 사용하고 복잡하게 만들어야 합니다.
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60) # 로그인 지속시간을 정합니다. 60분(1시간)


# json 시리얼 오류 처리용 인코더
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app.json_encoder = MyEncoder

# db 연동
conn = MongoClient('127.0.0.1')
# db 생성
db = conn.Test


@app.route('/', methods=['GET'])
def main():
    # collection 생성
    collect = db.mongoKakao

    # select 쿼리값 results에 저장
    results = collect.find()
    return render_template('main.html', data=results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # request.method를 통해 GET & POST 인지 확인함.
        # collection 생성
        collect = db.mongoUser

        #폼에서 ID/PW 가져오기
        userid = request.form['id']
        password = request.form['password']

        # 폼에서 입력받은 userid와 password값이 있는지 db에서 조회
        result = list(collect.find({'userid': userid, 'password': password}))
        username = result[0]['username']
        #userid와 password값이 db에 있다면 세션에 값입력
        if result:
            session['userid'] = userid
            session['password'] = password
            session['username'] = username
            return redirect(url_for('main'))
        else: #userid와 password값이 db에 없을 경우 (id 또는 pw가 틀렸을 경우)
            msg = "아이디와 비밀번호를 다시 확인해주세요"
            flash(msg) #리턴할 때 같이 넘겨줄 메시지
            redirect(url_for('login'))
    #GET일 경우
    return render_template('login.html')


@app.route('/logout')
def logout():
    #세션에서 값 삭제
    session.pop('userid', None)
    return redirect(url_for('main'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        # collection 생성
        collect = db.mongoUser

        # form에서 가져온 데이터들
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
        # userid가 db에 있는지 검색
        result = list(collect.find({'userid': userid}))

        # userid가 db에 없으면(중복되지 않는다면) insert쿼리 실행
        if not result:
            # document 삽입
            collect.insert_one(doc)
            return redirect(url_for('main'))
        # userid가 중복될 경우 다시 signup페이지로 이동
        else:
            msg = "이미 존재하는 아이디입니다."
            flash(msg) #리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('signup'))
    else:  # 메소드가 GET일 경우
        return render_template('signup.html')


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
        return redirect(url_for('main'))
    else:
        return render_template('kakao2db.html')


@app.route('/kakao', methods=['GET'])
def kakao():
    # collection 생성
    collect = db.mongoKakao

    # select 쿼리값 results에 저장
    results = collect.find()
    return render_template('kakao.html', data=results)


if __name__ == '__main__':
    app.run(debug=True)

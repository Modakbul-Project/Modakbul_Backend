from flask import Flask, render_template, redirect, request, url_for, json, session, flash
from pymongo import MongoClient
from bson.json_util import ObjectId
from authlib.integrations.flask_client import OAuth
from markupsafe import escape
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'secretkey'  # secret_key는 서버상에 동작하는 어플리케이션 구분하기 위해 사용하고 복잡하게 만들어야 합니다.
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60) # 로그인 지속시간을 정합니다. 60분(1시간)

oauth = OAuth(app)
with open('./static/client_secret.json') as f:
    json_data=json.load(f)


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


@app.route('/notice/<id>') #게시판 or 공지사항에 작성된 글 읽기 페이지
def notice(id=None):
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoBoard
        #db에서 id와 일치하는 글 검색
        result = list(collect.find({'_id': ObjectId(id)}))
        result = result[0]
        return render_template('read.html', data=result)
    else: #로그인 안되어 있을 경우
        return redirect('/login')


@app.route('/write', methods=['GET', 'POST']) #게시판 or 공지사항 글쓰기 페이지
def write():
    if 'userid' in session:  # 로그인 여부 확인
        if request.method == "POST":
            # collection 생성
            collect = db.mongoBoard

            # form에서 가져온 데이터들
            notice = request.form["notice"]
            title = request.form["title"]
            contents = request.form["contents"]
            userid = session['userid']
            username = session['username']

            # document 생성
            doc = {
                "notice": notice,
                "title": title,
                "contents": contents,
                "userid": userid,
                "username": username,
                "create_time": str(now.date())
            }
            collect.insert_one(doc)
            return redirect(url_for('meet_page'))
        # GET일 경우
        return render_template('write.html')
    else: #로그인 안되어 있을 경우
        return redirect('/login')


@app.route('/meet')
def meet_page():
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoBoard

        # select 쿼리값 results에 저장
        results = collect.find()
        return render_template('meetpage.html', data=results)
    else:
        return redirect('/login')


@app.route('/meetadmin')
def meet_admin():
    if 'userid' in session:  # 로그인 여부 확인
        return render_template('meetpage.html')
    else:
        return redirect('/login')


@app.route('/find_pw', methods=['GET', 'POST'])
def find_pw():
    if request.method == "POST":
        # collection 생성
        collect = db.mongoUser

        # form에서 가져온 데이터들
        userid = request.form["userid"]
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]

        # 회원정보가 db에 있는지 검색
        result = list(collect.find({'userid': userid, 'username': username, 'email': email, 'phone': phone}))

        if result:  # 회원 정보가 있을 때
            password = result[0]['password']
            msg = username + "님의 비밀번호는 " + password + "입니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('login'))
        else:  # 회원정보가 없을 때
            msg = "회원정보와 일치하는 비밀번호가 없습니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('find_pw'))
    # GET일 경우
    return render_template('find_pw.html')


@app.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == "POST":
        # collection 생성
        collect = db.mongoUser

        # form에서 가져온 데이터들
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]

        # 회원정보가 db에 있는지 검색
        result = list(collect.find({'username': username, 'email': email, 'phone': phone}))

        if result: #회원 정보가 있을 때
            userid = result[0]['userid']
            msg = username+"님의 아이디는 "+userid+"입니다."
            flash(msg) #리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('login'))
        else: #회원정보가 없을 때
            msg = "회원정보와 일치하는 아이디가 없습니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('find_id'))
    #GET일 경우
    return render_template('find_id.html')


@app.route('/mypage')
def my_page():
    if 'userid' in session:  # 로그인 여부 확인
        return render_template('mypage.html')
    else:
        return redirect('/login')


@app.route('/google/')
def google():
    GOOGLE_CLIENT_ID = json_data['web']['client_id']
    GOOGLE_CLIENT_SECRET = json_data['web']['client_secret']
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    print(redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = token.get('userinfo')
    if user:
        session['userid'] = user.email
        session['username'] = user.name
        session['profile'] = user.picture
    return redirect('/')


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

        #userid와 password값이 db에 있다면 세션에 값입력
        if result:
            username = result[0]['username']
            profile = "./static/user.png"
            session['userid'] = userid
            session['password'] = password
            session['username'] = username
            session['profile'] = profile
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


if __name__ == '__main__':
    app.run(debug=True)

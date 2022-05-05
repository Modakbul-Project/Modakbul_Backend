from flask import Flask, render_template, redirect, request, url_for, json, session, flash, jsonify
from pymongo import MongoClient
from bson.json_util import ObjectId
from authlib.integrations.flask_client import OAuth
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename

now = datetime.now()

app = Flask(__name__)
app.secret_key = 'secretkey'  # secret_key는 서버상에 동작하는 어플리케이션 구분하기 위해 사용하고 복잡하게 만들어야 합니다.
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)  # 로그인 지속시간을 정합니다. 60분(1시간)
app.config['JSON_AS_ASCII'] = False

oauth = OAuth(app)
with open('./static/client_secret.json') as f:
    json_data = json.load(f)


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
    collect = db.mongoMeeting

    # select 쿼리값 results에 저장
    results = collect.find()

    return render_template('main.html', data=results)


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

        if result:  # 회원 정보가 있을 때
            userid = result[0]['userid']
            msg = username + "님의 아이디는 " + userid + "입니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('login'))
        else:  # 회원정보가 없을 때
            msg = "회원정보와 일치하는 아이디가 없습니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('find_id'))
    # GET일 경우
    return render_template('find_id.html')


@app.route('/mypage')
def my_page():
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoUser
        meeting_collect = db.mongoMeeting

        userid = session['userid']
        # 회원정보가 db에 있는지 검색
        result = list(collect.find({'userid': userid}))
        meet = result[0]['meeting']

        meetList = list()
        meetInfo = list()

        for i in meet:
            if i != "":
                meetList.append(i)

        for i in meetList:
            meetInfo.append(meeting_collect.find({'meet_name': i}))

        return render_template('test.html', meetInfo=meetInfo)
    else:
        return redirect('/login')


@app.route('/makepage', methods=['GET', 'POST'])
def make_page():
    if 'userid' in session:  # 로그인 여부 확인
        if request.method == "POST":
            # collection 생성
            collect = db.mongoMeeting
            user_collect = db.mongoUser

            f = request.files["meet_profile"]
            meet_profile = f.filename
            meet_name = request.form["meet_name"]
            meet_title = request.form["meet_title"]
            location = request.form["location"]
            category = request.form["category"]
            headcount = request.form["headcount"]
            currentcount = 1
            address = request.form["address"]
            meetDetail = request.form["meetDetail"]
            tags = request.form["tags"]
            lat = request.form["lat"]
            lng = request.form["lng"]
            leader_id = session['userid']
            leader_name = session['username']
            done = False  # 모집중-(done: False), 모집완료-(done: True)

            tag_arr = tags.split('#')  # 태그들이 저장된 배열

            # document 생성
            doc = {
                "meet_name": meet_name,
                "leader_id": leader_id,
                "leader_name": leader_name,
                "meet_title": meet_title,
                "location": location,
                "category": category,
                "headcount": headcount,
                "currentcount": currentcount,
                "address": address,
                "meetDetail": meetDetail,
                "tags": tag_arr,
                "lat": lat,
                "lng": lng,
                "done": done
            }

            if meet_profile:  # form에서 넘어온 profile 값이 있다면
                f.save(
                    './static/meet_profile/' + secure_filename(meet_profile))  # 모임 프로필 이미지 파일 저장 (경로: static/meet_profile/)
                doc.update({'meet_profile': meet_profile})
                session['meet_profile'] = './static/meet_profile/' + meet_profile


            # user테이블에서 모임장의 meeting에 새로 만든 모임 추가 (배열에 값을 추가할 때는 $push 사용)
            user_collect.update_one({'userid': session['userid']}, {'$push': {"meeting": meet_name}})
            # document 삽입
            collect.insert_one(doc)

            redirect(url_for('my_page'))
        # GET일 경우
        return render_template('makemeet.html')
    else:
        return redirect('/login')


@app.route('/pfedit', methods=['GET', 'POST'])
def profile_edit():
    if 'userid' in session:  # 로그인 여부 확인
        if request.method == "POST":
            # collection 생성
            collect = db.mongoUser
            meeting_collect = db.mongoMeeting

            # form에서 값이 넘어오면 변수에 값 할당
            # 넘어오지 않는다면 null값 할당
            f = request.files["profile"]
            profile = f.filename
            username = request.form["username"]
            introduce = request.form["introduce"]

            doc = {}

            if profile:  # form에서 넘어온 profile 값이 있다면
                f.save('./static/profile/' + secure_filename(profile))  # 프로필 이미지 파일 저장 (경로: static/profile/)
                doc.update({'profile': profile})
                session['profile'] = './static/profile/' + profile
            if username:  # form에서 넘어온 username 값이 있다면
                doc.update({'username': username})
                session['username'] = username
            if introduce:  # form에서 넘어온 introduce 값이 있다면
                doc.update({'introduce': introduce})

            # 변경된 값 db에 반영
            collect.update_one({'userid': session['userid']}, {'$set': doc})
            meeting_collect.update_one({'leader_id': session['userid']}, {'$set': {"leader_name": username}})
            redirect(url_for('my_page'))

        # GET일 경우
        return render_template('profileedit.html')
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

        # 폼에서 ID/PW 가져오기
        userid = request.form['id']
        password = request.form['password']

        # 폼에서 입력받은 userid와 password값이 있는지 db에서 조회
        result = list(collect.find({'userid': userid, 'password': password}))

        # userid와 password값이 db에 있다면 세션에 값입력
        if result:
            username = result[0]['username']
            profile = 'static/profile/' + result[0]['profile']
            session['userid'] = userid
            session['password'] = password
            session['username'] = username
            session['profile'] = profile
            return redirect(url_for('main'))
        else:  # userid와 password값이 db에 없을 경우 (id 또는 pw가 틀렸을 경우)
            msg = "아이디와 비밀번호를 다시 확인해주세요"
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            redirect(url_for('login'))
    # GET일 경우
    return render_template('login.html')


@app.route('/logout')
def logout():
    # 세션에서 값 삭제
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
            "profile": "./static/profile/user.png",
            "username": username,
            "userid": userid,
            "password": password,
            "gender": gender,
            "birth": birth,
            "email": email,
            "phone": phone,
            "introduce": "",
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
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect(url_for('signup'))
    else:  # 메소드가 GET일 경우
        return render_template('signup.html')


@app.route('/notice/<id>')  # 게시판 or 공지사항에 작성된 글 읽기 페이지
def notice(id=None):
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoBoard
        # db에서 id와 일치하는 글 검색
        result = list(collect.find({'_id': ObjectId(id)}))
        result = result[0]
        return render_template('read.html', data=result)
    else:  # 로그인 안되어 있을 경우
        return redirect('/login')


@app.route('/write', methods=['GET', 'POST'])  # 게시판 or 공지사항 글쓰기 페이지
def write():
    if 'userid' in session:  # 로그인 여부 확인
        if request.method == "POST":
            # collection 생성
            collect = db.mongoBoard

            # form에서 가져온 데이터들
            title = request.form["title"]
            contents = request.form["contents"]
            userid = session['userid']
            username = session['username']

            # document 생성
            doc = {
                "title": title,
                "contents": contents,
                "userid": userid,
                "username": username,
                "create_time": str(now.date())
            }
            collect.insert_one(doc)
            return redirect(url_for('meet_page'))
        # GET일 경우
        return render_template('makenotice.html')
    else:  # 로그인 안되어 있을 경우
        return redirect('/login')


@app.route('/meet/<id>')
def meet_page(id=None):
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoBoard
        meeting_collect = db.mongoMeeting

        # 모임 정보
        meetInfo = meeting_collect.find({'_id': ObjectId(id)})

        # select 쿼리값 results에 저장
        results = collect.find()
        return render_template('meetpage.html', data=results, meetInfo=meetInfo)
    else:
        return redirect('/login')


@app.route('/meetadmin')
def meet_admin():
    if 'userid' in session:  # 로그인 여부 확인
        return render_template('meetpage.html')
    else:
        return redirect('/login')


@app.route('/delete/<id>')
def delete(id=None):
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoBoard
        # db에서 id와 일치하는 글 검색
        result = list(collect.find({'_id': ObjectId(id)}))
        if result[0]['userid'] == session['userid']:  # 작성자와 로그인한 사용자가 일치하면
            collect.delete_one({'_id': ObjectId(id)})  # 해당 게시글 삭제
            return redirect(url_for('meet_page'))
        else:  # 작성자와 로그인한 사용자가 일치하지 않으면
            msg = "삭제 권한이 없습니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect('/notice/' + id)
    else:  # 로그인 안되어 있을 경우
        return redirect('/login')


@app.route('/edit/<id>', methods=['GET', 'POST'])  # 게시판 or 공지사항에 작성된 글 읽기 페이지
def edit(id=None):
    if 'userid' in session:  # 로그인 여부 확인
        # collection 생성
        collect = db.mongoBoard

        if request.method == "POST":
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
            collect.update_one({'_id': ObjectId(id)}, {'$set': doc})
            return redirect(url_for('meet_page'))

        # GET일 경우
        # db에서 id와 일치하는 글 검색
        result = list(collect.find({'_id': ObjectId(id)}))
        if result[0]['userid'] == session['userid']:  # 작성자와 로그인한 사용자가 일치하면
            result = result[0]
            return render_template('edit.html', data=result)
        else:  # 작성자와 로그인한 사용자가 일치하지 않으면
            msg = "수정 권한이 없습니다."
            flash(msg)  # 리턴할 때 같이 넘겨줄 메시지
            return redirect('/notice/' + id)

    else:  # 로그인 안되어 있을 경우
        return redirect('/login')


# POST API(모임 등록)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db.meetings.insert_one(data)

    return jsonify(result = "success", result2 = data)


if __name__ == '__main__':
    app.run(debug=True)

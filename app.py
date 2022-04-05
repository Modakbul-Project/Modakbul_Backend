from flask import Flask, render_template, redirect, request, url_for
from pymongo import MongoClient

# db 연동
conn = MongoClient('127.0.0.1')

# db 생성
db = conn.Test

# collection 생성
collect = db.mongoKakao

app = Flask(__name__)


@app.route('/mypage')
def my_page():
    return 'This is My Page'


@app.route("/")
@app.route('/<int:num>')
def inputTest(num=None):
    return render_template('main.html', num=num)


@app.route('/calculate', methods=['POST'])
def calculate(num=None):
    if request.method == 'POST':
        temp = request.form['num']
    else:
        temp = None
    return redirect(url_for('inputTest', num=temp))


@app.route('/mongo', methods=['GET'])
def mongoTest():
    results = collect.find()
    return render_template('mongo.html', data=results)


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == "POST":
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
    # select 쿼리값 results에 저장
    results = collect.find()
    return render_template('kakao.html', data=results)


if __name__ == '__main__':
    app.run(debug=True)

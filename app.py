from flask import Flask, render_template, jsonify, request
# jsonify, request 임포트

app = Flask(__name__)

# HTML을 주는 부분
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


@app.route('/ajax', methods=['POST'])
def ajax():
    data = request.get_json()
    print(data)

    return jsonify(result = "success", result2= data)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

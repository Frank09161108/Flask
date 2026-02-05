from flask import Flask,request,jsonify

app=Flask(__name__)

@app.route('/index')
def index():
    name=request.args.get('name')
    age=request.args.get('age')

    print('Hello')
    print(name)
    print(age)


    return 'Hello'

@app.route('/home', methods=['GET', 'POST'])
def home():
    xx = request.form.get('xx')
    yy = request.form.get('yy')

    print(xx)
    print(yy)
    json=request.json
    print(json)
    return jsonify({"status":True,'data':'成功'})
    #return jsonify({"status":False,'error':'出错'})

if __name__ == '__main__':
    app.run()
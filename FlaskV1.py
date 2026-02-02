from flask import Flask,request

app=Flask(__name__)

@app.route('/index')
def index():
    name=request.args.get('name')
    age=request.args.get('age')

    print('Hello')
    print(name)
    print(age)

    return 'Hello'

@app.route('/home')
def home():
    return 'home'

if __name__ == '__main__':
    app.run()
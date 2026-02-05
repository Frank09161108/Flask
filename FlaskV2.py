from flask import Flask,request,jsonify
import hashlib

app=Flask(__name__)

@app.route('/test', methods=['POST'])
def test():
    """
    请求体数据格式要求有
    :return:
    """
    order_string=request.json.get('order_string')
    x='aaa'
    print(type(order_string))
    if not order_string:
        return jsonify({"status": False, 'error': '请求体错误'})
    encrypt_string=order_string+'guozhch2346'
    obj=hashlib.md5(encrypt_string.encode('utf-8'))
    sign=obj.hexdigest()
    return jsonify({"status":True,'data':sign})

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000)
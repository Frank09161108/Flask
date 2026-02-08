from flask import Flask,request,jsonify
import hashlib

app=Flask(__name__)

@app.route('/test', methods=['POST'])
def test():
    """
    请求的url中需要带  /test?token=<UUID>
    请求体数据格式要求有：{order_string:"......"}
    :return:
    """
    token = request.args.get('token')
    if not token:
        return jsonify({"status": False, 'error': '认证失败'})
    user_dict=get_user_dict()
    if token not in user_dict:
        return jsonify({"status": False, 'error': '认证失败'})

    order_string=request.json.get('order_string')
    x='aaa'
    print(type(order_string))
    if not order_string:
        return jsonify({"status": False, 'error': '请求体错误'})
    encrypt_string=order_string+'guozhch2346'
    obj=hashlib.md5(encrypt_string.encode('utf-8'))
    sign=obj.hexdigest()
    return jsonify({"status":True,'data':sign,"user":user_dict[token]})

def get_user_dict():
    info_dict={}
    with open('db.txt','r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            token,name=line.split(',')
            info_dict[token]=name
    return info_dict


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000)
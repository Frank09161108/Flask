from flask import Flask,request,jsonify
import hashlib
import sqlite3

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
    conn = sqlite3.connect('my_database.db')
    cur = conn.cursor()
    table_name="user"
    sql = f"SELECT * FROM {table_name} WHERE UUID=?"
    cur.execute(sql, (token,))
    result = cur.fetchall()
    conn.close()
    if not result:
        return jsonify({"status": False, 'error': '认证失败'})

    order_string=request.json.get('order_string')
    x='aaa'
    print(type(order_string))
    if not order_string:
        return jsonify({"status": False, 'error': '请求体错误'})
    encrypt_string=order_string+'guozhch2346'
    obj=hashlib.md5(encrypt_string.encode('utf-8'))
    sign=obj.hexdigest()
    return jsonify({"status":True,'data':sign,"user":result[0][1]})

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
    # conn=sqlite3.connect('my_database.db')
    # cursor=conn.cursor()
    # users_columns = {
    #     "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    #     "name": "TEXT NOT NULL",
    #     "UUID": "TEXT UNIQUE NOT NULL",
    # }
    # table_name="user"
    # columns_sql = ", ".join([f"{col_name} {col_type}" for col_name, col_type in users_columns.items()])
    # sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
    #
    # cursor.execute(sql)
    # conn.commit()
    #
    # users_data = [
    #     {"name": "郭志超", "UUID": "de7e79d4-7813-474c-baf9-1140f57e551a"},
    #     {"name": "邱睿", "UUID": "e630cba1-795d-4dab-b0c3-de9527c4d26f"}
    # ]
    #
    # columns = ", ".join(users_data[0].keys())
    # placeholders = ", ".join(["?" for _ in users_data[0]])
    # sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    #
    # values = [tuple(item.values()) for item in users_data]
    # cursor.executemany(sql, values)
    # conn.commit()

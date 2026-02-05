import requests

res=requests.post(url='http://127.0.0.1:5000/test',
                  json={"order_string": "aaa"})

print(res.json())
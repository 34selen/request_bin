import requests

url="http://127.0.0.1:5000/zz"
cookies={
    "pw":"password",
    "aa":'bb'
}
result=requests.post(url,cookies=cookies)
print(result.text)
import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    if firebase_admin._apps:
        return firestore.client()

    firebase_config = os.getenv("FIREBASE_CONFIG")

    if firebase_config:
        # Vercel 環境變數
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
    elif os.path.exists("serviceAccountKey.json"):
        # 本地實體金鑰檔
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        raise ValueError("找不到 Firebase 金鑰：請確認 Vercel 的 FIREBASE_CONFIG 或本地 serviceAccountKey.json")

    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

app = Flask(__name__)

print("FIREBASE_CONFIG exists:", os.getenv("FIREBASE_CONFIG") is not None)

@app.route("/")
def index():
    link = "<h1>這裡是睿謙的網站20260409</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=睿謙&d=靜宜>Get傳值</a><hr>"
    link += "<a href=/account>POST</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><br><hr>"
    link += "<a href=/read3>讀取Firestore資料(根據姓名關鍵字)</a><br><hr>"
    link += "<a href=/spider1>爬取子青老師本學期課程</a><br><hr>"
    return link

@app.route("/spider1")
def spider1():
    R = ""
    url = 'https://www1.pu.edu.tw/~tcyang/course.html'
    Data = requests.get(url)
    Data.encoding='utf-8'
    # print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")

    for i in result:
        R += i.text + " " + i.get('href') + "<br>"
    return R

@app.route("/read3", methods=["GET"])
def read3():
    keyword = request.args.get("keyword", "").strip()

    # 🔹 上半部（標題 + 輸入框）
    html = """
    <h1>靜宜資管老師查詢</h1>

    <form method="get">
        請輸入老師姓名關鍵字：
        <input type="text" name="keyword" value="{keyword}">
        <input type="submit" value="查詢">
    </form>

    <hr>
    """.format(keyword=keyword)

    # 🔹 如果還沒輸入
    if keyword == "":
        return html

    # 🔹 查詢結果標題
    html += f"<h2>查詢結果（關鍵字：{keyword}）：</h2>"

    db = firestore.client()
    docs = db.collection("靜宜資管2026B").get()

    found = False

    for doc in docs:
        teacher = doc.to_dict()

        if 'name' in teacher and teacher['name'] and keyword in teacher['name']:
            name = teacher.get('name', '無資料')
            lab = teacher.get('lab', '無研究室資料')

            html += f"""
            <p>
            <span style="color:blue; font-weight:bold;">{name}</span>
            老師的研究室在 <b>{lab}</b>
            </p>
            <hr>
            """
            found = True

    if not found:
        html += "<p>抱歉，查無此關鍵字姓名之老師資料</p>"

    # 🔹 返回首頁
    html += '<br><a href="/">返回首頁</a>'

    return html
@app.route("/read")
def read():
    result = ""
    collection_ref = db.collection("靜宜資管2026B")

    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()

    for doc in docs:
        result += str(doc.to_dict()) + "<br>"

    return result


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/me")
def me():
    return render_template("20260305.html")

@app.route("/welcome",methods=["GET"])
def welcome():
    user = request.values.get("u")
    school = request.values.get("d")
    lesson = request.values.get("l")

    return render_template("welcome.html",name=user,dep=school)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    result = None

    if request.method == "POST":
        x = int(request.form["x"])
        y = int(request.form["y"])
        opt = request.form["opt"]

        if opt == "^":
            result = x ** y
        elif opt == "√":
            if y == 0:
                result = "不行"
            else:
                result = x ** (1/y)
        else:
            result = "請輸入 ^ 或 √"

    return render_template("math.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)


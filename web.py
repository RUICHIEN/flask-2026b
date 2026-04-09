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
    link += "<a href=/read>讀取Firestore資料</a><br>"
    return link

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


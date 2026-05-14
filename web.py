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
# https://jsoneditoronline.org/#right=local.matizi&left=local.monusi
@app.route("/")
def index():
    link = "<h1>這裡是睿謙的網站</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=睿謙&d=靜宜>Get傳值</a><hr>"
    link += "<a href=/account>POST</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><br><hr>"
    link += "<a href=/read3>讀取Firestore資料(根據姓名關鍵字)</a><br><hr>"
    link += "<a href=/spider1>爬取子青老師本學期課程</a><br><hr>"
    link += "<a href=/movie2>爬取即將上映電影</a><br><hr>"
    link += "<a href=/spidermovie>爬取即將上映電影到firebase</a><br><hr>"
    link += "<a href=/searchMovie>從firebase查電影</a><br><hr>"
    link += "<a href=/road>台中市十大肇事路口</a><br><hr>"
    link += "<a href=/weather>天氣預報</a><br><hr>"
    link += "<a href=/rate>本週新片進DB</a><br><hr>"
    return link

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/weather", methods=["GET"])
def weather():
    city = request.args.get("city", "").strip()
    city = city.replace("台", "臺")

    R = """
    <h1>天氣預報查詢</h1>

    <form method="get">
        請輸入縣市：
        <input type="text" name="city" value="{city}">
        <input type="submit" value="查詢">
    </form>

    <p>範例：臺中市、臺北市、高雄市</p>
    <hr>
    """.format(city=city)

    if city == "":
        R += '<br><a href="/">返回首頁</a>'
        return R

    token = "rdec-key-123-45678-011121314"
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    params = {
        "Authorization": token,
        "format": "JSON",
        "locationName": city
    }

    Data = requests.get(url, params=params)
    JsonData = json.loads(Data.text)

    locations = JsonData["records"]["location"]

    if len(locations) == 0:
        R += "<p>查無此縣市天氣資料</p>"
        R += '<br><a href="/">返回首頁</a>'
        return R

    location = locations[0]
    weatherElement = location["weatherElement"]

    weather = weatherElement[0]["time"][0]["parameter"]["parameterName"]
    rain = weatherElement[1]["time"][0]["parameter"]["parameterName"]
    minT = weatherElement[2]["time"][0]["parameter"]["parameterName"]
    feel = weatherElement[3]["time"][0]["parameter"]["parameterName"]
    maxT = weatherElement[4]["time"][0]["parameter"]["parameterName"]

    R += "<h2>" + city + " 最新天氣</h2>"
    R += "天氣狀況：" + weather + "<br>"
    R += "降雨機率：" + rain + "%<br>"
    R += "最低溫：" + minT + "°C<br>"
    R += "最高溫：" + maxT + "°C<br>"
    R += "舒適度：" + feel + "<br>"

    R += '<br><a href="/">返回首頁</a>'

    return R

@app.route("/road")
def road():
    R = "<h1>台中市十大肇事路口(113年10月)</h1>" + "<h1>作者: 王睿謙</h1><br>"
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers = {'User-Agent':'Mozilla/5.0'}

    Data = requests.get(url,headers=headers,timeout=10)
    # print(Data.text)

    JsonData = json.loads(Data.text)
    Result = ""
    for item in JsonData:
        R += item['路口名稱'] +' ,原因: '+ item['主要肇因'] + ' ,總件數: '+item['總件數']+'<br>'

    return R

@app.route("/searchMovie")
def searchMovie():
    R = ""
    keyword = request.args.get("keyword", "").strip()
    R += f"""
    <h1>電影資料庫查詢</h1>

    <form method="get">
        請輸入片名關鍵字：
        <input type="text" name="keyword" value="{keyword}">
        <input type="submit" value="查詢">
    </form>

    <hr>
    """
    if keyword == "":
        return R

    R += f"<h2>查詢結果（關鍵字：{keyword}）</h2>"

    docs = db.collection("電影").get()

    found = False

    for doc in docs:
        data = doc.to_dict()
        title = data.get("title", "")
        picture = data.get("picture", "")
        hyperlink = data.get("hyperlink", "")
        showDate = data.get("showDate", "")
        
        if keyword in title:
        # if title.startswith(keyword):
            R += f"""
            <div>
                <p><b>編號：</b>{doc.id}</p>
                <h2>{title}</h2>
                <img src="{picture}" style="width:200px;"><br>
                <a href="{hyperlink}" target="_blank">介紹頁</a><br>
                <p>上映日期：{showDate}</p>
            </div>
            <hr>
            """
            found = True

    if not found:
        R += "<p>查無符合條件的電影</p>"
    R += '<br><a href="/">返回首頁</a>'
    return R

@app.route("/spidermovie")
def spidermovie():
    R = ""

    db = firestore.client()
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    update_time=sp.find(class_="smaller09").text.replace("更新時間：","")
    result = sp.select(".filmListAllX li")

    total =0
    for item in result:
        movie_id = item.find("a").get("href").replace("/movie/","").replace("/","")
        title = item.find(class_='filmtitle').text
        picture = "http://www.atmovies.com.tw" + item.find("img").get("src")
        hyperlink = "http://www.atmovies.com.tw" + item.find("a").get("href")
        showDate=item.find(class_="runtime").text[5:15]
        total +=1
        doc = {
          "title": title,
          "picture": picture,
          "hyperlink": hyperlink,
          "showDate": showDate,
          "lastUpdate": update_time
        }

        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)
    R+= "網站最近更新日期：" + update_time + "<br>"
    R+= "總共爬取"+ str(total) +"部電影到資料庫"
    return R

@app.route("/movie2", methods=["GET"])
def movie2():
    keyword = request.args.get("keyword", "").strip()

    html = """
    <h1>即將上映電影查詢</h1>

    <form method="get">
        請輸入電影片名關鍵字：
        <input type="text" name="keyword" value="{keyword}">
        <input type="submit" value="查詢">
    </form>

    <hr>
    """.format(keyword=keyword)

    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")

    found = False

    for item in result:
        a_tag = item.find("a")
        img_tag = item.find("img")

        if a_tag and img_tag:
            title = img_tag.get("alt")
            introduce = "https://www.atmovies.com.tw" + a_tag.get("href")
            poster = "https://www.atmovies.com.tw" + img_tag.get("src")

            if keyword == "" or keyword in title:
                html += f"""
                <div style="margin-bottom:30px;">
                    <h2>
                        <a href="{introduce}" target="_blank">{title}</a>
                    </h2>

                    <img src="{poster}" alt="{title}" style="width:200px;">
                </div>
                <hr>
                """
                found = True

    if not found:
        html += "<p>查無符合條件的電影。</p>"

    html += '<br><a href="/">返回首頁</a>'

    return html

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


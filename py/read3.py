import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate("service_accountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

keyword = input("請輸入老師姓名關鍵字：")

docs = db.collection("靜宜資管2026B").get() 

found = False  # 用來判斷有沒有找到

for doc in docs:
    teacher = doc.to_dict()
    if 'name' in teacher and teacher['name'] and keyword in teacher['name']:
        name = teacher.get('name', '無資料')
        lab = teacher.get('lab', '無研究室資料')

        print(f"姓名：{name}，研究室：{lab}")
        found = True

if not found:
    print("抱歉，查無符合的老師資料")
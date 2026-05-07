import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.document("靜宜資管2026B/richien")
doc = doc_ref.get()
result = doc.to_dict()
print(result)
print(result['name'],result['lab'])
print("文件內容為：{}".format(result))
print("教師姓名："+result.get("name"))
print("教師郵件：" + result["mail"])
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate("service_accountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

keyword = '楊'

docs = db.collection("靜宜資管2026B").get() 

for doc in docs:
    teacher = doc.to_dict()
    if 'name' in teacher and keyword in teacher['name']:
        print(teacher)

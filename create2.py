import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "RII",
  "mail": "reindio4444@gmail.com",
  "lab": 888
}

doc_ref = db.collection("靜宜資管2026B").document("richien")
doc_ref.set(doc)

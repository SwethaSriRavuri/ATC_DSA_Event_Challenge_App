import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred_path = "serviceAccountKey.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

print("Cleaning Database...")
delete_collection(db.collection('participants'), 50)
delete_collection(db.collection('submissions'), 50)
print("Database Wiped Clean.")

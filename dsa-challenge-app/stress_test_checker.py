import firebase_admin
from firebase_admin import credentials, firestore
import threading
import time

# Initialize Firebase
cred_path = "serviceAccountKey.json"
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        exit(1)

db = firestore.client()

def check_status():
    pending = db.collection('submissions').where('status', '==', 'pending').count().get()[0][0].value
    running = db.collection('submissions').where('status', '==', 'running').count().get()[0][0].value
    completed = db.collection('submissions').where('status', '==', 'completed').count().get()[0][0].value
    error = db.collection('submissions').where('status', '==', 'error').count().get()[0][0].value
    
    print(f"STATUS REPORT:")
    print(f"  Pending:   {pending}")
    print(f"  Running:   {running}")
    print(f"  Completed: {completed}")
    print(f"  Error:     {error}")
    print("-" * 20)
    total = completed + error + pending + running
    print(f"  Total:      {total}")
    if total > 0:
        print(f"  Completion: {((completed+error)/total)*100:.1f}%")
    print("-" * 20)
    print(f"  Total Done: {completed + error}")

if __name__ == "__main__":
    check_status()

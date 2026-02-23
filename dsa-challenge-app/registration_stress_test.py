import firebase_admin
from firebase_admin import credentials, firestore
import threading
import time
import random

# Initialize Firebase
cred_path = "serviceAccountKey.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

NUM_USERS = 300
success_count = 0
error_count = 0
lock = threading.Lock()

def register_user(i):
    global success_count, error_count
    
    user_id = f"reg-test-{random.randint(1000, 9999)}"
    try:
        # Simulate exact payload from registration.js
        db.collection('participants').document(user_id).set({
            "name": f"Reg Test User {i}",
            "email": f"reg{i}@test.com",
            "score": 0,
            "solved": [],
            "status": "ACTIVE",
            "violations": 0,
            "start_time": firestore.SERVER_TIMESTAMP
        })
        
        with lock:
            success_count += 1
            if success_count % 50 == 0:
                print(f" -> Registered {success_count} users...")
                
    except Exception as e:
        with lock:
            error_count += 1
            print(f"ERROR registering {user_id}: {e}")

print(f"Starting Registration Stress Test: {NUM_USERS} users...")
start_time = time.time()

threads = []
for i in range(NUM_USERS):
    t = threading.Thread(target=register_user, args=(i,))
    threads.append(t)
    t.start()
    
# Wait for all
for t in threads:
    t.join()

duration = time.time() - start_time
print(f"REGISTRATION TEST COMPLETE")
print(f"Success: {success_count}")
print(f"Errors:  {error_count}")
print(f"Time:    {duration:.2f} seconds")
print(f"Rate:    {success_count/duration:.2f} registrations/sec")

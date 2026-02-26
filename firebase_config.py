
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Global DB reference
db = None

def init_firebase():
    """Execute once to initialize Firebase connection"""
    global db
    
    # Check if already initialized
    if firebase_admin._apps:
        db = firestore.client()
        return db

    # Instructions for the user:
    # 1. Update this path to point to your actual serviceAccountKey.json
    # 2. Or set the FIREBASE_CREDENTIALS env var with the JSON content
    cred_path = "serviceAccountKey.json"
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
    
    if firebase_creds_json:
        try:
            creds_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(creds_dict)
        except Exception as e:
            print(f"Error parsing FIREBASE_CREDENTIALS env var: {e}")
            return None
    elif os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        print(f"ERROR: No Firebase credentials found (missing {cred_path} and FIREBASE_CREDENTIALS env var).")
        return None

    try:
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")
        return db
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        return None

def get_db():
    if db is None:
        return init_firebase()
    return db

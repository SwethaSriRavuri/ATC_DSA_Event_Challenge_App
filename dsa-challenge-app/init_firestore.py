from firebase_config import get_db

def init_db_structure():
    db = get_db()
    if not db:
        print("❌ Cannot connect to Firestore. Check your serviceAccountKey.json")
        return

    print("🚀 Initializing Firestore Structure...")

    # 1. Create Config Collection
    config_ref = db.collection('config').document('global')
    if not config_ref.get().exists:
        config_ref.set({
            'execution_enabled': True,
            'contest_status': 'ACTIVE',
            'contest_start_time': None, # Set this when you start
            'message': 'Contest is live!'
        })
        print("✅ Created config/global")
    else:
        print("ℹ️ config/global already exists")

    # 2. Create Dummy Submission to verify worker listener
    # (Optional, just to ensure collection exists)
    # db.collection('submissions').document('_init_').set({'_hidden': True})
    
    print("\n🎉 Database Initialized!")
    print("Next Steps:")
    print("1. Run 'python worker.py' in a separate terminal.")
    print("2. Run 'python app.py' to start the web server.")

if __name__ == "__main__":
    init_db_structure()

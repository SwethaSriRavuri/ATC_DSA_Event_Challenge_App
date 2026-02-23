from backend.models import get_session, Participant, Submission, Contest, Result

def reset_db():
    """
    Manually resets the database by deleting all participant data.
    Run this function/script on the server when you want to clear test data.
    """
    session = get_session()
    print("Deleting all Results...")
    session.query(Result).delete()
    
    print("Deleting all Contest entries...")
    session.query(Contest).delete()
    
    print("Deleting all Submissions...")
    session.query(Submission).delete()
    
    print("Deleting all Participants...")
    session.query(Participant).delete()
    
    session.commit()
    session.close()
    
    # RESET FIRESTORE
    try:
        from firebase_config import db
        if db:
            print("Deleting Firestore Collections...")
            
            def delete_collection(coll_ref, batch_size):
                docs = coll_ref.limit(batch_size).stream()
                deleted = 0
                for doc in docs:
                    doc.reference.delete()
                    deleted += 1
                if deleted >= batch_size:
                    delete_collection(coll_ref, batch_size)
            
            delete_collection(db.collection('participants'), 50)
            delete_collection(db.collection('submissions'), 50)
            print("Firestore cleared.")
    except Exception as e:
        print(f"Firestore reset error: {e}")

    print("Database reset complete. All participant data removed.")

if __name__ == "__main__":
    import sys
    # Simple safety check
    confirm = input("Are you sure you want to DELETE ALL DATA? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_db()
    else:
        print("Operation cancelled.")

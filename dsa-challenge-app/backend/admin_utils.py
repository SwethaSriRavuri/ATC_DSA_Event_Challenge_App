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
    print("Database reset complete. All participant data removed.")

if __name__ == "__main__":
    import sys
    # Simple safety check
    confirm = input("Are you sure you want to DELETE ALL DATA? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_db()
    else:
        print("Operation cancelled.")

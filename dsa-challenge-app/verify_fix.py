from datetime import datetime, timedelta
from backend.service import ContestService
from backend.models import get_session, Participant, Contest, Result, init_db
import config

def verify_leaderboard_fix():
    print("Running verification for Leaderboard Fix...")
    service = ContestService()
    session = get_session()
    
    try:
        # 1. Create a dummy participant
        test_email = "test_fix@example.com"
        # Cleanup existing test data if any
        session.query(Participant).filter_by(email=test_email).delete()
        session.commit()
        
        participant_id = service.register_participant("Test Fix User", test_email, "python")
        print(f"Created Test Participant: {participant_id}")
        
        # 2. Simulate an active contest that started 5 hours ago (Duration is 2 hours)
        start_time = datetime.now() - timedelta(hours=5)
        contest = Contest(
            participant_id=participant_id,
            start_time=start_time,
            duration=config.CONTEST_DURATION,
            is_active=1,
            status='ACTIVE',
            violation_count=0
        )
        session.add(contest)
        session.commit()
        print(f"Created 'ACTIVE' contest starting 5 hours ago.")
        
        # 3. Call get_leaderboard_data() - this should trigger the fix
        print("Calling get_leaderboard_data()...")
        leaderboard = service.get_leaderboard_data()
        
        # 4. Check if the contest was finalized
        session.expire_all()
        updated_contest = session.query(Contest).filter_by(participant_id=participant_id).first()
        
        print(f"Updated Contest Status: {updated_contest.status}")
        print(f"Updated Contest Is Active: {updated_contest.is_active}")
        
        expected_end_time = start_time + timedelta(seconds=config.CONTEST_DURATION)
        # Allow small tolerance in comparison if needed, but here it should be exact
        print(f"End Time (Expected): {expected_end_time}")
        print(f"End Time (Actual):   {updated_contest.end_time}")
        
        if updated_contest.status == 'COMPLETED' and updated_contest.is_active == 0:
            actual_duration = (updated_contest.end_time - updated_contest.start_time).total_seconds()
            if int(actual_duration) == config.CONTEST_DURATION:
                print("\n✅ SUCCESS: Contest was automatically finalized and time was capped at exactly 2 hours!")
            else:
                print(f"\n❌ FAILURE: Duration was {actual_duration}s, expected {config.CONTEST_DURATION}s")
        else:
            print("\n❌ FAILURE: Contest is still active or status is incorrect")
            
        # Cleanup
        session.query(Contest).filter_by(participant_id=participant_id).delete()
        session.query(Participant).filter_by(id=participant_id).delete()
        session.commit()
        
    except Exception as e:
        print(f"Error during verification: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    verify_leaderboard_fix()

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models import get_session, Contest
import config

def finalize_all_expired_sessions():
    """Manual cleanup script to finalize and cap all expired sessions"""
    print("Starting session finalization cleanup...")
    session = get_session()
    
    try:
        active_contests = session.query(Contest).filter_by(status='ACTIVE').all()
        count = 0
        
        for contest in active_contests:
            if contest.start_time:
                elapsed = (datetime.now() - contest.start_time).total_seconds()
                if elapsed >= contest.duration:
                    # Finalize and cap at exact duration
                    contest.is_active = 0
                    contest.status = 'COMPLETED'
                    contest.end_time = contest.start_time + timedelta(seconds=contest.duration)
                    count += 1
                    print(f"Finalized Participant ID {contest.participant_id} (Duration capped at {contest.duration}s)")
        
        session.commit()
        print(f"Successfully finalized {count} sessions.")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    finalize_all_expired_sessions()

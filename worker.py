import time
import socket
import datetime
import traceback
import threading
from firebase_config import get_db, firestore
from backend.executor import get_executor
from backend.judge import Judge
from backend.problem_loader import get_test_cases, load_problem

# Worker Identity
WORKER_ID = f"{socket.gethostname()}-{int(time.time())}"
print(f"🚀 Worker Started with ID: {WORKER_ID}")

# Configuration
POLL_INTERVAL = 1  # Seconds to wait between checks
REAPER_INTERVAL = 60 # Seconds between dead job checks
TIMEOUT_THRESHOLD = 120 # Seconds before a 'running' job is considered dead

def claim_next_submission(db):
    """
    Atomic Claiming Protocol:
    1. Query for 'pending' submissions (limit 1).
    2. Use Transaction to check if it's REALLY pending.
    3. If yes, mark as 'running' + set claimedBy/claimedAt.
    """
    transaction = db.transaction()
    
    # query outside transaction for candidate (First Come First Serve)
    # We order by timestamp to be fair
    candidates = db.collection('submissions')\
        .where('status', '==', 'pending')\
        .order_by('submitted_at', direction=firestore.Query.ASCENDING)\
        .limit(1)\
        .stream()
    
    candidate = next(candidates, None)
    
    if not candidate:
        return None

    candidate_ref = db.collection('submissions').document(candidate.id)

    @firestore.transactional
    def txn_claim(transaction, doc_ref):
        snapshot = doc_ref.get(transaction=transaction)
        if not snapshot.exists:
            return None
        
        data = snapshot.to_dict()
        if data.get('status') != 'pending':
            return None # Already stolen by another worker
        
        # CLAIM IT
        transaction.update(doc_ref, {
            'status': 'running',
            'claimed_by': WORKER_ID,
            'claimed_at': firestore.SERVER_TIMESTAMP,
            'started_at_worker': datetime.datetime.now().isoformat()
        })
        return snapshot

    try:
        # returns the snapshot if successful, None otherwise
        return txn_claim(transaction, candidate_ref)
    except Exception as e:
        # Transaction failed (likely contention), just return None and retry
        # print(f"Transaction conflict: {e}")
        return None

def process_submission(db, submission_doc):
    """Execute the code and write usage results"""
    data = submission_doc.to_dict()
    doc_id = submission_doc.id
    
    print(f"⚡ Processing {doc_id} (Problem {data.get('problem_id')}) ...")
    
    try:
        problem_id = data.get('problem_id')
        code = data.get('code')
        language = data.get('language')
        
        test_cases = get_test_cases(int(problem_id))
        if not test_cases:
            raise Exception("No test cases found")
            
        executor = get_executor(language)
        input_data = test_cases[0]['input']
        expected = test_cases[0]['expected_output']
        
        # RUN CODE
        success, output, error, exec_time = executor.execute(code, input_data)
        
        # JUDGE
        passed = False
        actual = None
        
        if success:
            import json
            try:
                actual = json.loads(output) if output else None
            except:
                actual = output.strip() if output else ""
                
            judge = Judge()
            passed = judge._compare_output(actual, expected)
        
        result_data = {
            'status': 'completed',
            'completed_at': firestore.SERVER_TIMESTAMP,
            'result': {
                'success': success,
                'passed': passed,
                'error': error,
                'time': exec_time,
                'worker': WORKER_ID
            }
        }
        
        # Write Result
        db.collection('submissions').document(doc_id).update(result_data)
        print(f"✅ Finished {doc_id}: {'PASSED' if passed else 'FAILED'}")

        # Update User Score (Atomic Increment)
        if passed and data.get('type') == 'submit':
             try:
                 participant_id = data.get('participant_id')
                 prob_data = load_problem(int(problem_id))
                 marks = prob_data.get('marks', 10) if prob_data else 10
                 
                 participant_ref = db.collection('participants').document(participant_id)
                 
                 @firestore.transactional
                 def txn_update_score(transaction, pat_ref):
                     snapshot = pat_ref.get(transaction=transaction)
                     if not snapshot.exists:
                         # Initialize if missing
                         current_data = {'score': 0, 'solved': [], 'name': data.get('name', 'Unknown')}
                         transaction.set(pat_ref, current_data)
                         current_solved = []
                         current_score = 0
                     else:
                         current_data = snapshot.to_dict()
                         current_solved = current_data.get('solved', [])
                         current_score = current_data.get('score', 0)
                     
                     # Check if already solved (String vs Int safety)
                     pid_str = str(problem_id)
                     if pid_str not in [str(x) for x in current_solved]:
                         current_solved.append(int(problem_id))
                         new_score = current_score + marks
                         transaction.update(pat_ref, {
                             'solved': current_solved,
                             'score': new_score,
                             'last_active': firestore.SERVER_TIMESTAMP
                         })
                         print(f"🏆 Score Updated for {participant_id}: +{marks} (Total: {new_score})")
                     else:
                         print(f"ℹ️ Problem {problem_id} already solved by {participant_id}")
                 
                 txn_update_score(db.transaction(), participant_ref)
             except Exception as score_e:
                 print(f"⚠️ Failed to update score: {score_e}")

    except Exception as e:
        print(f"❌ Error processing {doc_id}: {e}")
        traceback.print_exc()
        db.collection('submissions').document(doc_id).update({
            'status': 'error',
            'error_message': str(e),
            'completed_at': firestore.SERVER_TIMESTAMP,
            'worker': WORKER_ID
        })

def reaper_routine(db):
    """
    Background thread to reset jobs that have been 'running' for too long.
    This handles the case where a worker (Laptop B) crashes mid-execution.
    """
    while True:
        try:
            time.sleep(REAPER_INTERVAL)
            # Find stuck jobs
            cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=TIMEOUT_THRESHOLD)
            
            stuck_query = db.collection('submissions')\
                .where('status', '==', 'running')\
                .where('claimed_at', '<', cutoff)\
                .stream()
            
            for doc in stuck_query:
                print(f"💀 Reaping stuck job: {doc.id} (Claimed by {doc.to_dict().get('claimed_by')})")
                db.collection('submissions').document(doc.id).update({
                    'status': 'pending',
                    'claimed_by': None,
                    'claimed_at': None,
                    'reap_count': firestore.Increment(1)
                })
        except Exception as e:
            print(f"Reaper Error: {e}")

def main():
    db = get_db()
    if not db:
        print("❌ Database connection failed. Please check firebase_config.py")
        return

    # Start Reaper Thread
    reaper = threading.Thread(target=reaper_routine, args=(db,), daemon=True)
    reaper.start()
    
    print("🟢 Worker is Online. Waiting for jobs...")
    
    while True:
        try:
            # Check Kill Switch
            config_doc = db.collection('config').document('global').get()
            if config_doc.exists and not config_doc.to_dict().get('execution_enabled', True):
                print("🛑 Execution Disabled by Admin. Pausing...")
                time.sleep(5)
                continue

            # 1. Try to claim a job
            submission = claim_next_submission(db)
            
            if submission:
                # 2. Process it
                process_submission(db, submission)
            else:
                # No jobs, rest a bit
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n👋 Worker shutting down...")
            break
        except Exception as e:
            print(f"Critical Worker Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

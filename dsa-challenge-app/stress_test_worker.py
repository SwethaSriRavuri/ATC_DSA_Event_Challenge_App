import firebase_admin
from firebase_admin import credentials, firestore
import time
import random
import threading

# Initialize Firebase
cred_path = "serviceAccountKey.json"
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        exit(1)

db = firestore.client()

WORKER_ID = "stress-worker-1"

def process_submission(doc_ref, doc_data):
    """Simulates processing a single submission"""
    code = doc_data.get('code', '')
    
    print(f"   [Worker] Processing {doc_ref.id} ({doc_data.get('language')})...")
    
    try:
        # SIMULATE EXECUTION
        if "while True" in code:
            # Simulate Timeout
            time.sleep(2.0) 
            result = {
                "success": False,
                "error": "TimeoutError: Execution exceeded time limit",
                "verdict": "Time Limit Exceeded"
            }
            status = "error"
        else:
            # Simulate Success
            time.sleep(0.5) # Fast simulation
            result = {
                "success": True,
                "output": "Hello World\n",
                "verdict": "Accepted"
            }
            status = "completed"
            
        # Write Result
        doc_ref.update({
            "status": status,
            "result": result,
            "processed_at": firestore.SERVER_TIMESTAMP,
            "worker_id": WORKER_ID
        })
        
        # UPDATE SCORE (Simulation)
        if status == "completed" and doc_data.get('type') == 'submit':
            part_id = doc_data.get('participant_id')
            part_ref = db.collection('participants').document(part_id)
            
            # Simple atomic increment
            part_ref.update({
                "score": firestore.Increment(10),
                "solved": firestore.ArrayUnion([doc_data.get('problem_id')]),
                "status": "COMPLETED" if random.random() > 0.9 else "ACTIVE" # occasional completion
            })
            print(f"   🏆 Score updated for {part_id}")

        print(f"   ✅ Finished {doc_ref.id} -> {status}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error processing {doc_ref.id}: {e}")
        return False

@firestore.transactional
def claim_submission(transaction, query):
    """Atomically claims a submission"""
    snapshot = query.get(transaction=transaction)
    
    if not snapshot:
        return None
    
    # Get the first doc
    doc = snapshot[0]
    
    # Double check status (though query filters it, transaction ensures it)
    if doc.get("status") != "pending":
        return None
        
    # Claim it
    transaction.update(doc.reference, {
        "status": "running",
        "claimed_by": WORKER_ID,
        "claimed_at": firestore.SERVER_TIMESTAMP
    })
    
    return (doc.reference, doc.to_dict())

def worker_loop():
    print(f"Starting Stress Worker ({WORKER_ID})...")
    print("Waiting for jobs...")
    
    jobs_processed = 0
    start_time = time.time()
    
    while True:
        try:
            # Create a query for pending jobs
            # Using transaction requires strict query
            # We fetch ONE pending job
            
            # Note: Firestore Transactions on queries can be tricky. 
            # Standard pattern: Query -> Transaction(Get(config_doc)) -> Transaction(Update)
            # But for a queue, we just need to try to claim.
            
            # Simple approach without full strict transaction for query (to avoid contention complexity in this script)
            # We will use Optimistic Locking via Preconditions if possible, or just standard transaction
            
            transaction = db.transaction()
            query = db.collection('submissions').where('status', '==', 'pending').limit(1)
            
            try:
                # Attempt to claim
                claimed = claim_submission(transaction, query)
            except Exception as e:
                # Contention error likely (someone else grabbed it)
                # print(f"Contention: {e}")
                time.sleep(0.1)
                continue
                
            if claimed:
                doc_ref, doc_data = claimed
                process_submission(doc_ref, doc_data)
                jobs_processed += 1
                
                if jobs_processed % 10 == 0:
                     elapsed = time.time() - start_time
                     print(f"📊 Processed {jobs_processed} jobs in {elapsed:.1f}s")
            else:
                # Empty queue
                time.sleep(1) # Wait before polling again
                
        except KeyboardInterrupt:
            print("\n🛑 Worker stopping...")
            break
        except Exception as e:
            print(f"Critical Worker Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    worker_loop()

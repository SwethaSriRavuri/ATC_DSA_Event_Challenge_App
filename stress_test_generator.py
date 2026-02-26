import firebase_admin
from firebase_admin import credentials, firestore
import threading
import time
import random

# Initialize Firebase
cred_path = "serviceAccountKey.json"
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        exit(1)

db = firestore.client()

NUM_USERS = 300
DURATION_SECONDS = 30  # How long the simulation runs
MAX_THREADS = 50       # Batch threads to avoid python limit

# VALID SOLUTIONS DICTIONARY (Python)
SOLUTIONS = {
    1: """def solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []""",
    2: """def solution(s):
    return s[::-1]""",
    3: """def solution(s):
    filtered = [c.lower() for c in s if c.isalnum()]
    return filtered == filtered[::-1]""",
    4: """def solution(nums, target):
    import bisect
    idx = bisect.bisect_left(nums, target)
    if idx < len(nums) and nums[idx] == target:
        return idx
    return -1""",
    5: """def solution(nums):
    current_sum = nums[0]
    max_sum = nums[0]
    for i in range(1, len(nums)):
        current_sum = max(nums[i], current_sum + nums[i])
        max_sum = max(max_sum, current_sum)
    return max_sum""",
    6: """def solution(s):
    char_map = {}
    left = 0
    max_len = 0
    for right in range(len(s)):
        if s[right] in char_map:
            left = max(left, char_map[s[right]] + 1)
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len""",
    7: """def solution(height):
    if not height: return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water""",
    8: """def solution(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]""",
    9: """def solution(lists):
    merged = []
    for sublist in lists:
        for item in sublist:
            merged.append(item)
    merged.sort()
    return merged""",
    10: """from collections import deque
def solution(nums, k):
    q = deque()
    result = []
    for i in range(len(nums)):
        while q and nums[q[-1]] <= nums[i]:
            q.pop()
        q.append(i)
        if q[0] == i - k:
            q.popleft()
        if i >= k - 1:
            result.append(nums[q[0]])
    return result"""
}

def simulate_user(user_index):
    user_id = f"sim-user-{user_index}"
    
    # 1. Ensure User Exists
    try:
        db.collection('participants').document(user_id).set({
            "name": f"Simulated User {user_index}",
            "email": f"sim{user_index}@test.com",
            "score": 0,
            "solved": [],
            "status": "ACTIVE",
            "violations": 0,
            "start_time": firestore.SERVER_TIMESTAMP
        }, merge=True)
    except:
        pass # Ignore writes if busy

    # 2. Random Activity Loop
    start = time.time()
    submitted_count = 0
    
    while time.time() - start < DURATION_SECONDS:
        # Sleep random amount (thinking time)
        time.sleep(random.uniform(2.0, 10.0))
        
        q_id = random.randint(1, 10)
        action_type = random.choice(["run", "submit", "submit"]) # Bias towards submit
        
        # Determine Code
        is_correct = random.random() < 0.90 # 90% correct
        
        code = ""
        if is_correct:
            code = SOLUTIONS[q_id]
        else:
            code = "print('Debugging attempt... ' + str(3+4))"
            
        # Create Submission
        try:
            db.collection('submissions').add({
                "participant_id": user_id,
                "problem_id": q_id,
                "language": "python",
                "code": code,
                "status": "pending",
                "type": action_type,
                "submitted_at": firestore.SERVER_TIMESTAMP,
                "stress_test": True
            })
            submitted_count += 1
            # print(f"User {user_index} -> {action_type} Q{q_id}")
        except Exception as e:
            print(f"Error for {user_index}: {e}")
            
    return submitted_count

def run_simulation():
    print(f"Starting Realistic Simulation: {NUM_USERS} users for {DURATION_SECONDS}s...")
    
    threads = []
    total_ops = 0
    
    # Launch in chunks to avoid hitting thread limits on some OS
    chunk_size = 50
    for i in range(0, NUM_USERS, chunk_size):
        chunk_threads = []
        for j in range(i, min(i+chunk_size, NUM_USERS)):
            t = threading.Thread(target=simulate_user, args=(j,))
            chunk_threads.append(t)
            t.start()
        
        for t in chunk_threads:
            t.join() # Wait for chunk (simplification for script stability)
            
    print("All users initiated. (Note: Script runs in batches, real event is parallel)")
    print("Generation Logic Complete.")

if __name__ == "__main__":
    run_simulation()

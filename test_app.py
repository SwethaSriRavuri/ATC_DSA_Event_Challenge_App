"""
Quick test script to verify the application components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import init_db, get_session, Participant
from backend.problem_loader import load_all_problems
from backend.executor import PythonExecutor
from backend.judge import Judge
import config

def test_database():
    """Test database initialization"""
    print("Testing database...")
    init_db()
    session = get_session()
    
    # Create a test participant
    participant = Participant(name="Test User", email="test@example.com", language="python")
    session.add(participant)
    session.commit()
    
    # Query it back
    result = session.query(Participant).first()
    assert result.name == "Test User"
    session.close()
    print("[OK] Database test passed")

def test_problem_loader():
    """Test problem loading"""
    print("\nTesting problem loader...")
    problems = load_all_problems()
    assert len(problems) == config.TOTAL_PROBLEMS, f"Expected {config.TOTAL_PROBLEMS} problems, got {len(problems)}"
    print(f"[OK] Loaded {len(problems)} problems")
    for prob in problems:
        print(f"  - Problem {prob['problem_id']}: {prob['title']}")

def test_python_executor():
    """Test Python code execution"""
    print("\nTesting Python executor...")
    executor = PythonExecutor()
    
    # Test simple code
    code = """
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    test_input = {"nums": [2, 7, 11, 15], "target": 9}
    success, output, error, exec_time = executor.execute(code, test_input)
    
    if success:
        print(f"[OK] Python execution successful")
        print(f"  Output: {output}")
        print(f"  Execution time: {exec_time:.3f}s")
    else:
        print(f"[FAIL] Python execution failed: {error}")

def test_judge():
    """Test judging system"""
    print("\nTesting judge...")
    judge = Judge()
    
    # Correct solution for Problem 1 (Basic Array Sum)
    code = """
def solution(nums):
    return sum(nums)
"""
    
    verdict, score, details = judge.judge_submission(1, code, "python")
    print(f"  Verdict: {verdict}")
    print(f"  Score: {score}")
    print(f"  Details: {details}")
    
    if verdict == "Accepted":
        print("[OK] Judge test passed")
    else:
        print(f"[FAIL] Judge test failed: {verdict}")

if __name__ == "__main__":
    print("=" * 50)
    print("DSA Challenge Application - Component Tests")
    print("=" * 50)
    
    try:
        test_database()
        test_problem_loader()
        test_python_executor()
        test_judge()
        
        print("\n" + "=" * 50)
        print("All tests passed!")
        print("=" * 50)
        print("\nYou can now run the application with: python main.py")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()

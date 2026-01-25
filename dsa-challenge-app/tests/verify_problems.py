import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.problem_loader import load_all_problems

def verify_problems():
    problems = load_all_problems()
    
    # Check total count
    if len(problems) != 10:
        print(f"FAILED: Expected 10 problems, got {len(problems)}")
        return False
    
    # Verify Syntax Fix problems (1-2)
    for i in range(2):
        p = problems[i]
        if p['problem_id'] != i + 1:
             print(f"FAILED: Problem order mismatch at index {i}")
             return False
        if p['type'] != 'syntax_fix':
            print(f"FAILED: Problem {p['problem_id']} should be 'syntax_fix', got '{p.get('type')}'")
            return False
        print(f"Problem {p['problem_id']}: Syntax Fix - OK")

    # Verify Logic Fix problems (3-5)
    for i in range(2, 5):
        p = problems[i]
        if p['type'] != 'logic_fix':
            print(f"FAILED: Problem {p['problem_id']} should be 'logic_fix', got '{p.get('type')}'")
            return False
        print(f"Problem {p['problem_id']}: Logic Fix - OK")
        
    # Verify Description problems (6-10)
    for i in range(5, 10):
        p = problems[i]
        if p['type'] != 'description':
            print(f"FAILED: Problem {p['problem_id']} should be 'description', got '{p.get('type')}'")
            return False
        print(f"Problem {p['problem_id']}: Description - OK")
            
    return True

if __name__ == "__main__":
    if verify_problems():
        print("\nAll problem types verified successfully!")
    else:
        print("\nVerification failed!")
        sys.exit(1)

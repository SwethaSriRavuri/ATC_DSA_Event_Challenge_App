"""
Quick test to verify executor output
"""
from backend.executor import PythonExecutor

# Test code
code = """
def solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []
"""

test_input = {"nums": [2, 7, 11, 15], "target": 9}

executor = PythonExecutor()
success, output, error, exec_time = executor.execute(code, test_input)

print("="*50)
print("EXECUTOR TEST")
print("="*50)
print(f"Success: {success}")
print(f"Output: '{output}'")
print(f"Output (repr): {repr(output)}")
print(f"Error: '{error}'")
print(f"Time: {exec_time:.3f}s")
print("="*50)

# Parse output
import json
try:
    parsed = json.loads(output)
    print(f"Parsed output: {parsed}")
    print(f"Parsed type: {type(parsed)}")
except Exception as e:
    print(f"Parse error: {e}")

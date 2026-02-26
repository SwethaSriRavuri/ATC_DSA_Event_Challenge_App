import json
from backend.executor import get_executor
from backend.problem_loader import get_test_cases
import config

class Judge:
    """Automated judging system"""
    
    VERDICT_ACCEPTED = "Accepted"
    VERDICT_WRONG_ANSWER = "Wrong Answer"
    VERDICT_COMPILATION_ERROR = "Compilation Error"
    VERDICT_RUNTIME_ERROR = "Runtime Error"
    VERDICT_TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"
    
    def __init__(self):
        pass
    
    def judge_submission(self, problem_id, code, language):
        """
        Judge a code submission against test cases
        Returns: (verdict, score, details)
        """
        # Get test cases for the problem
        test_cases = get_test_cases(problem_id)
        
        if not test_cases:
            return self.VERDICT_RUNTIME_ERROR, 0, "No test cases found"
        
        # Get executor for the language
        try:
            executor = get_executor(language)
        except ValueError as e:
            return self.VERDICT_COMPILATION_ERROR, 0, str(e)
        
        # Run all test cases
        passed = 0
        total = len(test_cases)
        details = []
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get('input', {})
            expected_output = test_case.get('expected_output')
            
            # Execute code
            success, output, error, exec_time = executor.execute(code, test_input)
            
            # Check for errors
            if not success:
                if 'Time Limit Exceeded' in error:
                    return self.VERDICT_TIME_LIMIT_EXCEEDED, 0, f"TLE on test case {i+1}"
                elif error:
                    return self.VERDICT_RUNTIME_ERROR, 0, f"Error on test case {i+1}: {error[:200]}"
                else:
                    return self.VERDICT_COMPILATION_ERROR, 0, "Compilation failed"
            
            # Compare output
            try:
                actual_output = json.loads(output) if output else None
            except json.JSONDecodeError:
                actual_output = output.strip()
            
            if self._compare_output(actual_output, expected_output):
                passed += 1
                details.append(f"Test {i+1}: Passed ({exec_time:.3f}s)")
            else:
                details.append(f"Test {i+1}: Failed (Expected: {expected_output}, Got: {actual_output})")
        
        # Calculate score and verdict
        if passed == total:
            verdict = self.VERDICT_ACCEPTED
            score = config.MARKS_PER_PROBLEM
        else:
            verdict = self.VERDICT_WRONG_ANSWER
            score = 0  # No partial credit
        
        details_str = '\n'.join(details)
        return verdict, score, details_str
    
    def _compare_output(self, actual, expected):
        """Compare actual and expected output"""
        # Handle None
        if actual is None and expected is None:
            return True
        if actual is None or expected is None:
            return False
        
        # Handle lists
        if isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            return all(self._compare_output(a, e) for a, e in zip(actual, expected))
        
        # Handle dictionaries
        if isinstance(expected, dict) and isinstance(actual, dict):
            if set(expected.keys()) != set(actual.keys()):
                return False
            return all(self._compare_output(actual[k], expected[k]) for k in expected.keys())
        
        # Handle numbers (with small tolerance for floats)
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) < 1e-6
        
        # Handle strings
        if isinstance(expected, str) and isinstance(actual, str):
            return expected.strip() == actual.strip()
        
        # Direct comparison
        return actual == expected

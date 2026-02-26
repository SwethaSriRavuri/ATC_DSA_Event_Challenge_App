import json
import os
import config

def load_problem(problem_id):
    """Load a single problem from JSON file"""
    problem_file = os.path.join(config.PROBLEMS_DIR, f'problem_{problem_id}.json')
    
    if not os.path.exists(problem_file):
        return None
    
    with open(problem_file, 'r', encoding='utf-8') as f:
        problem_data = json.load(f)
    
    return problem_data

def load_all_problems():
    """Load all problems (without test cases for display)"""
    problems = []
    
    for i in range(1, config.TOTAL_PROBLEMS + 1):
        problem = load_problem(i)
        if problem:
            # Remove test cases for display
            display_problem = {
                'problem_id': problem['problem_id'],
                'title': problem['title'],
                'difficulty': problem['difficulty'],
                'marks': problem['marks'],
                'description': problem['description'],
                'type': problem.get('type', 'description')
            }
            problems.append(display_problem)
    
    return problems

def get_problem_with_starter_code(problem_id, language):
    """Get problem with starter code for specific language"""
    problem = load_problem(problem_id)
    
    if not problem:
        return None
    
    return {
        'problem_id': problem['problem_id'],
        'title': problem['title'],
        'difficulty': problem['difficulty'],
        'marks': problem['marks'],
        'description': problem['description'],
        'type': problem.get('type', 'description'),
        'starter_code': problem['starter_code'].get(language, '')
    }

def get_test_cases(problem_id):
    """Get test cases for a problem (for judging only)"""
    problem = load_problem(problem_id)
    
    if not problem:
        return []
    
    return problem.get('test_cases', [])

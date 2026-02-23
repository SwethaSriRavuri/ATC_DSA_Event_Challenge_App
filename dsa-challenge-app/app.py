from flask import Flask, render_template, request, jsonify, session, redirect
from backend.service import ContestService
from backend.queue_manager import JobQueue
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dsa-challenge-secure-key-2024')
service = ContestService()
# Initialize Job Queue with 2 concurrent workers
job_queue = JobQueue(max_concurrent=2)

@app.route('/')
def index():
    """Landing page / registration"""
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Register participant"""
    data = request.json
    try:
        participant_id = service.register_participant(
            data['name'],
            data.get('email', ''),
            'python'
        )
        session['participant_id'] = participant_id
        session['name'] = data['name']
        session['email'] = data.get('email', '')
        
        # Start contest
        success, message = service.start_contest(participant_id)
        if success:
            return jsonify({'success': True, 'participant_id': participant_id})
        else:
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/contest')
def contest():
    """Contest interface"""
    # Client-side Auth (Firebase/LocalStorage) handles security now.
    # We just serve the page.
    return render_template('contest.html', name='Participant', email='', participant_id='')

@app.route('/completion')
def completion():
    """Completion page"""
    return render_template('completion.html')

@app.route('/api/problems', methods=['GET'])
def get_problems():
    """Get all problems"""
    problems = service.get_all_problems()
    return jsonify(problems)

@app.route('/api/problem/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    """Get specific problem with starter code"""
    language = request.args.get('language', 'python')
    problem = service.get_problem(problem_id, language)
    return jsonify(problem)

# Helper function to perform the actual run
def _perform_run_code(data):
    try:
        problem_id = data['problem_id']
        code = data['code']
        language = data['language']
        
        from backend.problem_loader import get_test_cases
        from backend.executor import get_executor
        from backend.judge import Judge
        
        test_cases = get_test_cases(problem_id)
        if not test_cases:
            return {'success': False, 'message': 'No test cases available'}
        
        executor = get_executor(language)
        test_input = test_cases[0]['input']
        expected = test_cases[0]['expected_output']
        
        success, output, error, exec_time = executor.execute(code, test_input)
        
        if success:
            import json
            try:
                actual = json.loads(output) if output else None
            except:
                actual = output.strip()
            
            judge = Judge()
            passed = judge._compare_output(actual, expected)
            
            return {
                'success': True,
                'passed': passed,
                'input': test_input,
                'expected': expected,
                'actual': actual,
                'time': exec_time,
                'error': None
            }
        else:
            return {
                'success': False,
                'passed': False,
                'error': error,
                'error_type': 'execution'
            }
    except Exception as e:
        return {
            'success': False,
            'passed': False,
            'error': str(e),
            'error_type': 'system'
        }

@app.route('/api/run', methods=['POST'])
def run_code():
    """Queue code for execution"""
    data = request.json
    
    # Add to queue
    task_id = job_queue.add_job('run', _perform_run_code, data)
    
    return jsonify({
        'success': True,
        'queued': True,
        'task_id': task_id,
        'message': 'Queued for execution'
    })

# Helper function for submission
def _perform_submit(participant_id, data):
    return service.submit_code(
        participant_id,
        data['problem_id'],
        data['code'],
        data['language']
    )

@app.route('/api/submit', methods=['POST'])
def submit_code():
    """Queue submission for judging"""
    if 'participant_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    participant_id = session['participant_id']
    
    # Add to queue
    task_id = job_queue.add_job('submit', _perform_submit, participant_id, data)
    
    return jsonify({
        'success': True,
        'queued': True,
        'task_id': task_id,
        'message': 'Queued for judging'
    })
    
@app.route('/api/queue/status/<task_id>', methods=['GET'])
def get_queue_status(task_id):
    """Check status of a queued job"""
    status = job_queue.get_status(task_id)
    if status is None:
        return jsonify({'status': 'not_found'}), 404
        
    return jsonify(status)

@app.route('/api/contest/status', methods=['GET'])
def contest_status():
    """Get contest status"""
    if 'participant_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    status = service.get_contest_status(session['participant_id'])
    return jsonify(status)

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get participant results"""
    if 'participant_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    results = service.get_results(session['participant_id'])
    return jsonify(results)

@app.route('/api/contest/end', methods=['POST'])
def end_contest():
    """End contest"""
    if 'participant_id' not in session:
        return jsonify({'success': False})
    
    service.end_contest(session['participant_id'])
    return jsonify({'success': True})

@app.route('/api/contest/violation', methods=['POST'])
def record_violation():
    """Record an anti-cheating violation"""
    if 'participant_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    result = service.record_violation(session['participant_id'])
    return jsonify(result)



@app.route('/organizer')
def organizer_view():
    """Organizer leaderboard view - triggers lazy finalization of expired sessions"""
    service.get_leaderboard_data()
    return render_template('organizer.html')

@app.route('/api/organizer/data', methods=['GET'])
def get_organizer_data():
    """Get leaderboard data"""
    data = service.get_leaderboard_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
    
# --- ADMIN UTILS (For cleanup) ---
from backend.admin_utils import reset_db

@app.route('/secret/reset-db-now')
def reset_database_route():
    """Secret route to wipe database"""
    reset_db()
    # Check if request wants JSON (AJAX) or HTML (Browser)
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Database cleared successfully'})
    return "<h1>Database CLEARED</h1><p>All participants and submissions have been deleted.</p><a href='/'>Go to Home</a>"

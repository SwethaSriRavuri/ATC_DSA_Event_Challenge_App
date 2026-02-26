import unittest
import time
import json
from app import app, job_queue

class TestQueueSystem(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        
    def tearDown(self):
        self.ctx.pop()

    def test_queue_direct(self):
        """Test JobQueue class directly"""
        def dummy_job(x):
            time.sleep(0.5)
            return x * 2
            
        task_id = job_queue.add_job('test', dummy_job, 21)
        
        # Check pending
        status = job_queue.get_status(task_id)
        self.assertEqual(status['status'], 'pending')
        
        # Wait for result
        result = None
        for _ in range(20):
            status = job_queue.get_status(task_id)
            if status['status'] == 'completed':
                result = status['result']
                break
            time.sleep(0.1)
            
        self.assertEqual(result, 42)

    def test_run_endpoint_async(self):
        """Test /api/run endpoint returns queue info"""
        # Mock data for existing problem 1
        data = {
            'problem_id': 1,
            'code': 'def solution(nums, target):\n    pass', # Won't pass but should run
            'language': 'python'
        }
        
        response = self.client.post('/api/run', json=data)
        self.assertEqual(response.status_code, 200)
        res = response.get_json()
        
        self.assertTrue(res['queued'])
        self.assertIn('task_id', res)
        
        task_id = res['task_id']
        
        # Poll status
        completed = False
        final_result = None
        for i in range(50):
            s_resp = self.client.get(f'/api/queue/status/{task_id}')
            s_data = s_resp.get_json()
            print(f"Poll {i}: {s_data}", flush=True)
            
            if s_data['status'] == 'completed':
                completed = True
                final_result = s_data
                self.assertIn('success', s_data['result'])
                break
            elif s_data['status'] == 'failed':
                print(f"Task Failed: {s_data}", flush=True)
                break
                
            time.sleep(0.5)
            
        if not completed:
            print("Timeout waiting for task", flush=True)
            
        self.assertTrue(completed, f"Task did not complete. Final status: {final_result}")

if __name__ == '__main__':
    unittest.main()

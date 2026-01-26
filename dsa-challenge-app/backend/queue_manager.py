import queue
import threading
import uuid
import time
import json
from datetime import datetime

class JobQueue:
    def __init__(self, max_warnings=3, max_concurrent=2):
        self.queue = queue.Queue()
        self.results = {}
        self.max_concurrent = max_concurrent
        
        # Start worker threads
        self.workers = []
        for _ in range(max_concurrent):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self.workers.append(t)
            
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()

    def add_job(self, task_type, func, *args, **kwargs):
        """
        Add a job to the queue.
        task_type: 'run' or 'submit'
        func: The function to execute
        """
        task_id = str(uuid.uuid4())
        self.results[task_id] = {
            'status': 'pending',
            'submitted_at': time.time()
        }
        
        job = {
            'id': task_id,
            'type': task_type,
            'func': func,
            'args': args,
            'kwargs': kwargs
        }
        
        self.queue.put(job)
        return task_id

    def get_status(self, task_id):
        return self.results.get(task_id, None)

    def _worker_loop(self):
        while True:
            try:
                job = self.queue.get()
                task_id = job['id']
                
                # Update status to processing
                self.results[task_id]['status'] = 'processing'
                
                try:
                    # Execute the function
                    # result is expected to be a dict (response data)
                    result_data = job['func'](*job['args'], **job['kwargs'])
                    
                    # If the result is a Flask Response object (e.g. jsonify), we need to extract data
                    # But our service methods usually return dicts. We should ensure we pass service methods, not route handlers.
                    
                    self.results[task_id]['result'] = result_data
                    self.results[task_id]['status'] = 'completed'
                    
                except Exception as e:
                    self.results[task_id]['status'] = 'failed'
                    self.results[task_id]['error'] = str(e)
                finally:
                    self.queue.task_done()
                    
            except Exception as e:
                print(f"Worker Error: {e}")

    def _cleanup_loop(self):
        """Remove old results to prevent memory leaks"""
        while True:
            time.sleep(60) # Run every minute
            now = time.time()
            to_remove = []
            
            for task_id, data in self.results.items():
                # Keep results for 5 minutes
                if now - data['submitted_at'] > 300:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.results[task_id]

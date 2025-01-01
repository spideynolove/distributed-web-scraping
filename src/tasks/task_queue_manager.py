import redis
import time
import logging
from typing import Optional, List, Dict
from datetime import datetime

class TaskQueueManager:
    """Manages task queues and task processing in Redis"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port)
        self.logger = logging.getLogger(__name__)
        
        # Queue configuration
        self.queues = {
            'high_priority': 'queue:high',
            'normal_priority': 'queue:normal',
            'low_priority': 'queue:low'
        }
        
        # Error handling configuration
        self.max_retries = 3
        self.retry_delay = 60  # seconds

    def add_task(self, url: str, spider_name: str, priority: str = 'normal', meta: Optional[Dict] = None) -> bool:
        """Add a new task to the appropriate queue"""
        if priority not in self.queues:
            self.logger.warning(f"Invalid priority {priority}, using normal priority")
            priority = 'normal'
            
        queue_name = self.queues[priority]
        task_data = {
            'url': url,
            'spider': spider_name,
            'timestamp': datetime.utcnow().isoformat(),
            'meta': meta or {},
            'retries': 0
        }
        
        return bool(self.redis.rpush(queue_name, task_data))

    def get_next_task(self) -> Optional[Dict]:
        """Get the next task from the highest priority queue"""
        for queue in ['high_priority', 'normal_priority', 'low_priority']:
            task = self.redis.lpop(self.queues[queue])
            if task:
                return task
        return None

    def mark_task_failed(self, task: Dict, error: str) -> None:
        """Handle failed tasks with retry logic"""
        task['retries'] += 1
        task['last_error'] = error
        task['next_retry'] = time.time() + self.retry_delay
        
        if task['retries'] <= self.max_retries:
            self.redis.rpush(self.queues['low_priority'], task)
        else:
            self.redis.rpush('queue:failed', task)

    def get_queue_stats(self) -> Dict:
        """Get statistics about all queues"""
        stats = {}
        for queue_name, queue_key in self.queues.items():
            stats[queue_name] = {
                'size': self.redis.llen(queue_key),
                'oldest_task': self.redis.lindex(queue_key, 0),
                'newest_task': self.redis.lindex(queue_key, -1)
            }
        return stats

    def clear_queues(self) -> None:
        """Clear all task queues"""
        for queue_key in self.queues.values():
            self.redis.delete(queue_key)
        self.redis.delete('queue:failed')
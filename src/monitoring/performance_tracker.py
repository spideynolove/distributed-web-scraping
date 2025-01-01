import time
import redis
import logging
from typing import Dict, Optional
from datetime import datetime

class PerformanceTracker:
    """Tracks and monitors scraping performance metrics"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port)
        self.logger = logging.getLogger(__name__)
        
        # Metric keys
        self.metric_keys = {
            'requests': 'metrics:requests',
            'success': 'metrics:success',
            'errors': 'metrics:errors',
            'response_time': 'metrics:response_time',
            'items': 'metrics:items'
        }
        
        # Alert thresholds
        self.thresholds = {
            'error_rate': 0.1,  # 10%
            'response_time': 5.0,  # seconds
            'throughput': 10  # items/second
        }

    def start_request(self):
        """Track the start of a request"""
        self.redis.incr(self.metric_keys['requests'])
        return time.time()

    def end_request(self, start_time: float, success: bool = True):
        """Track the end of a request"""
        response_time = time.time() - start_time
        self.redis.incr(self.metric_keys['success'] if success else self.metric_keys['errors'])
        self.redis.rpush(self.metric_keys['response_time'], response_time)

    def track_item(self, count: int = 1):
        """Track scraped items"""
        self.redis.incrby(self.metric_keys['items'], count)

    def get_metrics(self) -> Dict:
        """Get current performance metrics"""
        metrics = {}
        try:
            metrics = {
                'requests': int(self.redis.get(self.metric_keys['requests']) or 0),
                'success': int(self.redis.get(self.metric_keys['success']) or 0),
                'errors': int(self.redis.get(self.metric_keys['errors']) or 0),
                'items': int(self.redis.get(self.metric_keys['items']) or 0),
                'response_times': [
                    float(rt) for rt in 
                    self.redis.lrange(self.metric_keys['response_time'], 0, -1)
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Calculate derived metrics
            if metrics['requests'] > 0:
                metrics['error_rate'] = metrics['errors'] / metrics['requests']
                metrics['success_rate'] = metrics['success'] / metrics['requests']
            else:
                metrics['error_rate'] = 0.0
                metrics['success_rate'] = 0.0
                
            if metrics['response_times']:
                metrics['avg_response_time'] = sum(metrics['response_times']) / len(metrics['response_times'])
            else:
                metrics['avg_response_time'] = 0.0
                
        except redis.RedisError as e:
            self.logger.error(f"Error getting metrics: {e}")
            
        return metrics

    def check_alerts(self) -> Dict:
        """Check if any metrics exceed alert thresholds"""
        metrics = self.get_metrics()
        alerts = {}
        
        if 'error_rate' in metrics and metrics['error_rate'] > self.thresholds['error_rate']:
            alerts['error_rate'] = {
                'value': metrics['error_rate'],
                'threshold': self.thresholds['error_rate']
            }
            
        if 'avg_response_time' in metrics and metrics['avg_response_time'] > self.thresholds['response_time']:
            alerts['response_time'] = {
                'value': metrics['avg_response_time'],
                'threshold': self.thresholds['response_time']
            }
            
        if 'items' in metrics and metrics['items'] > 0:
            elapsed_time = time.time() - datetime.fromisoformat(metrics['timestamp']).timestamp()
            throughput = metrics['items'] / elapsed_time
            if throughput < self.thresholds['throughput']:
                alerts['throughput'] = {
                    'value': throughput,
                    'threshold': self.thresholds['throughput']
                }
                
        return alerts

    def reset_metrics(self):
        """Reset all performance metrics"""
        try:
            for key in self.metric_keys.values():
                self.redis.delete(key)
        except redis.RedisError as e:
            self.logger.error(f"Error resetting metrics: {e}")
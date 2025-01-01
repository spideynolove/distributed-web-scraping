import scrapy
from scrapy_redis.spiders import RedisSpider
from redis import Redis
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.utils.log import logger

class BaseSpider(RedisSpider):
    """Base spider class for all spiders in the project"""
    
    custom_settings = {
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': 6379,
        'SCHEDULER': 'scrapy_redis.scheduler.Scheduler',
        'DUPEFILTER_CLASS': 'scrapy_redis.dupefilter.RFPDupeFilter',
        'ITEM_PIPELINES': {
            'scrapy_redis.pipelines.RedisPipeline': 300
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = Redis(
            host=self.settings.get('REDIS_HOST'),
            port=self.settings.get('REDIS_PORT')
        )
        self.log_prefix = f"[{self.name}]"

    def parse(self, response):
        """Base parse method to be overridden by child classes"""
        raise NotImplementedError("parse method must be implemented in child class")

    def handle_error(self, failure):
        """Handle request failures"""
        logger.error(f"{self.log_prefix} Request failed: {failure.value}")
        self.redis_client.rpush(f"{self.name}:failed_urls", failure.request.url)

    def close(self, reason):
        """Clean up when spider closes"""
        super().close(reason)
        logger.info(f"{self.log_prefix} Spider closed: {reason}")
        self.redis_client.close()

    def make_request(self, url, callback, meta=None, priority=0):
        """Create a new request with common settings"""
        return Request(
            url=url,
            callback=callback,
            errback=self.handle_error,
            meta=meta or {},
            priority=priority,
            dont_filter=True
        )
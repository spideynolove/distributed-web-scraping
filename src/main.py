import os
import sys
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
from redis import Redis

def configure_redis():
    """Configure Redis connection"""
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    return Redis(host=redis_host, port=redis_port)

def get_spider_class(spider_name):
    """Dynamically load spider class"""
    module_path = f'src.spiders.{spider_name}'
    try:
        module = __import__(module_path, fromlist=[spider_name])
        return getattr(module, spider_name)
    except (ImportError, AttributeError) as e:
        print(f"Error loading spider: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Distributed Web Scraping System')
    parser.add_argument('spider', help='Name of the spider to run')
    parser.add_argument('--redis-host', help='Redis host', default='localhost')
    parser.add_argument('--redis-port', help='Redis port', type=int, default=6379)
    
    args = parser.parse_args()

    # Configure Redis
    redis_client = configure_redis()

    # Set up Scrapy settings
    settings = get_project_settings()
    settings.set('REDIS_HOST', args.redis_host)
    settings.set('REDIS_PORT', args.redis_port)
    settings.set('SCHEDULER', 'scrapy_redis.scheduler.Scheduler')
    settings.set('DUPEFILTER_CLASS', 'scrapy_redis.dupefilter.RFPDupeFilter')

    # Load and run spider
    spider_class = get_spider_class(args.spider)
    process = CrawlerProcess(settings)
    process.crawl(spider_class)
    process.start()

if __name__ == '__main__':
    main()

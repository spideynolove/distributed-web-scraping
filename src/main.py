#!/usr/bin/env python3

import os
import yaml
import logging.config
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.ecommerce_spider import EcommerceSpider
from spiders.finance_spider import FinanceSpider
import redis
from prometheus_client import start_http_server
import argparse

def load_config():
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(config):
    """Configure logging based on settings."""
    logging_config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': config['logging']['format']
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': config['logging']['file'],
                'maxBytes': config['logging']['max_size'],
                'backupCount': config['logging']['backup_count'],
                'formatter': 'standard'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': config['logging']['level']
            }
        }
    }
    logging.config.dictConfig(logging_config)

def setup_redis(config):
    """Setup Redis connection."""
    redis_config = config['redis']
    return redis.Redis(
        host=redis_config['host'],
        port=redis_config['port'],
        db=redis_config['db'],
        password=redis_config['password']
    )

def setup_scrapy_settings(config):
    """Configure Scrapy settings."""
    settings = get_project_settings()
    
    # Redis settings
    settings.set('REDIS_HOST', config['redis']['host'])
    settings.set('REDIS_PORT', config['redis']['port'])
    
    # Scraping settings
    settings.set('CONCURRENT_REQUESTS', config['scraping']['concurrent_requests'])
    settings.set('DOWNLOAD_DELAY', config['scraping']['download_delay'])
    settings.set('RETRY_TIMES', config['scraping']['retry_times'])
    settings.set('RETRY_DELAY', config['scraping']['retry_delay'])
    settings.set('DOWNLOAD_TIMEOUT', config['scraping']['timeout'])
    
    # Storage settings
    if config['storage']['type'] == 'mongodb':
        settings.set('ITEM_PIPELINES', {
            'scrapy_mongodb.MongoDBPipeline': 300
        })
        settings.set('MONGODB_URI', config['mongodb']['uri'])
        settings.set('MONGODB_DATABASE', config['mongodb']['database'])
    
    return settings

def start_metrics_server(config):
    """Start Prometheus metrics server."""
    try:
        metrics_port = config['monitoring']['prometheus']['port']
        start_http_server(metrics_port)
        logging.info(f"Started metrics server on port {metrics_port}")
    except Exception as e:
        logging.error(f"Failed to start metrics server: {str(e)}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Distributed Web Scraping System')
    parser.add_argument('--spider', choices=['ecommerce', 'finance', 'all'],
                      default='all', help='Spider to run')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode')
    return parser.parse_args()

def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        if args.debug:
            logger.setLevel(logging.DEBUG)
        
        logger.info("Starting Distributed Web Scraping System")
        
        # Setup Redis
        redis_client = setup_redis(config)
        logger.info("Connected to Redis")
        
        # Start metrics server
        start_metrics_server(config)
        
        # Setup and start Scrapy
        settings = setup_scrapy_settings(config)
        process = CrawlerProcess(settings)
        
        # Add spiders based on arguments
        if args.spider in ['ecommerce', 'all']:
            process.crawl(EcommerceSpider)
            logger.info("Added E-commerce spider to crawl queue")
            
        if args.spider in ['finance', 'all']:
            process.crawl(FinanceSpider)
            logger.info("Added Finance spider to crawl queue")
        
        logger.info("Starting spider(s)")
        process.start()
        
    except Exception as e:
        logger.error(f"Failed to start scraping system: {str(e)}")
        raise

if __name__ == "__main__":
    main()

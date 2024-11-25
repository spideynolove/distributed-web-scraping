# Distributed Web Scraping System

A scalable, distributed web scraping solution built with Scrapy and Redis for gathering large-scale datasets from e-commerce and financial websites.

## Features

- Distributed task queue using Redis for parallel scraping
- URL deduplication and intelligent task management
- Robust data extraction from e-commerce and financial sources 
- Error handling with automated retry mechanisms
- Flexible data storage using MongoDB/PostgreSQL
- Comprehensive monitoring and scheduling capabilities
- Docker-based deployment for easy scaling

## Project Structure
```
distributed-web-scraping/
├── src/
│   ├── spiders/
│   │   ├── ecommerce_spider.py     # E-commerce data spider
│   │   ├── finance_spider.py       # Financial data spider
│   │   └── parsers.py             # Data cleaning utilities
│   ├── middleware/
│   │   ├── rate_limiter.py        # Smart rate limiting
│   │   ├── proxy_manager.py       # Proxy rotation & management
│   │   └── user_agents.py         # User agent rotation
│   ├── tasks/
│   │   ├── task_queue_manager.py  # Redis queue management
│   │   ├── url_deduplication.py   # URL uniqueness
│   │   ├── error_handler.py       # Retry logic
│   │   └── scheduling.py          # Task scheduling
│   ├── storage/
│   │   ├── mongo_storage.py       # MongoDB integration
│   │   ├── postgres_storage.py    # PostgreSQL integration
│   │   └── schema_definitions.py  # Database schemas
│   ├── monitoring/
│   │   ├── performance_tracker.py # Performance metrics
│   │   ├── alert_manager.py      # Error alerting
│   │   └── redis_monitor.py      # Queue monitoring
│   ├── validation/
│   │   ├── data_validator.py     # Input/output validation
│   │   └── schema_validator.py   # JSON schema validation
│   ├── exporters/
│   │   ├── csv_exporter.py      # Data export utilities
│   │   └── api_publisher.py     # API for data access
│   └── main.py                  # Entry point
├── infrastructure/
│   ├── terraform/               # Cloud deployment IaC
│   ├── kubernetes/             # K8s configurations
│   └── monitoring/
│       ├── grafana/           # Monitoring dashboards
│       └── prometheus/        # Metrics collection
├── dags/
│   ├── scraping_dag.py       # Airflow DAG
│   └── task_definitions.py   # Airflow tasks
├── config/
│   ├── settings.yaml         # System configuration
│   └── logging.yaml          # Logging configuration
├── data/
│   ├── raw/                 # Raw scraped data
│   ├── processed/          # Cleaned data
│   └── backups/           # Data backups
├── docs/
│   ├── api/               # API documentation
│   ├── architecture/     # System design docs
│   ├── deployment/      # Deployment guides
│   └── maintenance/     # Operation guides
├── security/
│   ├── encryption/      # Data encryption
│   ├── access_control.py # Access management
│   └── compliance/     # Scraping compliance
├── tests/
│   ├── test_spiders.py
│   ├── test_task_queue.py
│   ├── test_storage.py
│   └── test_monitoring.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yaml
├── scheduler/
│   ├── cron_jobs/      # Periodic scraping
│   └── airflow_dags/   # Complex scheduling
├── logs/
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Redis
- MongoDB or PostgreSQL
- Scrapy
- Redis-py

## Installation

1. Clone the repository:
```bash
git clone https://github.com/username/distributed-scraping.git
cd distributed-scraping
```

2. Build Docker containers:
```bash
docker-compose build
```

3. Start services:
```bash
docker-compose up -d
```

## Configuration

### Spider Configuration
```python
# settings.py
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
```

### Database Settings
```python
# Choose between MongoDB and PostgreSQL
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "scraping_data"

# Or for PostgreSQL
POSTGRES_DB = "scraping_data"
POSTGRES_USER = "user"
POSTGRES_PASSWORD = "password"
```

## Usage

1. Add URLs to Redis queue:
```python
from redis import Redis
redis_client = Redis(host='localhost', port=6379)
redis_client.lpush('spider:start_urls', 'https://example.com')
```

2. Run spiders:
```bash
docker-compose exec scraper scrapy crawl spider_name
```

3. Monitor progress:
```bash
docker-compose logs -f
```

## Spider Examples

### E-commerce Spider
```python
from scrapy_redis.spiders import RedisSpider

class EcommerceSpider(RedisSpider):
    name = 'ecommerce'
    
    def parse(self, response):
        yield {
            'product_name': response.css('.product-name::text').get(),
            'price': response.css('.price::text').get(),
            'stock': response.css('.stock::text').get()
        }
```

### Finance Spider
```python
class FinanceSpider(RedisSpider):
    name = 'finance'
    
    def parse(self, response):
        yield {
            'ticker': response.css('.symbol::text').get(),
            'price': response.css('.current-price::text').get(),
            'volume': response.css('.volume::text').get()
        }
```

## Error Handling

The system implements multiple layers of error handling:

1. Network failures: Automatic retry with exponential backoff
2. Rate limiting: Intelligent delay between requests
3. Data validation: Schema validation before storage
4. Monitoring: Alert system for critical failures

## Scaling

Scale horizontally by adding more worker containers:
```bash
docker-compose up -d --scale scraper=3
```

## Monitoring

Access monitoring dashboards:
- Redis monitoring: `http://localhost:8001`
- Database metrics: `http://localhost:8002`
- Spider logs: `http://localhost:8003`
- Grafana dashboards: `http://localhost:3000`
- Prometheus metrics: `http://localhost:9090`

## Security

- Data encryption at rest and in transit
- Access control for scraped data
- Compliance with robots.txt
- Rate limiting and polite crawling
- Regular security audits

## License

MIT License - See LICENSE file for details

## Contact

Project maintainers:
- Email: spdeynolove@gmail.com
- GitHub: [@spdeynolove](https://github.com/spdeynolove)
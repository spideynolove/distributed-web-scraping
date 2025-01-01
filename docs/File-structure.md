# Project File Structure and Components

## Directory Structure

```
distributed-web-scraping/
├── src/
│   ├── spiders/
│   │   ├── base/
│   │   │   ├── base_spider.py          # Base spider class
│   │   │   └── mixins.py               # Reusable spider components
│   │   ├── extractors/
│   │   │   ├── price_extractor.py      # Price extraction logic
│   │   │   ├── product_extractor.py    # Product details extraction
│   │   │   └── common_extractors.py    # Shared extraction utilities
│   │   └── validators/
│   │       ├── field_validator.py      # Field validation
│   │       └── output_validator.py     # Output data validation
│   ├── middleware/
│   │   ├── rate_limiting/
│   │   │   ├── domain_rates.py        # Domain-specific rates
│   │   │   └── adaptive_delay.py      # Dynamic rate adjustment
│   │   ├── proxy/
│   │   │   ├── proxy_pool.py          # Proxy management
│   │   │   └── rotation_logic.py      # Proxy rotation rules
│   │   └── user_agents/
│   │       ├── agent_pool.py          # User agent management
│   │       └── browser_profiles.py     # Browser fingerprinting
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

## Key Files and Their Roles

### Core Functionality
- **src/main.py**: Application entry point
- **src/spiders/**: Contains all spider implementations
- **src/middleware/**: Request processing components
- **src/tasks/**: Task queue management

### Data Management
- **src/storage/**: Database integration and schema management
- **src/validation/**: Data validation pipelines
- **src/exporters/**: Data export and API access

### Infrastructure
- **docker/**: Containerization configuration
- **infrastructure/**: Cloud deployment configurations
- **config/**: System and logging configurations

### Monitoring
- **src/monitoring/**: Application-level monitoring
- **infrastructure/monitoring/**: Infrastructure monitoring

### Testing
- **tests/**: Unit and integration tests

## Component Interactions

1. **Task Queue System**
   - Redis interacts with task_queue_manager.py
   - URL deduplication and scheduling handled by dedicated modules

2. **Spider Execution**
   - Spiders use middleware components for request processing
   - Extracted data passed to validation system

3. **Data Pipeline**
   - Validated data stored in selected database
   - Monitoring system tracks data quality and storage performance

4. **Export System**
   - Data can be exported via CSV or API
   - Exporters interact with storage system

5. **Monitoring**
   - Collects metrics from all components
   - Provides alerts and dashboards

6. **Infrastructure**
   - Docker containers managed by docker-compose
   - Kubernetes orchestrates container deployment
   - Terraform manages cloud resources
# Application Workflow

```mermaid
flowchart TD
    A[URL Ingestion] --> B[Redis Task Queue]
    B --> C{Spider Selection}
    C --> D[E-commerce Spider]
    C --> E[Finance Spider]
    D --> F[Middleware Processing]
    E --> F
    F --> G[Data Validation]
    G --> H{Storage Selection}
    H --> I[MongoDB]
    H --> J[PostgreSQL]
    I --> K[Monitoring & Alerting]
    J --> K
    K --> L[Data Export]
    L --> M[CSV Files]
    L --> N[API Access]
    
    subgraph Middleware
        F --> O[Rate Limiting]
        F --> P[Proxy Rotation]
        F --> Q[User Agent Management]
        F --> R[Request Filtering]
    end
    
    subgraph Monitoring
        K --> S[Redis Monitoring]
        K --> T[Database Metrics]
        K --> U[Spider Logs]
        K --> V[Grafana Dashboards]
        K --> W[Prometheus Metrics]
    end
```

## Workflow Description

1. **URL Ingestion**: URLs are added to the Redis task queue through the Redis client interface
2. **Spider Selection**: The system selects the appropriate spider based on the URL domain and type
3. **Middleware Processing**: Each request goes through multiple middleware components for:
   - Rate limiting
   - Proxy rotation
   - User agent management
   - Request filtering
4. **Data Validation**: Extracted data is validated against predefined schemas
5. **Storage**: Validated data is stored in either MongoDB or PostgreSQL
6. **Monitoring**: System performance and data quality are monitored through various tools
7. **Export**: Data can be exported as CSV files or accessed through an API
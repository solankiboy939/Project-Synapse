# Project Synapse Deployment Guide

## Overview

This guide covers deploying Project Synapse in various environments, from development to enterprise production deployments.

## Quick Start (Development)

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Git

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/synapse-ai/project-synapse.git
cd project-synapse

# Run development setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# Activate virtual environment
source venv/bin/activate

# Initialize configuration
synapse init --config-path config/dev.yaml

# Start services with Docker Compose
docker-compose up -d redis elasticsearch postgres

# Start the indexer
synapse indexer start

# Start the API server
synapse server start --reload
```

The API will be available at `http://localhost:8080` with interactive docs at `http://localhost:8080/docs`.

## Docker Deployment

### Single Container

```bash
# Build the image
docker build -t synapse:latest .

# Run with default configuration
docker run -p 8080:8080 synapse:latest

# Run with custom configuration
docker run -p 8080:8080 -v $(pwd)/config:/app/config synapse:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f synapse-api

# Scale API servers
docker-compose up -d --scale synapse-api=3

# Stop services
docker-compose down
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Helm 3.x (optional)

### Basic Kubernetes Deployment

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: synapse
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: synapse-config
  namespace: synapse
data:
  config.yaml: |
    synapse:
      privacy:
        global_budget: 50.0
      api:
        host: "0.0.0.0"
        port: 8080
---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synapse-api
  namespace: synapse
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synapse-api
  template:
    metadata:
      labels:
        app: synapse-api
    spec:
      containers:
      - name: synapse-api
        image: synapse:latest
        ports:
        - containerPort: 8080
        env:
        - name: SYNAPSE_CONFIG
          value: /app/config/config.yaml
        volumeMounts:
        - name: config
          mountPath: /app/config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: synapse-config
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: synapse-api-service
  namespace: synapse
spec:
  selector:
    app: synapse-api
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: synapse-ingress
  namespace: synapse
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - synapse.yourdomain.com
    secretName: synapse-tls
  rules:
  - host: synapse.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: synapse-api-service
            port:
              number: 80
```

Deploy to Kubernetes:

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n synapse
kubectl get services -n synapse

# View logs
kubectl logs -f deployment/synapse-api -n synapse
```

### Helm Chart Deployment

```bash
# Add Synapse Helm repository
helm repo add synapse https://charts.synapse.ai
helm repo update

# Install with default values
helm install synapse synapse/synapse -n synapse --create-namespace

# Install with custom values
helm install synapse synapse/synapse -n synapse --create-namespace -f values.yaml

# Upgrade deployment
helm upgrade synapse synapse/synapse -n synapse
```

## Cloud Provider Deployments

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster --name synapse-cluster --region us-west-2 --nodes 3

# Deploy Synapse
kubectl apply -f k8s/

# Setup Application Load Balancer
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json

# Configure RDS for PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier synapse-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username synapse \
  --master-user-password your-password \
  --allocated-storage 20
```

### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create synapse-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10

# Get credentials
gcloud container clusters get-credentials synapse-cluster --zone us-central1-a

# Deploy Synapse
kubectl apply -f k8s/

# Setup Cloud SQL
gcloud sql instances create synapse-db \
  --database-version POSTGRES_13 \
  --tier db-f1-micro \
  --region us-central1
```

### Azure AKS

```bash
# Create resource group
az group create --name synapse-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group synapse-rg \
  --name synapse-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group synapse-rg --name synapse-cluster

# Deploy Synapse
kubectl apply -f k8s/

# Setup Azure Database for PostgreSQL
az postgres server create \
  --resource-group synapse-rg \
  --name synapse-db \
  --location eastus \
  --admin-user synapse \
  --admin-password your-password \
  --sku-name GP_Gen5_2
```

## Production Configuration

### Environment Variables

```bash
# Core Configuration
SYNAPSE_CONFIG=/app/config/production.yaml
PYTHONPATH=/app
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/synapse
REDIS_URL=redis://redis:6379/0
ELASTICSEARCH_URL=http://elasticsearch:9200

# Security Configuration
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
JWT_SECRET=your-jwt-secret

# Privacy Configuration
GLOBAL_PRIVACY_BUDGET=100.0
DEFAULT_QUERY_BUDGET=0.1

# Monitoring Configuration
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
SENTRY_DSN=your-sentry-dsn
```

### Production Configuration File

```yaml
# config/production.yaml
synapse:
  privacy:
    global_budget: 100.0
    default_query_budget: 0.1
    
  indexing:
    embedding_model: "all-MiniLM-L6-v2"
    batch_size: 1000
    update_interval: 1800
    
  security:
    encryption_enabled: true
    key_rotation_interval: 43200  # 12 hours
    
  api:
    host: "0.0.0.0"
    port: 8080
    cors_origins: ["https://yourdomain.com"]
    
  database:
    url: "${DATABASE_URL}"
    pool_size: 20
    max_overflow: 30
    
  redis:
    url: "${REDIS_URL}"
    max_connections: 100
    
  elasticsearch:
    url: "${ELASTICSEARCH_URL}"
    timeout: 30
    
  monitoring:
    prometheus_enabled: true
    metrics_port: 9090
    log_level: "INFO"
    sentry_dsn: "${SENTRY_DSN}"

# Production silo configurations
silos:
  # Configure your actual data sources here
  production_docs:
    name: "Production Documentation"
    type: "documentation"
    organization_id: "your_org"
    team_id: "engineering"
    data_classification: "internal"
    connection:
      type: "confluence"
      url: "https://your-org.atlassian.net"
      credentials: "${CONFLUENCE_CREDENTIALS}"
```

## Security Hardening

### Network Security

```yaml
# Network policies for Kubernetes
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: synapse-network-policy
  namespace: synapse
spec:
  podSelector:
    matchLabels:
      app: synapse-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
  - to: []
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 9200  # Elasticsearch
```

### TLS Configuration

```yaml
# TLS certificate configuration
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: synapse-tls
  namespace: synapse
spec:
  secretName: synapse-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - synapse.yourdomain.com
  - api.synapse.yourdomain.com
```

### RBAC Configuration

```yaml
# Kubernetes RBAC
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: synapse
  name: synapse-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: synapse-rolebinding
  namespace: synapse
subjects:
- kind: ServiceAccount
  name: synapse-serviceaccount
  namespace: synapse
roleRef:
  kind: Role
  name: synapse-role
  apiGroup: rbac.authorization.k8s.io
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'synapse-api'
    static_configs:
      - targets: ['synapse-api:8080']
    metrics_path: '/metrics'
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
      
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

### Grafana Dashboards

Key metrics to monitor:
- Query response times
- Privacy budget usage
- Silo indexing status
- Error rates and types
- Resource utilization
- Security events

### Logging Configuration

```yaml
# Structured logging configuration
logging:
  version: 1
  disable_existing_loggers: false
  formatters:
    standard:
      format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    json:
      format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: json
      stream: ext://sys.stdout
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: standard
      filename: /app/logs/synapse.log
      maxBytes: 10485760  # 10MB
      backupCount: 5
  loggers:
    synapse:
      level: DEBUG
      handlers: [console, file]
      propagate: false
  root:
    level: INFO
    handlers: [console]
```

## Backup and Disaster Recovery

### Database Backups

```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="synapse_backup_${DATE}.sql"

pg_dump -h postgres -U synapse -d synapse > "${BACKUP_DIR}/${BACKUP_FILE}"
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to cloud storage
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://your-backup-bucket/
```

### Configuration Backups

```bash
# Backup Kubernetes configurations
kubectl get all -n synapse -o yaml > synapse-k8s-backup.yaml

# Backup ConfigMaps and Secrets
kubectl get configmaps,secrets -n synapse -o yaml > synapse-config-backup.yaml
```

## Scaling Considerations

### Horizontal Scaling

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: synapse-api-hpa
  namespace: synapse
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: synapse-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Scaling

```yaml
# PostgreSQL cluster with read replicas
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: synapse-postgres
  namespace: synapse
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised
  
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
      
  bootstrap:
    initdb:
      database: synapse
      owner: synapse
      secret:
        name: synapse-postgres-credentials
        
  storage:
    size: 100Gi
    storageClass: fast-ssd
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   kubectl top pods -n synapse
   
   # Increase memory limits
   kubectl patch deployment synapse-api -n synapse -p '{"spec":{"template":{"spec":{"containers":[{"name":"synapse-api","resources":{"limits":{"memory":"4Gi"}}}]}}}}'
   ```

2. **Privacy Budget Exhaustion**
   ```bash
   # Check privacy budget status
   curl http://localhost:8080/api/v1/privacy/report
   
   # Reset privacy budget (use carefully)
   curl -X POST http://localhost:8080/api/v1/privacy/reset
   ```

3. **Slow Query Performance**
   ```bash
   # Check Elasticsearch cluster health
   curl http://elasticsearch:9200/_cluster/health
   
   # Rebuild indexes
   synapse indexer start --rebuild
   ```

### Health Checks

```bash
# API health check
curl http://localhost:8080/health

# Detailed health check
curl http://localhost:8080/api/v1/health/detailed

# Component status
curl http://localhost:8080/api/v1/stats
```

## Maintenance

### Regular Maintenance Tasks

1. **Update Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Rotate Encryption Keys**
   ```bash
   synapse encryption rotate-keys --all-silos
   ```

3. **Clean Old Logs**
   ```bash
   find /app/logs -name "*.log" -mtime +30 -delete
   ```

4. **Update Indexes**
   ```bash
   synapse indexer update --incremental
   ```

### Monitoring Checklist

- [ ] API response times < 500ms
- [ ] Privacy budget usage < 80%
- [ ] Error rate < 1%
- [ ] All silos indexed successfully
- [ ] Database connections healthy
- [ ] Disk usage < 80%
- [ ] Memory usage < 80%
- [ ] CPU usage < 70%

This deployment guide provides comprehensive coverage for deploying Project Synapse in various environments. Choose the deployment method that best fits your infrastructure and security requirements.
# KafkaTrace

A Kubernetes-based event processing system demonstrating modern SRE/DevOps practices with Apache Kafka, Python microservices, and comprehensive observability.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Producer      │───▶│     Kafka       │───▶│   Consumer      │
│   Service       │    │   (Bitnami)     │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │   Kubernetes    │
│   (Metrics)     │    │  (Dashboards)   │    │   (Orchestration)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Minikube or local Kubernetes cluster
- Helm 3.x
- kubectl
- Docker

### Option 1: Automated Deployment (Recommended)
```bash
# Run the automated deployment script
./deploy.sh

# Test the system
./test-system.sh
```

### Option 2: Manual Deployment

### 1. Start Minikube

> **Minimum recommended:** 4 CPUs, 8GB RAM  
> If you have less, adjust the `--memory` flag accordingly.

#### a) If you have no existing Minikube cluster:
```bash
minikube start --cpus 4 --memory 7000
```

> **If you get a memory error like this:**
> ```
> ❌  Exiting due to MK_USAGE: Docker Desktop has only 7837MB memory but you specified 8192MB
> ```
> **Use the maximum available memory:**
> ```bash
> minikube start --cpus 4 --memory 7000
> ```

#### b) If you already have a Minikube cluster:
```bash
minikube start
```

> **To change resources, you must first delete the cluster:**
> ```bash
> minikube delete
> minikube start --cpus 4 --memory 8192
> ```

#### c) Check Minikube status:
```bash
minikube status
```

> **Wait until you see:** `host: Running`, `kubelet: Running`, and `apiserver: Running`

### 2. Install Kafka
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install kafka bitnami/kafka --namespace kafka --create-namespace
```

### 3. Build and Deploy Services
```bash
# Build Docker images (if using local images)
eval $(minikube docker-env)
docker build -t kafkatrace-producer:latest ./producer-service
docker build -t kafkatrace-consumer:latest ./consumer-service

# Deploy producer service
helm install producer ./charts/producer

# Deploy consumer service  
helm install consumer ./charts/consumer
```

### 4. Verify Deployment
```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get svc

# Check Kafka is ready
kubectl get pods -n kafka
```

### 5. Test the System
```bash
# Start background event production
curl -X POST http://localhost:8000/start-background

# Check consumer logs for events
kubectl logs -l app.kubernetes.io/name=consumer -f

# Access services
kubectl port-forward svc/producer-service 8000:8000 &
kubectl port-forward svc/consumer-service 8001:8000 &

# Producer: http://localhost:8000
# Consumer: http://localhost:8001
```

## 📚 Learning Objectives

This project is designed to teach:

### Event-Driven Architecture
- **Kafka Fundamentals**: Topics, partitions, producers, consumers
- **Event Streaming**: Real-time data processing patterns
- **Service Communication**: Asynchronous messaging between microservices

### Kubernetes & Helm
- **Service Discovery**: How services find each other in K8s
- **Helm Charts**: Infrastructure as Code with templating
- **Resource Management**: CPU/memory limits, scaling policies

### Observability
- **Metrics Collection**: Prometheus scraping and custom metrics
- **Dashboard Creation**: Grafana visualization best practices
- **Alerting**: SRE-style monitoring and alerting rules

### DevOps Practices
- **Containerization**: Multi-stage Docker builds
- **CI/CD Ready**: Structure for GitHub Actions integration
- **Security**: Non-root containers, RBAC, network policies

## 🛠️ Project Structure

```
kafkatrace/
├── producer-service/          # Event producer microservice
│   ├── app.py                # FastAPI app with Kafka producer
│   ├── Dockerfile            # Multi-stage Docker build
│   └── requirements.txt      # Python dependencies
├── consumer-service/          # Event consumer microservice  
│   ├── app.py                # FastAPI app with Kafka consumer
│   ├── Dockerfile            # Multi-stage Docker build
│   └── requirements.txt      # Python dependencies
├── charts/                    # Helm charts for deployment
│   ├── producer/             # Producer service Helm chart
│   ├── consumer/             # Consumer service Helm chart
│   └── kafka/                # Kafka configuration (Bitnami)
├── observability/             # Prometheus, Grafana configs
│   ├── prometheus.yaml       # Prometheus scrape configuration
│   ├── grafana-dashboards/   # Grafana dashboard JSON files
│   └── alerts.yaml           # Alert rules (stub)
├── manifests/                 # Direct K8s manifests
├── docs/                      # Additional documentation
├── deploy.sh                  # Automated deployment script
├── test-system.sh            # System verification script
└── README.md                 # This file
```

## 🔧 Development Workflow

### Local Development Setup
```bash
# Clone and setup
git clone <your-repo-url>
cd KafkaTrace

# Install Python dependencies
pip install -r producer-service/requirements.txt
pip install -r consumer-service/requirements.txt

# Set up local Kafka (optional - for local development)
# You can use Docker Compose or run Kafka locally
```

### Local Development
```bash
# Run producer locally
cd producer-service
python app.py

# Run consumer locally (in another terminal)
cd consumer-service
python app.py
```

### Development Testing
```bash
# Run unit tests
pytest tests/

# Lint code
flake8 producer-service/ consumer-service/

# Type checking (if using mypy)
mypy producer-service/ consumer-service/

# Security scanning
bandit -r producer-service/ consumer-service/
```

### Kubernetes Development Workflow
```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=7000

# 2. Deploy to development environment
./deploy.sh

# 3. Test the deployment
./test-system.sh

# 4. Monitor logs
kubectl logs -l app.kubernetes.io/name=producer -f
kubectl logs -l app.kubernetes.io/name=consumer -f

# 5. Access services
kubectl port-forward svc/producer-service 8000:8000 &
kubectl port-forward svc/consumer-service 8001:8000 &
```

### Debugging Commands
```bash
# Check pod status
kubectl get pods -o wide

# Check service endpoints
kubectl get endpoints

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check logs with timestamps
kubectl logs -l app.kubernetes.io/name=producer --timestamps

# Exec into a pod for debugging
kubectl exec -it deployment/producer-service -- /bin/bash

# Check resource usage
kubectl top pods
kubectl top nodes

# Check Helm releases
helm list
helm status producer
helm status consumer
```

### Performance Testing
```bash
# Load test the producer
curl -X POST "http://localhost:8000/events/batch?count=1000"

# Monitor consumer lag
kubectl logs -l app.kubernetes.io/name=consumer | grep "lag"

# Check metrics
curl http://localhost:8000/metrics | grep events_produced_total
curl http://localhost:8001/metrics | grep events_consumed_total
```

## 📊 Monitoring & Observability

### Metrics Endpoints
- **Producer Metrics**: `/metrics` endpoint with event count, latency
- **Consumer Metrics**: `/metrics` endpoint with processing rate, errors
- **Kafka Metrics**: Available via Prometheus service discovery
- **Grafana Dashboards**: Pre-configured dashboards in `observability/grafana-dashboards/`

### Monitoring Commands
```bash
# Check Prometheus targets
kubectl port-forward svc/prometheus-server 9090:9090 &
# Visit http://localhost:9090/targets

# Check Grafana dashboards
kubectl port-forward svc/grafana 3000:3000 &
# Visit http://localhost:3000 (admin/admin)

# Query metrics directly
curl http://localhost:8000/metrics | grep events_produced_total
curl http://localhost:8001/metrics | grep events_consumed_total
```

### Log Aggregation
```bash
# Follow logs in real-time
kubectl logs -l app.kubernetes.io/name=producer -f --tail=100
kubectl logs -l app.kubernetes.io/name=consumer -f --tail=100

# Search logs
kubectl logs -l app.kubernetes.io/name=producer | grep "ERROR"
kubectl logs -l app.kubernetes.io/name=consumer | grep "Event processed"
```

## 🚀 CI/CD & Production Deployment

### GitHub Actions Workflow (TODO)
```yaml
# .github/workflows/deploy.yml
name: Deploy KafkaTrace

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r producer-service/requirements.txt
          pip install -r consumer-service/requirements.txt
          pytest tests/
  
  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Build and push Docker images
      - name: Deploy to Kubernetes cluster
```

### Production Deployment
```bash
# 1. Build production images
docker build -t your-registry/kafkatrace-producer:v1.0.0 ./producer-service
docker build -t your-registry/kafkatrace-consumer:v1.0.0 ./consumer-service

# 2. Push to registry
docker push your-registry/kafkatrace-producer:v1.0.0
docker push your-registry/kafkatrace-consumer:v1.0.0

# 3. Deploy with production values
helm install kafkatrace-prod ./charts/producer \
  --values charts/producer/values-prod.yaml \
  --namespace production

helm install kafkatrace-consumer-prod ./charts/consumer \
  --values charts/consumer/values-prod.yaml \
  --namespace production
```

### Production Configuration
```bash
# Create production values files
cp charts/producer/values.yaml charts/producer/values-prod.yaml
cp charts/consumer/values.yaml charts/consumer/values-prod.yaml

# Edit for production settings:
# - Increase replica count
# - Set resource limits
# - Enable autoscaling
# - Configure ingress
# - Add security policies
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper tests
4. Commit with conventional commits: `git commit -m "feat: add amazing feature"`
5. Push to your fork: `git push origin feature/amazing-feature`
6. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8, use type hints, add docstrings
- **YAML**: Use consistent indentation, add comments
- **Docker**: Multi-stage builds, security best practices
- **Helm**: Template best practices, validate charts

### Testing Requirements
- Unit tests for all new functionality
- Integration tests for service interactions
- Load tests for performance validation
- Documentation updates for new features

## 🎓 Learning Paths & Next Steps

### Beginner Learning Path
1. **Start with the basics**: Run `./deploy.sh` and explore the system
2. **Understand the architecture**: Study the service communication patterns
3. **Explore the code**: Read the TODO comments in the Python files
4. **Monitor the system**: Use the provided monitoring commands
5. **Make small changes**: Modify event generation or processing logic

### Intermediate Learning Path
1. **Add new metrics**: Implement custom Prometheus metrics
2. **Improve error handling**: Add retries and dead letter queues
3. **Enhance security**: Enable Kafka authentication and TLS
4. **Add testing**: Create unit and integration tests
5. **Optimize performance**: Tune resource limits and scaling

### Advanced Learning Path
1. **Implement tracing**: Add OpenTelemetry for distributed tracing
2. **Add data pipelines**: Integrate Kafka Connect for external systems
3. **Implement schema evolution**: Add Schema Registry for data governance
4. **Build CI/CD**: Create automated deployment pipelines
5. **Production hardening**: Add monitoring, alerting, and disaster recovery

### Common Learning Exercises
```bash
# Exercise 1: Add a new event type
# Modify producer-service/app.py to generate new event types
# Update consumer-service/app.py to handle them

# Exercise 2: Implement event filtering
# Add filtering logic in the consumer based on event properties

# Exercise 3: Add custom metrics
# Create new Prometheus metrics for business KPIs

# Exercise 4: Scale the system
# Increase replica counts and test horizontal scaling

# Exercise 5: Add monitoring alerts
# Create Prometheus alert rules for SLOs
```

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

**Kafka connection refused:**
```bash
# Check if Kafka is running
kubectl get pods -n kafka

# Check Kafka service
kubectl get svc -n kafka
```

**Services not starting:**
```bash
# Check pod logs
kubectl logs -f deployment/producer-service
kubectl logs -f deployment/consumer-service

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

**Prometheus not scraping:**
```bash
# Check service monitors
kubectl get servicemonitors

# Check Prometheus targets
kubectl port-forward svc/prometheus-server 9090:9090
# Then visit http://localhost:9090/targets
```

**Minikube memory issues:**
```bash
# Check available memory
docker system df

# Use less memory if needed
minikube start --cpus 2 --memory 4000

# Or delete and recreate with different settings
minikube delete
minikube start --cpus 4 --memory 7000
```
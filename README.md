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

### 1. Start Minikube
```bash
minikube start --cpus 4 --memory 8192
```

### 2. Install Kafka
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka --namespace kafka --create-namespace
```

### 3. Deploy Services
```bash
# Deploy producer service
helm install producer ./charts/producer

# Deploy consumer service  
helm install consumer ./charts/consumer
```

### 4. Access Services
```bash
# Port forward to access services
kubectl port-forward svc/producer-service 8000:8000
kubectl port-forward svc/consumer-service 8001:8000

# Access producer: http://localhost:8000
# Access consumer: http://localhost:8001
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
├── consumer-service/          # Event consumer microservice  
├── charts/                    # Helm charts for deployment
├── observability/             # Prometheus, Grafana configs
├── manifests/                 # Direct K8s manifests (optional)
└── docs/                      # Additional documentation
```

## 🔧 Development

### Local Development
```bash
# Run producer locally
cd producer-service
pip install -r requirements.txt
python app.py

# Run consumer locally  
cd consumer-service
pip install -r requirements.txt
python app.py
```

### Testing
```bash
# Run tests
pytest tests/

# Lint code
flake8 producer-service/ consumer-service/
```

## 📊 Monitoring

- **Producer Metrics**: `/metrics` endpoint with event count, latency
- **Consumer Metrics**: `/metrics` endpoint with processing rate, errors
- **Kafka Metrics**: Available via Prometheus service discovery
- **Grafana Dashboards**: Pre-configured dashboards in `observability/grafana-dashboards/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper tests
4. Submit a pull request

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
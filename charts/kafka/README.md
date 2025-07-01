# Kafka Chart for KafkaTrace

This directory contains configuration and instructions for deploying Kafka in the KafkaTrace project using Bitnami's Kafka Helm chart.

## Quick Start

### 1. Add Bitnami Helm Repository
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### 2. Install Kafka
```bash
# Create namespace
kubectl create namespace kafka

# Install Kafka with recommended configuration
helm install kafka bitnami/kafka \
  --namespace kafka \
  --values values.yaml
```

### 3. Verify Installation
```bash
# Check Kafka pods
kubectl get pods -n kafka

# Check Kafka services
kubectl get svc -n kafka

# Test Kafka connectivity
kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:latest -n kafka --command -- sleep infinity
kubectl exec --tty -i kafka-client --namespace kafka -- bash
```

## Configuration

The `values.yaml` file contains recommended configuration for the KafkaTrace project:

- **Single broker setup** for development (replicaCount: 1)
- **Auto topic creation** enabled
- **3 partitions** by default for new topics
- **7-day log retention** with 1GB size limit
- **Resource limits** appropriate for Minikube
- **Prometheus monitoring** enabled

## Service Discovery

Kafka will be available at:
- **Bootstrap servers**: `kafka.kafka.svc.cluster.local:9092`
- **Internal service**: `kafka.kafka.svc.cluster.local`
- **External access**: Use port-forwarding for local development

## Topics

The following topics will be auto-created when the services start:
- `events` - Main event stream for KafkaTrace

## Monitoring

Kafka exposes Prometheus metrics at:
- Kafka: `/metrics` endpoint
- Zookeeper: `/metrics` endpoint

ServiceMonitors are configured for automatic Prometheus scraping.

## Security

For production deployments, consider enabling:
- SASL authentication
- TLS encryption
- Network policies
- RBAC for service accounts

See the commented sections in `values.yaml` for configuration examples.

## Troubleshooting

### Common Issues

**Kafka pods not starting:**
```bash
kubectl describe pod -n kafka -l app.kubernetes.io/name=kafka
kubectl logs -n kafka -l app.kubernetes.io/name=kafka
```

**Connection refused:**
```bash
# Check if Kafka service is running
kubectl get svc -n kafka

# Check if pods are ready
kubectl get pods -n kafka
```

**Topic creation issues:**
```bash
# Check Kafka logs
kubectl logs -n kafka -l app.kubernetes.io/name=kafka -f
```

## Learning Objectives

This Kafka setup teaches:

1. **Helm Chart Usage**: How to use third-party charts with custom values
2. **Kafka Configuration**: Understanding broker settings and tuning
3. **Service Discovery**: How services find each other in Kubernetes
4. **Monitoring Integration**: Prometheus metrics and ServiceMonitors
5. **Resource Management**: CPU/memory limits and requests
6. **Security Patterns**: Authentication, encryption, and network policies

## Next Steps

1. **Scale Kafka**: Add more brokers for high availability
2. **Enable Security**: Configure SASL/TLS for production
3. **Add Kafka Connect**: For data pipeline integration
4. **Add Schema Registry**: For schema management
5. **Add Kafka UI**: For administration and monitoring 
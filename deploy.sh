#!/bin/bash

# KafkaTrace Deployment Script
# This script deploys the complete KafkaTrace system on Minikube

set -e  # Exit on any error

echo "🚀 Deploying KafkaTrace on Minikube..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed. Please install helm first."
    exit 1
fi

# Check if minikube is running
if ! minikube status | grep -q "Running"; then
    print_warning "Minikube is not running. Starting Minikube..."
    minikube start --cpus=4 --memory=7000
fi

print_success "Prerequisites check passed"

# Step 1: Add Bitnami Helm repository
print_status "Adding Bitnami Helm repository..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
print_success "Bitnami repository added"

# Step 2: Install Kafka
print_status "Installing Kafka..."
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
helm install kafka bitnami/kafka --namespace kafka --create-namespace \
    --set replicaCount=1 \
    --set zookeeper.replicaCount=1 \
    --set persistence.enabled=true \
    --set persistence.size=8Gi \
    --set resources.requests.memory=256Mi \
    --set resources.requests.cpu=250m \
    --set resources.limits.memory=512Mi \
    --set resources.limits.cpu=500m

print_success "Kafka installation initiated"

# Step 3: Wait for Kafka to be ready
print_status "Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n kafka --timeout=300s
print_success "Kafka is ready"

# Step 4: Build Docker images
print_status "Building Docker images..."
eval $(minikube docker-env)

print_status "Building producer image..."
docker build -t kafkatrace-producer:latest ./producer-service

print_status "Building consumer image..."
docker build -t kafkatrace-consumer:latest ./consumer-service

print_success "Docker images built"

# Step 5: Deploy producer service
print_status "Deploying producer service..."
helm install producer ./charts/producer
print_success "Producer service deployed"

# Step 6: Deploy consumer service
print_status "Deploying consumer service..."
helm install consumer ./charts/consumer
print_success "Consumer service deployed"

# Step 7: Wait for services to be ready
print_status "Waiting for services to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=producer --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=consumer --timeout=300s
print_success "Services are ready"

# Step 8: Display status
print_status "Deployment completed! Here's the status:"
echo ""
echo "📊 Pod Status:"
kubectl get pods
echo ""
echo "🔗 Services:"
kubectl get svc
echo ""
echo "📝 Kafka Status:"
kubectl get pods -n kafka
echo ""

# Step 9: Provide next steps
print_success "KafkaTrace is now running!"
echo ""
echo "🎯 Next steps:"
echo "1. Start background event production:"
echo "   kubectl port-forward svc/producer-service 8000:8000 &"
echo "   curl -X POST http://localhost:8000/start-background"
echo ""
echo "2. Monitor consumer logs:"
echo "   kubectl logs -l app.kubernetes.io/name=consumer -f"
echo ""
echo "3. Access services:"
echo "   Producer: http://localhost:8000"
echo "   Consumer: http://localhost:8001"
echo ""
echo "4. Check metrics:"
echo "   Producer metrics: http://localhost:8000/metrics"
echo "   Consumer metrics: http://localhost:8001/metrics"
echo ""
echo "🔧 To clean up:"
echo "   helm uninstall producer consumer"
echo "   helm uninstall kafka -n kafka"
echo "   kubectl delete namespace kafka"
echo ""

print_success "Deployment script completed successfully!" 
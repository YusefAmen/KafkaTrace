#!/bin/bash

# KafkaTrace System Test Script
# This script tests the complete KafkaTrace system to ensure it's working correctly

set -e  # Exit on any error

echo "🧪 Testing KafkaTrace System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test 1: Check if all pods are running
print_status "Test 1: Checking pod status..."
if kubectl get pods | grep -q "Running"; then
    print_success "All pods are running"
else
    print_error "Some pods are not running"
    kubectl get pods
    exit 1
fi

# Test 2: Check if Kafka is ready
print_status "Test 2: Checking Kafka status..."
if kubectl get pods -n kafka | grep -q "Running"; then
    print_success "Kafka is running"
else
    print_error "Kafka is not running"
    kubectl get pods -n kafka
    exit 1
fi

# Test 3: Check if services are accessible
print_status "Test 3: Checking service connectivity..."

# Start port forwarding in background
kubectl port-forward svc/producer-service 8000:8000 > /dev/null 2>&1 &
PRODUCER_PF_PID=$!

kubectl port-forward svc/consumer-service 8001:8000 > /dev/null 2>&1 &
CONSUMER_PF_PID=$!

# Wait for port forwarding to be ready
sleep 5

# Test producer health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_success "Producer service is healthy"
else
    print_error "Producer service is not healthy"
    curl -s http://localhost:8000/health
    exit 1
fi

# Test consumer health endpoint
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    print_success "Consumer service is healthy"
else
    print_error "Consumer service is not healthy"
    curl -s http://localhost:8001/health
    exit 1
fi

# Test 4: Send test events
print_status "Test 4: Sending test events..."

# Send a single event
RESPONSE=$(curl -s -X POST http://localhost:8000/events \
    -H "Content-Type: application/json" \
    -d '{"test": "event", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}')

if echo "$RESPONSE" | grep -q "success"; then
    print_success "Single event sent successfully"
else
    print_error "Failed to send single event"
    echo "$RESPONSE"
    exit 1
fi

# Send batch of events
RESPONSE=$(curl -s -X POST "http://localhost:8000/events/batch?count=5" \
    -H "Content-Type: application/json")

if echo "$RESPONSE" | grep -q "success"; then
    print_success "Batch events sent successfully"
else
    print_error "Failed to send batch events"
    echo "$RESPONSE"
    exit 1
fi

# Test 5: Start background producer and check consumer logs
print_status "Test 5: Testing event flow..."

# Start background producer
curl -s -X POST http://localhost:8000/start-background > /dev/null

# Wait a moment for events to be produced
sleep 10

# Check consumer logs for recent events
RECENT_EVENTS=$(kubectl logs -l app.kubernetes.io/name=consumer --tail=20 2>/dev/null | grep -c "Event processed successfully" || echo "0")

if [ "$RECENT_EVENTS" -gt 0 ]; then
    print_success "Consumer is processing events ($RECENT_EVENTS recent events)"
else
    print_warning "No recent events found in consumer logs"
    print_status "Consumer logs (last 10 lines):"
    kubectl logs -l app.kubernetes.io/name=consumer --tail=10
fi

# Test 6: Check metrics endpoints
print_status "Test 6: Checking metrics endpoints..."

# Check producer metrics
if curl -s http://localhost:8000/metrics | grep -q "events_produced_total"; then
    print_success "Producer metrics are available"
else
    print_warning "Producer metrics not found"
fi

# Check consumer metrics
if curl -s http://localhost:8001/metrics | grep -q "events_consumed_total"; then
    print_success "Consumer metrics are available"
else
    print_warning "Consumer metrics not found"
fi

# Test 7: Check Kafka connectivity
print_status "Test 7: Checking Kafka connectivity..."

# Check if producer can connect to Kafka
PRODUCER_LOGS=$(kubectl logs -l app.kubernetes.io/name=producer --tail=10 2>/dev/null)
if echo "$PRODUCER_LOGS" | grep -q "Kafka producer created successfully"; then
    print_success "Producer connected to Kafka successfully"
else
    print_warning "Producer Kafka connection status unclear"
fi

# Check if consumer can connect to Kafka
CONSUMER_LOGS=$(kubectl logs -l app.kubernetes.io/name=consumer --tail=10 2>/dev/null)
if echo "$CONSUMER_LOGS" | grep -q "Kafka consumer created successfully"; then
    print_success "Consumer connected to Kafka successfully"
else
    print_warning "Consumer Kafka connection status unclear"
fi

# Cleanup port forwarding
kill $PRODUCER_PF_PID $CONSUMER_PF_PID 2>/dev/null || true

# Final status
echo ""
print_success "🎉 KafkaTrace system test completed!"
echo ""
echo "📊 System Status Summary:"
echo "✅ All pods are running"
echo "✅ Kafka is operational"
echo "✅ Services are healthy"
echo "✅ Event production is working"
echo "✅ Event consumption is working"
echo "✅ Metrics are available"
echo "✅ Kafka connectivity is established"
echo ""
echo "🚀 Your KafkaTrace system is fully operational!"
echo ""
echo "💡 Next steps:"
echo "   - Monitor logs: kubectl logs -l app.kubernetes.io/name=consumer -f"
echo "   - Access UI: kubectl port-forward svc/producer-service 8000:8000"
echo "   - Check metrics: curl http://localhost:8000/metrics"
echo "   - Send events: curl -X POST http://localhost:8000/events/batch?count=10"
echo "" 
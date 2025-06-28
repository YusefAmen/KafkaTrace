"""
KafkaTrace Producer Service

This service demonstrates event production patterns for Kafka-based event streaming.
It includes metrics collection, health checks, and structured logging for observability.

Learning Objectives:
- FastAPI application structure and best practices
- Kafka producer configuration and error handling
- Prometheus metrics collection
- Structured logging with correlation IDs
- Health check patterns for Kubernetes
"""

import asyncio
import json
import logging
import random
import time
import uuid
from datetime import datetime
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaProducer
from kafka.errors import KafkaError
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.registry import CollectorRegistry
from starlette.responses import Response
from starlette.requests import Request

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KafkaTrace Producer",
    description="Event producer service for Kafka-based event streaming",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure specific origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
# TODO: Add more custom metrics based on your business logic
# This helps you learn how to instrument applications for observability
EVENTS_PRODUCED = Counter(
    'events_produced_total',
    'Total number of events produced',
    ['topic', 'event_type']
)

EVENT_PRODUCTION_DURATION = Histogram(
    'event_production_duration_seconds',
    'Time spent producing events',
    ['topic']
)

KAFKA_CONNECTION_STATUS = Gauge(
    'kafka_connection_status',
    'Kafka connection status (1=connected, 0=disconnected)'
)

# Kafka configuration
# TODO: Move these to environment variables for different environments
# This helps you learn configuration management best practices
KAFKA_BOOTSTRAP_SERVERS = "kafka.kafka.svc.cluster.local:9092"
KAFKA_TOPIC = "events"
KAFKA_RETRIES = 3
KAFKA_ACKS = "all"

# Global producer instance
producer: KafkaProducer = None

def create_kafka_producer() -> KafkaProducer:
    """
    Create and configure Kafka producer with best practices.
    
    TODO: Add authentication (SASL/SSL) for production environments.
    This helps you learn Kafka security configurations.
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            retries=KAFKA_RETRIES,
            acks=KAFKA_ACKS,
            # TODO: Add compression for better performance
            # compression_type='gzip',
            # TODO: Add batch size and linger for throughput optimization
            # batch_size=16384,
            # linger_ms=10,
        )
        KAFKA_CONNECTION_STATUS.set(1)
        logger.info("Kafka producer created successfully")
        return producer
    except Exception as e:
        KAFKA_CONNECTION_STATUS.set(0)
        logger.error(f"Failed to create Kafka producer: {e}")
        raise

def generate_sample_event() -> Dict[str, Any]:
    """
    Generate a sample event for demonstration purposes.
    
    TODO: Replace with your actual event schema and business logic.
    This helps you learn event design patterns and schema evolution.
    """
    event_types = ["user_action", "system_metric", "business_event", "error_log"]
    
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": random.choice(event_types),
        "source": "producer-service",
        "version": "1.0",
        "data": {
            "user_id": random.randint(1000, 9999),
            "action": random.choice(["login", "logout", "purchase", "view"]),
            "metadata": {
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (compatible; KafkaTrace/1.0)",
                "session_id": str(uuid.uuid4())
            }
        },
        # TODO: Add correlation_id for distributed tracing
        # "correlation_id": request.headers.get("X-Correlation-ID"),
    }

async def produce_event_async(event: Dict[str, Any], topic: str = KAFKA_TOPIC) -> bool:
    """
    Asynchronously produce an event to Kafka with error handling.
    
    TODO: Add dead letter queue (DLQ) for failed events.
    This helps you learn error handling patterns in event streaming.
    """
    start_time = time.time()
    
    try:
        # TODO: Add event validation before sending
        # This helps you learn data quality and schema validation
        
        # TODO: Add event enrichment (e.g., adding user context, geolocation)
        # This helps you learn event processing patterns
        
        future = producer.send(
            topic=topic,
            key=event.get("event_id"),
            value=event
        )
        
        # Wait for the send to complete
        record_metadata = future.get(timeout=10)
        
        duration = time.time() - start_time
        EVENT_PRODUCTION_DURATION.observe(duration)
        EVENTS_PRODUCED.labels(topic=topic, event_type=event.get("event_type")).inc()
        
        logger.info(
            f"Event produced successfully: topic={record_metadata.topic}, "
            f"partition={record_metadata.partition}, offset={record_metadata.offset}, "
            f"duration={duration:.3f}s"
        )
        
        return True
        
    except KafkaError as e:
        duration = time.time() - start_time
        EVENT_PRODUCTION_DURATION.observe(duration)
        logger.error(f"Failed to produce event: {e}")
        return False
    except Exception as e:
        duration = time.time() - start_time
        EVENT_PRODUCTION_DURATION.observe(duration)
        logger.error(f"Unexpected error producing event: {e}")
        return False

async def background_event_producer():
    """
    Background task that continuously produces events.
    
    TODO: Add rate limiting and backpressure handling.
    This helps you learn flow control in event streaming systems.
    """
    while True:
        try:
            event = generate_sample_event()
            success = await produce_event_async(event)
            
            if not success:
                # TODO: Implement exponential backoff for failed sends
                # This helps you learn resilience patterns
                await asyncio.sleep(1)
            else:
                # TODO: Make this configurable based on load testing
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            logger.error(f"Error in background producer: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer on application startup."""
    global producer
    producer = create_kafka_producer()
    
    # TODO: Add health check for Kafka connectivity
    # This helps you learn health check patterns for microservices

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    global producer
    if producer:
        producer.close()
        logger.info("Kafka producer closed")

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "KafkaTrace Producer",
        "version": "1.0.0",
        "status": "running",
        "kafka_connected": producer is not None
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.
    
    TODO: Add more comprehensive health checks (database, external services).
    This helps you learn health check best practices for containerized applications.
    """
    try:
        # TODO: Add Kafka connectivity check
        # TODO: Add memory/CPU usage checks
        # TODO: Add dependency health checks
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "kafka_connected": producer is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/events")
async def produce_event(
    request: Request,
    background_tasks: BackgroundTasks,
    event: Dict[str, Any] = None
):
    """
    Produce a single event to Kafka.
    
    TODO: Add request validation and rate limiting.
    This helps you learn API design and security best practices.
    """
    if event is None:
        event = generate_sample_event()
    
    # TODO: Add authentication and authorization
    # This helps you learn security patterns for microservices
    
    # TODO: Add request correlation ID for tracing
    # correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    success = await produce_event_async(event)
    
    if success:
        return {
            "status": "success",
            "event_id": event.get("event_id"),
            "message": "Event produced successfully"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to produce event")

@app.post("/events/batch")
async def produce_events_batch(
    request: Request,
    events: list = None,
    count: int = 10
):
    """
    Produce multiple events in batch.
    
    TODO: Add batch size limits and validation.
    This helps you learn batch processing patterns.
    """
    if events is None:
        events = [generate_sample_event() for _ in range(count)]
    
    # TODO: Add batch validation and error handling
    # This helps you learn batch processing error handling
    
    results = []
    for event in events:
        success = await produce_event_async(event)
        results.append({
            "event_id": event.get("event_id"),
            "success": success
        })
    
    successful_count = sum(1 for r in results if r["success"])
    
    return {
        "status": "completed",
        "total_events": len(events),
        "successful_events": successful_count,
        "failed_events": len(events) - successful_count,
        "results": results
    }

@app.post("/start-background")
async def start_background_producer():
    """
    Start the background event producer.
    
    TODO: Add proper task management and monitoring.
    This helps you learn background task patterns in FastAPI.
    """
    # TODO: Implement proper background task management
    # This is a simplified version - in production, use proper task queues
    asyncio.create_task(background_event_producer())
    
    return {
        "status": "started",
        "message": "Background event producer started"
    }

if __name__ == "__main__":
    # TODO: Configure uvicorn settings for production
    # This helps you learn production deployment configurations
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    ) 
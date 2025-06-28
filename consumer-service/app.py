"""
KafkaTrace Consumer Service

This service demonstrates event consumption patterns for Kafka-based event streaming.
It includes metrics collection, health checks, and structured logging for observability.

Learning Objectives:
- FastAPI application structure and best practices
- Kafka consumer configuration and error handling
- Prometheus metrics collection
- Structured logging with correlation IDs
- Health check patterns for Kubernetes
- Event processing and filtering patterns
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
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
    title="KafkaTrace Consumer",
    description="Event consumer service for Kafka-based event streaming",
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
EVENTS_CONSUMED = Counter(
    'events_consumed_total',
    'Total number of events consumed',
    ['topic', 'event_type', 'status']
)

EVENT_PROCESSING_DURATION = Histogram(
    'event_processing_duration_seconds',
    'Time spent processing events',
    ['event_type']
)

KAFKA_CONNECTION_STATUS = Gauge(
    'kafka_connection_status',
    'Kafka connection status (1=connected, 0=disconnected)'
)

CONSUMER_LAG = Gauge(
    'consumer_lag',
    'Consumer lag per partition',
    ['topic', 'partition']
)

# Kafka configuration
# TODO: Move these to environment variables for different environments
# This helps you learn configuration management best practices
KAFKA_BOOTSTRAP_SERVERS = "kafka.kafka.svc.cluster.local:9092"
KAFKA_TOPIC = "events"
KAFKA_GROUP_ID = "kafkatrace-consumer-group"
KAFKA_AUTO_OFFSET_RESET = "earliest"

# Global consumer instance
consumer: KafkaConsumer = None
consumer_task: Optional[asyncio.Task] = None

def create_kafka_consumer() -> KafkaConsumer:
    """
    Create and configure Kafka consumer with best practices.
    
    TODO: Add authentication (SASL/SSL) for production environments.
    This helps you learn Kafka security configurations.
    """
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_GROUP_ID,
            auto_offset_reset=KAFKA_AUTO_OFFSET_RESET,
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            # TODO: Add consumer timeout and session timeout configurations
            # session_timeout_ms=30000,
            # heartbeat_interval_ms=3000,
            # TODO: Add max poll records for batch processing
            # max_poll_records=500,
        )
        KAFKA_CONNECTION_STATUS.set(1)
        logger.info("Kafka consumer created successfully")
        return consumer
    except Exception as e:
        KAFKA_CONNECTION_STATUS.set(0)
        logger.error(f"Failed to create Kafka consumer: {e}")
        raise

def process_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single event with business logic.
    
    TODO: Implement your actual event processing logic here.
    This helps you learn event processing patterns and data transformation.
    """
    start_time = time.time()
    event_type = event.get("event_type", "unknown")
    
    try:
        # TODO: Add event validation and schema checking
        # This helps you learn data quality and validation patterns
        
        # TODO: Add event enrichment (e.g., user lookup, geolocation)
        # This helps you learn data enrichment patterns
        
        # TODO: Add event filtering based on business rules
        # This helps you learn event filtering and routing patterns
        
        # TODO: Add event transformation (e.g., format conversion, aggregation)
        # This helps you learn data transformation patterns
        
        # TODO: Add event persistence to database
        # This helps you learn data persistence patterns
        
        # TODO: Add event routing to other systems
        # This helps you learn event routing and integration patterns
        
        # Example processing logic (replace with your actual logic)
        processed_event = {
            "processed_at": datetime.utcnow().isoformat(),
            "original_event": event,
            "processing_metadata": {
                "processor": "kafkatrace-consumer",
                "version": "1.0",
                "processing_time_ms": (time.time() - start_time) * 1000
            }
        }
        
        # TODO: Add business logic based on event type
        if event_type == "user_action":
            # TODO: Process user actions (e.g., analytics, notifications)
            pass
        elif event_type == "system_metric":
            # TODO: Process system metrics (e.g., alerting, monitoring)
            pass
        elif event_type == "business_event":
            # TODO: Process business events (e.g., reporting, workflows)
            pass
        elif event_type == "error_log":
            # TODO: Process error logs (e.g., alerting, debugging)
            pass
        
        duration = time.time() - start_time
        EVENT_PROCESSING_DURATION.observe(duration)
        EVENTS_CONSUMED.labels(
            topic=KAFKA_TOPIC,
            event_type=event_type,
            status="success"
        ).inc()
        
        logger.info(
            f"Event processed successfully: event_id={event.get('event_id')}, "
            f"event_type={event_type}, duration={duration:.3f}s"
        )
        
        return processed_event
        
    except Exception as e:
        duration = time.time() - start_time
        EVENT_PROCESSING_DURATION.observe(duration)
        EVENTS_CONSUMED.labels(
            topic=KAFKA_TOPIC,
            event_type=event_type,
            status="error"
        ).inc()
        
        logger.error(f"Failed to process event {event.get('event_id')}: {e}")
        
        # TODO: Add dead letter queue (DLQ) for failed events
        # This helps you learn error handling patterns in event streaming
        
        raise

async def consume_events():
    """
    Main event consumption loop with error handling and metrics.
    
    TODO: Add rate limiting and backpressure handling.
    This helps you learn flow control in event streaming systems.
    """
    global consumer
    
    if not consumer:
        logger.error("Kafka consumer not initialized")
        return
    
    logger.info("Starting event consumption loop")
    
    try:
        for message in consumer:
            try:
                # TODO: Add message validation before processing
                # This helps you learn message validation patterns
                
                event = message.value
                if not event:
                    logger.warning("Received empty message, skipping")
                    continue
                
                # TODO: Add correlation ID extraction for distributed tracing
                # correlation_id = event.get("correlation_id")
                
                # Process the event
                processed_event = process_event(event)
                
                # TODO: Add event acknowledgment and offset management
                # This helps you learn consumer offset management
                
                # TODO: Add batch processing for better performance
                # This helps you learn batch processing patterns
                
                # TODO: Add event routing based on content
                # This helps you learn event routing patterns
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # TODO: Add retry logic with exponential backoff
                # This helps you learn resilience patterns
                
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down consumer")
    except Exception as e:
        logger.error(f"Unexpected error in consumer loop: {e}")
        KAFKA_CONNECTION_STATUS.set(0)
    finally:
        if consumer:
            consumer.close()
            logger.info("Kafka consumer closed")

async def start_consumer():
    """Start the Kafka consumer in the background."""
    global consumer_task
    if consumer_task is None or consumer_task.done():
        consumer_task = asyncio.create_task(consume_events())
        logger.info("Consumer task started")

async def stop_consumer():
    """Stop the Kafka consumer gracefully."""
    global consumer_task
    if consumer_task and not consumer_task.done():
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        logger.info("Consumer task stopped")

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka consumer on application startup."""
    global consumer
    consumer = create_kafka_consumer()
    
    # TODO: Add health check for Kafka connectivity
    # This helps you learn health check patterns for microservices

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    await stop_consumer()
    global consumer
    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed")

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "KafkaTrace Consumer",
        "version": "1.0.0",
        "status": "running",
        "kafka_connected": consumer is not None,
        "consumer_running": consumer_task is not None and not consumer_task.done()
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
            "kafka_connected": consumer is not None,
            "consumer_running": consumer_task is not None and not consumer_task.done()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/start")
async def start_consumer_endpoint():
    """
    Start the Kafka consumer manually.
    
    TODO: Add proper task management and monitoring.
    This helps you learn background task patterns in FastAPI.
    """
    await start_consumer()
    return {
        "status": "started",
        "message": "Kafka consumer started"
    }

@app.post("/stop")
async def stop_consumer_endpoint():
    """
    Stop the Kafka consumer manually.
    
    TODO: Add proper task management and monitoring.
    This helps you learn background task patterns in FastAPI.
    """
    await stop_consumer()
    return {
        "status": "stopped",
        "message": "Kafka consumer stopped"
    }

@app.get("/status")
async def consumer_status():
    """
    Get detailed consumer status and metrics.
    
    TODO: Add more detailed metrics and status information.
    This helps you learn monitoring and observability patterns.
    """
    if not consumer:
        return {
            "status": "not_initialized",
            "message": "Kafka consumer not initialized"
        }
    
    # TODO: Add consumer group information
    # TODO: Add partition assignment information
    # TODO: Add lag information per partition
    
    return {
        "status": "running" if consumer_task and not consumer_task.done() else "stopped",
        "kafka_connected": consumer is not None,
        "topic": KAFKA_TOPIC,
        "group_id": KAFKA_GROUP_ID,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/process-event")
async def process_single_event(event: Dict[str, Any]):
    """
    Process a single event manually (for testing).
    
    TODO: Add request validation and rate limiting.
    This helps you learn API design and security best practices.
    """
    try:
        processed_event = process_event(event)
        return {
            "status": "success",
            "processed_event": processed_event
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process event: {str(e)}")

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
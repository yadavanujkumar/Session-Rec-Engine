"""FastAPI application for session-based recommendations."""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import torch

from ..config import get_settings, Settings
from ..models import SASRec
from ..storage import SessionStore, VectorStore
from ..coldstart import ThompsonSamplingBandit, ColdStartHandler
from ..monitoring import MetricsTracker
from ..utils import ItemCatalog
from ..service import RecommendationService


# Request/Response models
class ClickEvent(BaseModel):
    """Click event data."""
    session_id: str = Field(..., description="Unique session identifier")
    item_id: str = Field(..., description="Item that was clicked")


class RecommendationRequest(BaseModel):
    """Recommendation request."""
    session_id: str = Field(..., description="Unique session identifier")


class RecommendationResponse(BaseModel):
    """Recommendation response."""
    session_id: str
    recommendations: List[str]
    used_coldstart: bool
    message: str


class FeedbackEvent(BaseModel):
    """Feedback event for recommendation."""
    session_id: str = Field(..., description="Session identifier")
    recommended_items: List[str] = Field(..., description="Items that were recommended")
    clicked_item: Optional[str] = Field(None, description="Item that was clicked")


class MetricsResponse(BaseModel):
    """Metrics response."""
    hit_rate_at_10: float
    p99_latency_ms: float
    p50_latency_ms: float
    avg_latency_ms: float
    total_requests: int
    coldstart_requests: int
    model_requests: int
    coldstart_percentage: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    components: dict


# Global service instance
recommendation_service: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    """Get recommendation service instance."""
    global recommendation_service
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return recommendation_service


# Create FastAPI app
app = FastAPI(
    title="Privacy-First Session-Based Recommendation API",
    description="Real-time recommendation system for anonymous users",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global recommendation_service
    
    settings = get_settings()
    
    # Create sample item catalog
    item_catalog = ItemCatalog.create_sample_catalog(num_items=100)
    
    # Initialize model
    model = SASRec(
        num_items=item_catalog.get_num_items(),
        embedding_dim=settings.embedding_dim,
        num_heads=settings.num_heads,
        num_layers=settings.num_layers,
        dropout=settings.dropout,
        max_seq_len=settings.sequence_length
    )
    
    # Initialize storage
    session_store = SessionStore(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        expiry_seconds=settings.session_expiry_seconds
    )
    
    vector_store = VectorStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=settings.qdrant_collection_name,
        embedding_dim=settings.embedding_dim
    )
    
    # Initialize cold-start handler
    bandit = ThompsonSamplingBandit(item_ids=item_catalog.get_all_item_ids())
    coldstart_handler = ColdStartHandler(
        bandit=bandit,
        threshold=settings.cold_start_threshold
    )
    
    # Initialize metrics
    metrics_tracker = MetricsTracker(window_size=1000)
    
    # Create recommendation service
    recommendation_service = RecommendationService(
        model=model,
        session_store=session_store,
        vector_store=vector_store,
        coldstart_handler=coldstart_handler,
        metrics_tracker=metrics_tracker,
        item_catalog=item_catalog,
        sequence_length=settings.sequence_length,
        top_k=settings.top_k
    )
    
    print("✓ Recommendation service initialized successfully")


@app.post("/api/v1/click", response_model=dict)
async def record_click(
    event: ClickEvent,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Record a click event.
    
    This endpoint accepts click events and stores them in the session.
    Sessions automatically expire after 30 minutes for privacy.
    """
    try:
        service.add_click_event(event.session_id, event.item_id)
        return {
            "status": "success",
            "message": f"Click event recorded for session {event.session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get recommendations for a session.
    
    Returns personalized recommendations based on the session history.
    If the session has less than 2 clicks, returns trending items using
    Multi-Armed Bandit algorithm.
    """
    try:
        recommendations, used_coldstart = service.get_recommendations(request.session_id)
        
        strategy = "cold-start (trending items)" if used_coldstart else "model-based"
        
        return RecommendationResponse(
            session_id=request.session_id,
            recommendations=recommendations,
            used_coldstart=used_coldstart,
            message=f"Recommendations generated using {strategy} strategy"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/feedback", response_model=dict)
async def record_feedback(
    event: FeedbackEvent,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Record feedback for recommendations.
    
    This helps improve the Multi-Armed Bandit algorithm for cold-start scenarios.
    """
    try:
        service.record_feedback(
            event.session_id,
            event.recommended_items,
            event.clicked_item
        )
        return {
            "status": "success",
            "message": "Feedback recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics", response_model=MetricsResponse)
async def get_metrics(
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get real-time metrics.
    
    Returns:
    - Hit Rate@10: Percentage of recommendations that were clicked
    - P99 Latency: 99th percentile response time
    - Request statistics
    """
    try:
        metrics = service.metrics_tracker.get_metrics_summary()
        return MetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check(
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Health check endpoint.
    
    Checks the status of all components (Redis, Qdrant, Model).
    """
    try:
        health = service.health_check()
        all_healthy = all(health.values())
        status = "healthy" if all_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            components=health
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Privacy-First Session-Based Recommendation System",
        "version": "1.0.0",
        "docs": "/docs"
    }

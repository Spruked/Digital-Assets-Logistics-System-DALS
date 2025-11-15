# predictive_api.py
# Phase 11-A: Predictive Failure Modeling API
# REST endpoints for accessing failure predictions and managing the predictive engine
# Version 1.0.0

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from iss_module.csmm.predictive_failure_modeling import get_predictive_engine, PredictionResult

logger = logging.getLogger("DALS.Predictive.API")

# Pydantic models for API responses
class PredictionResponse(BaseModel):
    module: str
    failure_type: str
    time_to_failure: float
    confidence: float
    risk_level: str
    recommended_actions: List[str]
    timestamp: str

class HealthReadingRequest(BaseModel):
    module: str
    health_score: int
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    response_time: Optional[float] = None
    error_rate: Optional[float] = None

class PredictionSummary(BaseModel):
    total_predictions: int
    critical_predictions: int
    high_risk_predictions: int
    modules_at_risk: List[str]
    timestamp: str

class LearningEvent(BaseModel):
    module: str
    predicted_failure: str
    actual_outcome: str
    accuracy: float
    timestamp: str

# Create router
predictive_router = APIRouter(
    prefix="/predictive",
    tags=["predictive-failure-modeling"],
    responses={404: {"description": "Not found"}}
)

@predictive_router.get("/health", summary="Get predictive engine health")
async def get_predictive_health():
    """
    Get the health status of the predictive failure modeling engine.

    Returns:
        Dict containing engine status and basic metrics
    """
    try:
        engine = get_predictive_engine()

        return {
            "status": "active",
            "engine_type": "PredictiveFailureEngine",
            "monitored_modules": len(engine.health_history),
            "active_predictions": len(engine.active_predictions),
            "learned_patterns": len(engine.failure_patterns),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting predictive health: {e}")
        raise HTTPException(status_code=500, detail=f"Engine health check failed: {str(e)}")

@predictive_router.post("/record-health", summary="Record health reading")
async def record_health_reading(reading: HealthReadingRequest):
    """
    Record a health reading for analysis and prediction.

    Args:
        reading: Health metrics for a module

    Returns:
        Success confirmation
    """
    try:
        engine = get_predictive_engine()

        health_data = {
            "health_score": reading.health_score,
            "cpu_usage": reading.cpu_usage,
            "memory_usage": reading.memory_usage,
            "response_time": reading.response_time,
            "error_rate": reading.error_rate
        }

        engine.record_health_reading(reading.module, health_data)

        return {
            "status": "recorded",
            "module": reading.module,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error recording health reading: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record health reading: {str(e)}")

@predictive_router.get("/predictions", summary="Get all predictions")
async def get_all_predictions():
    """
    Get all active failure predictions.

    Returns:
        List of all current predictions
    """
    try:
        engine = get_predictive_engine()
        predictions = engine.get_all_predictions()

        response = []
        for module, prediction in predictions.items():
            response.append(PredictionResponse(
                module=prediction.module,
                failure_type=prediction.failure_type,
                time_to_failure=prediction.time_to_failure,
                confidence=prediction.confidence,
                risk_level=prediction.risk_level,
                recommended_actions=prediction.recommended_actions,
                timestamp=prediction.timestamp.isoformat()
            ))

        return {
            "predictions": response,
            "count": len(response),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get predictions: {str(e)}")

@predictive_router.get("/predictions/{module}", summary="Get prediction for module")
async def get_module_prediction(module: str):
    """
    Get failure prediction for a specific module.

    Args:
        module: Module name to check

    Returns:
        Prediction for the module or null if none
    """
    try:
        engine = get_predictive_engine()
        prediction = engine.get_prediction_for_module(module)

        if prediction:
            return PredictionResponse(
                module=prediction.module,
                failure_type=prediction.failure_type,
                time_to_failure=prediction.time_to_failure,
                confidence=prediction.confidence,
                risk_level=prediction.risk_level,
                recommended_actions=prediction.recommended_actions,
                timestamp=prediction.timestamp.isoformat()
            )
        else:
            return {
                "module": module,
                "prediction": None,
                "status": "no_prediction",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting module prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get prediction for {module}: {str(e)}")

@predictive_router.get("/summary", summary="Get prediction summary")
async def get_prediction_summary():
    """
    Get a summary of current predictions and risk levels.

    Returns:
        Summary of prediction status
    """
    try:
        engine = get_predictive_engine()
        predictions = engine.get_all_predictions()

        critical_count = sum(1 for p in predictions.values() if p.risk_level == 'critical')
        high_count = sum(1 for p in predictions.values() if p.risk_level == 'high')
        modules_at_risk = list(predictions.keys())

        summary = PredictionSummary(
            total_predictions=len(predictions),
            critical_predictions=critical_count,
            high_risk_predictions=high_count,
            modules_at_risk=modules_at_risk,
            timestamp=datetime.utcnow().isoformat()
        )

        return summary
    except Exception as e:
        logger.error(f"Error getting prediction summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get prediction summary: {str(e)}")

@predictive_router.delete("/predictions/{module}", summary="Clear prediction for module")
async def clear_module_prediction(module: str):
    """
    Clear any active prediction for a module.

    Args:
        module: Module name to clear prediction for

    Returns:
        Success confirmation
    """
    try:
        engine = get_predictive_engine()
        engine.clear_prediction(module)

        return {
            "status": "cleared",
            "module": module,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear prediction for {module}: {str(e)}")

@predictive_router.post("/learn", summary="Learn from prediction outcome")
async def learn_from_outcome(learning: LearningEvent):
    """
    Learn from the accuracy of a prediction to improve future predictions.

    Args:
        learning: Learning event with predicted vs actual outcome

    Returns:
        Success confirmation
    """
    try:
        engine = get_predictive_engine()
        engine.learn_from_outcome(
            learning.module,
            learning.predicted_failure,
            learning.actual_outcome
        )

        return {
            "status": "learned",
            "module": learning.module,
            "accuracy": learning.accuracy,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error learning from outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to learn from outcome: {str(e)}")

@predictive_router.get("/patterns", summary="Get learned failure patterns")
async def get_failure_patterns():
    """
    Get all learned failure patterns used for predictions.

    Returns:
        Dictionary of failure patterns
    """
    try:
        engine = get_predictive_engine()

        patterns = {}
        for pattern_id, pattern in engine.failure_patterns.items():
            patterns[pattern_id] = {
                "pattern_id": pattern.pattern_id,
                "trigger_conditions": pattern.trigger_conditions,
                "failure_type": pattern.failure_type,
                "time_to_failure": pattern.time_to_failure,
                "confidence": pattern.confidence,
                "historical_occurrences": pattern.historical_occurrences,
                "prevention_actions": pattern.prevention_actions
            }

        return {
            "patterns": patterns,
            "count": len(patterns),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting failure patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get failure patterns: {str(e)}")

@predictive_router.get("/health-history/{module}", summary="Get health history for module")
async def get_module_health_history(
    module: str,
    limit: int = Query(50, description="Maximum number of readings to return", ge=1, le=100)
):
    """
    Get recent health history for a module.

    Args:
        module: Module name
        limit: Maximum number of readings to return (1-100)

    Returns:
        List of recent health readings
    """
    try:
        engine = get_predictive_engine()

        if module not in engine.health_history:
            return {
                "module": module,
                "history": [],
                "count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        history = list(engine.health_history[module])[-limit:]

        history_data = []
        for reading in history:
            history_data.append({
                "timestamp": reading.timestamp.isoformat(),
                "health_score": reading.health_score,
                "cpu_usage": reading.cpu_usage,
                "memory_usage": reading.memory_usage,
                "response_time": reading.response_time,
                "error_rate": reading.error_rate
            })

        return {
            "module": module,
            "history": history_data,
            "count": len(history_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting health history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health history for {module}: {str(e)}")
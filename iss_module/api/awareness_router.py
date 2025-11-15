# awareness_router.py
# FastAPI router for Caleon Awareness Layer API
# Version 1.0.0

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from iss_module.csmm.awareness.self_model import get_self_model

router = APIRouter(prefix="/awareness", tags=["awareness"])
self_model = get_self_model()

@router.get("/identity")
async def get_identity() -> Dict[str, str]:
    """
    Get Caleon's identity statement.

    Returns:
        Identity statement
    """
    return {"identity": self_model.identity()}

@router.get("/summary")
async def get_summary() -> Dict[str, str]:
    """
    Get Caleon's system summary.

    Returns:
        System summary
    """
    return {"summary": self_model.system_summary()}

@router.get("/module/{name}")
async def get_module_status(name: str) -> Dict[str, Any]:
    """
    Get status of a specific module.

    Args:
        name: Module name

    Returns:
        Module status information
    """
    status = self_model.get_module_status(name)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Module '{name}' not found")
    return {"module": name, "status": status}

@router.get("/duties")
async def get_duties() -> Dict[str, Any]:
    """
    Get Caleon's prime and operational duties.

    Returns:
        Duties information
    """
    return {
        "prime_duties": self_model.PRIME_DUTIES,
        "operational_duties": self_model.OPERATIONAL_DUTIES
    }

@router.get("/abby")
async def get_abby_directive() -> Dict[str, Any]:
    """
    Get Abby directive information.

    Returns:
        Abby directive details
    """
    return self_model.ABBY_DIRECTIVE

@router.get("/founder")
async def get_founder() -> Dict[str, Any]:
    """
    Get founder information.

    Returns:
        Founder details
    """
    return self_model.FOUNDER

@router.get("/health")
async def get_health() -> Dict[str, Any]:
    """
    Get comprehensive health dashboard data.

    Returns:
        Full health and status information
    """
    return self_model.to_dashboard_dict()

@router.get("/purpose")
async def get_purpose() -> Dict[str, str]:
    """
    Get Caleon's purpose explanation.

    Returns:
        Purpose explanation
    """
    return {"purpose": self_model.explain_purpose()}

@router.get("/nervous-system")
async def get_nervous_system() -> Dict[str, str]:
    """
    Get nervous system explanation.

    Returns:
        Nervous system explanation
    """
    return {"nervous_system": self_model.explain_nervous_system()}

@router.get("/authority")
async def get_authority() -> Dict[str, str]:
    """
    Get authority structure explanation.

    Returns:
        Authority explanation
    """
    return {"authority": self_model.explain_authority()}

@router.get("/predict/status")
async def get_predictive_status() -> Dict[str, Any]:
    """
    Get predictive engine status and risk assessment - Phase 11-A2.

    Returns:
        Predictive engine status and risk data
    """
    try:
        from iss_module.csmm.predictive_engine import PredictiveEngine

        status = PredictiveEngine.get_status()

        return {
            "identity": self_model.identity(),
            "predictive_status": status,
            "risk_scores": PredictiveEngine.risk_scores,
            "trends": PredictiveEngine.health_trends,
            "prevention_history": PredictiveEngine.prevention_history[-10:],  # Last 10 events
            "mode": "11-A2_autonomous",
            "phase": "Autonomous Predictive Prevention"
        }
    except ImportError:
        return {
            "identity": self_model.identity(),
            "predictive_status": "initializing",
            "risk_scores": {},
            "trends": {},
            "prevention_history": [],
            "mode": "11-A2_pending",
            "phase": "Autonomous Predictive Prevention"
        }
    except Exception as e:
        return {
            "identity": self_model.identity(),
            "predictive_status": f"error: {str(e)}",
            "risk_scores": {},
            "trends": {},
            "prevention_history": [],
            "mode": "11-A2_error",
            "phase": "Autonomous Predictive Prevention"
        }
"""
CSMM FastAPI Service

Provides REST API endpoints for the Caleon Self-Maintenance Module.
Exposes diagnostic, repair, and learning capabilities as a microservice.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from iss_module.core.utils import get_stardate, current_timecodes
from iss_module.core.caleon_security_layer import CaleonSecurityLayer
from iss_module.csmm.core.csmm_engine import CSMMEngine
from iss_module.csmm.diagnostics.diagnostic_engine import DiagnosticEngine
from iss_module.csmm.repair.repair_engine import RepairEngine
from iss_module.csmm.learning.learning_engine import LearningEngine
from iss_module.csmm.models.csmm_models import (
    RepairAction,
    ComponentIssue,
    RepairStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DALS.CSMM.API")

# Global CSMM components
csmm_engine: Optional[CSMMEngine] = None
diagnostic_engine: Optional[DiagnosticEngine] = None
repair_engine: Optional[RepairEngine] = None
learning_engine: Optional[LearningEngine] = None
security_layer: CaleonSecurityLayer = CaleonSecurityLayer()

# Request/Response models
class HealthCheckResponse(BaseModel):
    status: str
    stardate: float
    timestamp: str
    version: str = "1.0.0"

class DiagnosticRequest(BaseModel):
    component: Optional[str] = None
    deep_scan: bool = False

class DiagnosticResponse(BaseModel):
    diagnostic_id: str
    status: str
    issues_found: int
    critical_issues: int
    started_at: str
    completed_at: Optional[str] = None

class RepairRequest(BaseModel):
    issue_id: str
    action_type: str
    priority: str = "normal"

class RepairResponse(BaseModel):
    repair_id: str
    status: str
    target_component: str
    action_type: str
    started_at: str

class LearningInsightsResponse(BaseModel):
    patterns_count: int
    insights_count: int
    rules_count: int
    generated_at: str
    stardate: float

class ComponentHealthResponse(BaseModel):
    component: str
    health_score: float
    risk_level: str
    factors: List[str]
    calculated_at: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global csmm_engine, diagnostic_engine, repair_engine, learning_engine

    # Startup
    logger.info("Starting CSMM FastAPI service", extra={"stardate": get_stardate()})

    try:
        # Initialize CSMM components
        csmm_engine = CSMMEngine()
        diagnostic_engine = DiagnosticEngine()
        repair_engine = RepairEngine()
        learning_engine = LearningEngine()

        # Start CSMM engine
        await csmm_engine.start()

        logger.info("CSMM components initialized successfully", extra={"stardate": get_stardate()})

    except Exception as e:
        logger.error(f"Failed to initialize CSMM components: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down CSMM FastAPI service", extra={"stardate": get_stardate()})

    if csmm_engine:
        await csmm_engine.stop()

# Create FastAPI app
app = FastAPI(
    title="Caleon Self-Maintenance Module (CSMM)",
    description="Autonomous system diagnosis, repair, and learning microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """CSMM service health check"""
    return HealthCheckResponse(
        status="healthy",
        stardate=get_stardate(),
        timestamp=current_timecodes()["iso_timestamp"]
    )

@app.get("/status")
async def get_csmm_status():
    """Get comprehensive CSMM status"""
    if not csmm_engine:
        raise HTTPException(status_code=503, detail="CSMM engine not initialized")

    status = await csmm_engine.get_status()

    # Add component statuses
    status["components"] = {
        "diagnostic_engine": "active" if diagnostic_engine else "inactive",
        "repair_engine": "active" if repair_engine else "inactive",
        "learning_engine": "active" if learning_engine else "inactive"
    }

    return status

@app.post("/diagnostics/run", response_model=DiagnosticResponse)
async def run_diagnostics(request: DiagnosticRequest, background_tasks: BackgroundTasks):
    """Run system diagnostics"""
    if not diagnostic_engine:
        raise HTTPException(status_code=503, detail="Diagnostic engine not available")

    try:
        # Validate security
        security_check = await security_layer.validate_reasoning_request(
            query=f"CSMM diagnostic request: {request.component or 'full_system'}",
            mode="sequential",
            ethical_check=True
        )

        if not security_check.get("approved", False):
            raise HTTPException(
                status_code=403,
                detail="Diagnostic request blocked by Caleon security"
            )

        # Run diagnostics in background
        diagnostic_result = await diagnostic_engine.run_diagnostics(
            target_component=request.component,
            deep_scan=request.deep_scan
        )

        # Convert to response format
        response = DiagnosticResponse(
            diagnostic_id=diagnostic_result.get("diagnostic_id", "unknown"),
            status=diagnostic_result.get("status", "unknown"),
            issues_found=len(diagnostic_result.get("issues", [])),
            critical_issues=len([
                issue for issue in diagnostic_result.get("issues", [])
                if issue.get("severity") == "critical"
            ]),
            started_at=diagnostic_result.get("started_at", ""),
            completed_at=diagnostic_result.get("completed_at")
        )

        # Trigger learning analysis in background if issues found
        if response.issues_found > 0 and learning_engine:
            background_tasks.add_task(
                learning_engine.analyze_diagnostic_results,
                diagnostic_result.get("issues", [])
            )

        return response

    except Exception as e:
        logger.error(f"Diagnostic request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/diagnostics/history")
async def get_diagnostic_history(limit: int = 20):
    """Get diagnostic history"""
    if not diagnostic_engine:
        raise HTTPException(status_code=503, detail="Diagnostic engine not available")

    try:
        history = await diagnostic_engine.get_diagnostic_history(limit)
        return {"diagnostics": history}

    except Exception as e:
        logger.error(f"Failed to get diagnostic history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repairs/execute", response_model=RepairResponse)
async def execute_repair(request: RepairRequest):
    """Execute a repair action"""
    if not repair_engine:
        raise HTTPException(status_code=503, detail="Repair engine not available")

    try:
        # Validate security
        security_check = await security_layer.validate_reasoning_request(
            query=f"CSMM repair request: {request.issue_id} - {request.action_type}",
            mode="sequential",
            ethical_check=True
        )

        if not security_check.get("approved", False):
            raise HTTPException(
                status_code=403,
                detail="Repair request blocked by Caleon security"
            )

        # Create repair action
        repair_action = RepairAction(
            id=f"repair_{get_stardate()}_{request.issue_id}",
            target_component=request.issue_id.split('_')[0] if '_' in request.issue_id else "unknown",
            action_type=request.action_type,
            priority=request.priority,
            status=RepairStatus.PENDING
        )

        # Execute repair
        success = await repair_engine.execute_repair(repair_action)

        if not success:
            raise HTTPException(
                status_code=500,
                detail=repair_action.error_message or "Repair execution failed"
            )

        # Trigger learning analysis
        if learning_engine:
            await learning_engine.analyze_repair_outcome(repair_action)

        return RepairResponse(
            repair_id=repair_action.id,
            status=repair_action.status.value,
            target_component=repair_action.target_component,
            action_type=repair_action.action_type,
            started_at=repair_action.started_at or ""
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Repair execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repairs/status/{repair_id}")
async def get_repair_status(repair_id: str):
    """Get repair status"""
    if not repair_engine:
        raise HTTPException(status_code=503, detail="Repair engine not available")

    try:
        status = await repair_engine.get_repair_status(repair_id)
        return status

    except Exception as e:
        logger.error(f"Failed to get repair status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/repairs/{repair_id}")
async def cancel_repair(repair_id: str):
    """Cancel a repair action"""
    if not repair_engine:
        raise HTTPException(status_code=503, detail="Repair engine not available")

    try:
        success = await repair_engine.cancel_repair(repair_id)
        if not success:
            raise HTTPException(status_code=404, detail="Repair not found or not active")

        return {"status": "cancelled", "repair_id": repair_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel repair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repairs/history")
async def get_repair_history(limit: int = 20):
    """Get repair history"""
    if not repair_engine:
        raise HTTPException(status_code=503, detail="Repair engine not available")

    try:
        history = await repair_engine.get_repair_history(limit)
        return {"repairs": [repair.dict() for repair in history]}

    except Exception as e:
        logger.error(f"Failed to get repair history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/insights", response_model=LearningInsightsResponse)
async def get_learning_insights(component: Optional[str] = None):
    """Get learning insights"""
    if not learning_engine:
        raise HTTPException(status_code=503, detail="Learning engine not available")

    try:
        insights = await learning_engine.get_learning_insights(component)

        return LearningInsightsResponse(
            patterns_count=len(insights.get("patterns", {})),
            insights_count=len(insights.get("predictive_insights", [])),
            rules_count=len(insights.get("diagnostic_rules", {})),
            generated_at=insights.get("generated_at", ""),
            stardate=insights.get("stardate", 0.0)
        )

    except Exception as e:
        logger.error(f"Failed to get learning insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/health/{component}", response_model=ComponentHealthResponse)
async def get_component_health(component: str):
    """Get component health score"""
    if not learning_engine:
        raise HTTPException(status_code=503, detail="Learning engine not available")

    try:
        health = await learning_engine.get_component_health_score(component)

        return ComponentHealthResponse(
            component=health["component"],
            health_score=health["health_score"],
            risk_level=health["risk_level"],
            factors=health["factors"],
            calculated_at=health["calculated_at"]
        )

    except Exception as e:
        logger.error(f"Failed to get component health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/predictions/{component}")
async def get_failure_predictions(component: str, days_ahead: int = 7):
    """Get failure predictions for a component"""
    if not learning_engine:
        raise HTTPException(status_code=503, detail="Learning engine not available")

    try:
        predictions = await learning_engine.predict_component_failures(component, days_ahead)
        return {"predictions": predictions}

    except Exception as e:
        logger.error(f"Failed to get failure predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/export")
async def export_learning_data():
    """Export learning data"""
    if not learning_engine:
        raise HTTPException(status_code=503, detail="Learning engine not available")

    try:
        # Validate security
        security_check = await security_layer.validate_reasoning_request(
            query="CSMM learning data export",
            mode="sequential",
            ethical_check=True
        )

        if not security_check.get("approved", False):
            raise HTTPException(
                status_code=403,
                detail="Learning data export blocked by Caleon security"
            )

        data = await learning_engine.export_learning_data()
        return data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export learning data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/import")
async def import_learning_data(data: Dict[str, Any]):
    """Import learning data"""
    if not learning_engine:
        raise HTTPException(status_code=503, detail="Learning engine not available")

    try:
        # Validate security
        security_check = await security_layer.validate_reasoning_request(
            query="CSMM learning data import",
            mode="sequential",
            ethical_check=True
        )

        if not security_check.get("approved", False):
            raise HTTPException(
                status_code=403,
                detail="Learning data import blocked by Caleon security"
            )

        success = await learning_engine.import_learning_data(data)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid learning data format")

        return {"status": "imported", "message": "Learning data imported successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import learning data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate")
async def integrate_with_dals_system():
    """Integrate CSMM with the full DALS system"""
    if not csmm_engine:
        raise HTTPException(status_code=503, detail="CSMM engine not available")

    try:
        # Validate security
        security_check = await security_layer.validate_reasoning_request(
            query="CSMM system integration request",
            mode="sequential",
            ethical_check=True
        )

        if not security_check.get("approved", False):
            raise HTTPException(
                status_code=403,
                detail="System integration blocked by Caleon security"
            )

        success = await csmm_engine.integrate_with_dals_system()

        if not success:
            raise HTTPException(status_code=500, detail="System integration failed")

        return {"status": "integrated", "message": "CSMM successfully integrated with DALS system"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System integration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/issues/active")
async def get_active_issues():
    """Get currently active system issues"""
    if not diagnostic_engine:
        raise HTTPException(status_code=503, detail="Diagnostic engine not available")

    try:
        issues = await diagnostic_engine.get_active_issues()
        return {"issues": issues}

    except Exception as e:
        logger.error(f"Failed to get active issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/issues/critical")
async def get_critical_issues():
    """Get critical system issues requiring immediate attention"""
    if not diagnostic_engine:
        raise HTTPException(status_code=503, detail="Diagnostic engine not available")

    try:
        issues = await diagnostic_engine.get_critical_issues()
        return {"critical_issues": issues}

    except Exception as e:
        logger.error(f"Failed to get critical issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI server
    uvicorn.run(
        "csmm_api:app",
        host="0.0.0.0",
        port=8009,  # CSMM service port
        reload=True,
        log_level="info"
    )
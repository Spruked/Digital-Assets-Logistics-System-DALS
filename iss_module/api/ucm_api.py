"""
UCM Integration API
===================
API endpoints for Unified Cognition Module integration with DALS

These endpoints allow UCM to manage DALS operations while
CALEON security layer validates all commands.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from ..integrations.ucm_connector import get_ucm_connector, UCMConnector
from ..core.caleon_security_layer import CaleonSecurityLayer


logger = logging.getLogger("DALS.UCM.API")

# Initialize router
ucm_router = APIRouter(prefix="/api/ucm", tags=["UCM Integration"])

# Initialize security layer (shared with CALEON)
security_layer = CaleonSecurityLayer()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class UCMQueryRequest(BaseModel):
    """UCM cognitive query request"""
    content: str
    priority: str = "normal"
    metadata: Optional[Dict[str, Any]] = None


class UCMCommandRequest(BaseModel):
    """UCM command execution request"""
    command: str
    parameters: Dict[str, Any]
    ucm_session_id: str


class UCMConnectionRequest(BaseModel):
    """UCM connection initialization"""
    ucm_host: str = "localhost"
    ucm_port: int = 8080


# ==========================================
# CONNECTION MANAGEMENT
# ==========================================

@ucm_router.post("/connect")
async def connect_ucm(request: UCMConnectionRequest):
    """
    Establish connection to UCM
    
    Initializes the bridge between DALS and Caleon Prime (UCM).
    UCM becomes the cognitive manager with CALEON as security gateway.
    """
    try:
        connector = get_ucm_connector(
            ucm_host=request.ucm_host,
            ucm_port=request.ucm_port
        )
        
        result = await connector.connect()
        
        if result.get("success"):
            # Register connection with CALEON security layer
            await security_layer.ucm_connect_request({
                "ucm_id": "caleon_prime",
                "api_key": "dals_integration",
                "signature": "ucm_caleon_bridge"
            })
            
            logger.info(f"UCM connected successfully: {request.ucm_host}:{request.ucm_port}")
            
            return {
                "success": True,
                "message": "UCM connected - Caleon Prime is now managing DALS",
                "connection": result,
                "security_gateway": "CALEON active"
            }
        else:
            raise HTTPException(
                status_code=503,
                detail=f"UCM connection failed: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"UCM connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ucm_router.get("/status")
async def get_ucm_status():
    """
    Get UCM connection status and metrics
    
    Returns health, performance metrics, and connection state
    """
    try:
        connector = get_ucm_connector()
        status = connector.get_status()
        
        # Add CALEON security metrics
        caleon_metrics = security_layer.get_performance_metrics()
        
        return {
            "ucm_status": status,
            "caleon_security": {
                "gateway_active": security_layer.ucm_state.connected,
                "commands_processed": caleon_metrics.get("total_commands", 0),
                "commands_blocked": caleon_metrics.get("blocked_commands", 0),
                "security_level": security_layer.security_level.value
            },
            "integration_health": "active" if status["connection_state"] == "connected" else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ucm_router.post("/disconnect")
async def disconnect_ucm():
    """Disconnect from UCM"""
    try:
        connector = get_ucm_connector()
        await connector.disconnect()
        
        logger.info("UCM disconnected")
        
        return {
            "success": True,
            "message": "UCM disconnected - DALS in standalone mode"
        }
        
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# COGNITIVE PROCESSING
# ==========================================

@ucm_router.post("/query")
async def submit_ucm_query(request: UCMQueryRequest):
    """
    Submit query to UCM for cognitive processing
    
    UCM (Caleon Prime) processes the query through its cognitive pipeline:
    - Synaptic Resonator
    - Anterior Helix
    - EchoStack (second-order reasoning)
    - EchoRipple (recursive verification)
    - GyroHarmonizer (ethical oversight)
    """
    try:
        connector = get_ucm_connector()
        
        # Submit to UCM
        result = await connector.submit_reasoning_request(
            content=request.content,
            priority=request.priority,
            metadata=request.metadata
        )
        
        if result.get("success"):
            # Log to CALEON security vault
            await security_layer._log_security_event(
                security_layer.ThreatType.UNAUTHORIZED_ACCESS,  # Using as general category
                security_layer.SecurityLevel.NORMAL,
                f"UCM query processed: {request.priority}",
                {
                    "content_length": len(request.content),
                    "priority": request.priority,
                    "response_time": result.get("response_time")
                }
            )
            
            return {
                "success": True,
                "ucm_response": result.get("result"),
                "processing_time": result.get("response_time"),
                "timestamp": result.get("timestamp")
            }
        else:
            raise HTTPException(
                status_code=503,
                detail=f"UCM processing failed: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ucm_router.post("/command")
async def execute_ucm_command(request: UCMCommandRequest):
    """
    Execute DALS command via UCM cognitive evaluation
    
    Flow:
    1. UCM evaluates command through cognitive pipeline
    2. CALEON validates command for security
    3. Command executes if both approve
    4. Founder override can bypass at any point
    """
    try:
        connector = get_ucm_connector()
        
        # Submit to UCM for cognitive evaluation
        ucm_result = await connector.execute_dals_command(
            command=request.command,
            parameters=request.parameters,
            ucm_authorization=request.ucm_session_id
        )
        
        if not ucm_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"UCM rejected command: {ucm_result.get('error')}"
            )
        
        # Route through CALEON security validation
        caleon_result = await security_layer.ucm_command_relay(
            session_id=request.ucm_session_id,
            command={
                "action": request.command,
                "parameters": request.parameters,
                "ucm_reasoning": ucm_result.get("ucm_reasoning")
            }
        )
        
        if caleon_result.get("success"):
            return {
                "success": True,
                "message": "Command executed successfully",
                "ucm_evaluation": ucm_result,
                "caleon_validation": caleon_result,
                "execution_result": caleon_result.get("result")
            }
        else:
            return {
                "success": False,
                "message": "CALEON security blocked command",
                "ucm_evaluation": ucm_result,
                "caleon_reason": caleon_result.get("error"),
                "security_alert": True
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# HEALTH & MONITORING
# ==========================================

class UCMReasoningRequest(BaseModel):
    """Sequential reasoning request for UCM"""
    query: str
    mode: str = "sequential"  # sequential, parallel, tree
    enable_ethical_check: bool = True
    enable_drift_detection: bool = True
    max_steps: int = 10
    context: Optional[Dict[str, Any]] = None


class UCMReasoningStep(BaseModel):
    """Individual reasoning step response"""
    step_number: int
    content: str
    step_type: str  # analysis, synthesis, evaluation, conclusion
    confidence: float
    ethical_score: Optional[float] = None
    drift_score: Optional[float] = None
    requires_review: bool = False
    metadata: Optional[Dict[str, Any]] = None


@ucm_router.post("/reason")
async def sequential_reasoning(request: UCMReasoningRequest):
    """
    Execute sequential reasoning through UCM cerebral cortex

    This endpoint streams reasoning steps as Server-Sent Events,
    allowing real-time visualization of the Chain of Thought process.
    """
    try:
        # Validate request through CALEON security layer
        security_validation = await security_layer.validate_reasoning_request(
            query=request.query,
            mode=request.mode,
            ethical_check=request.enable_ethical_check
        )

        if not security_validation["approved"]:
            raise HTTPException(
                status_code=403,
                detail=f"Reasoning request blocked: {security_validation['reason']}"
            )

        # Get UCM connector
        connector = get_ucm_connector()

        # Prepare reasoning context
        reasoning_context = {
            "query": request.query,
            "mode": request.mode,
            "ethical_check": request.enable_ethical_check,
            "drift_detection": request.enable_drift_detection,
            "max_steps": request.max_steps,
            "context": request.context or {},
            "security_validation": security_validation,
            "stardate": security_layer.get_stardate()
        }

        # Execute reasoning through UCM
        reasoning_result = await connector.execute_reasoning(reasoning_context)

        # Stream results as SSE
        from fastapi.responses import StreamingResponse
        import json
        import asyncio

        async def generate_reasoning_steps():
            """Generate reasoning steps as Server-Sent Events"""
            step_count = 0

            for step in reasoning_result.get("steps", []):
                if step_count >= request.max_steps:
                    break

                step_count += 1

                # Create step response
                step_response = UCMReasoningStep(
                    step_number=step_count,
                    content=step.get("content", ""),
                    step_type=step.get("type", "analysis"),
                    confidence=step.get("confidence", 0.8),
                    ethical_score=step.get("ethical_score"),
                    drift_score=step.get("drift_score"),
                    requires_review=step.get("requires_review", False),
                    metadata=step.get("metadata", {})
                )

                # Send as SSE
                event_data = {
                    "step": step_response.content,
                    "step_number": step_response.step_number,
                    "type": step_response.step_type,
                    "confidence": step_response.confidence,
                    "ethical_score": step_response.ethical_score,
                    "drift_score": step_response.drift_score,
                    "requires_review": step_response.requires_review,
                    "metadata": step_response.metadata
                }

                yield f"data: {json.dumps(event_data)}\n\n"

                # Small delay between steps for UI visualization
                await asyncio.sleep(0.5)

            # Send completion event
            completion_data = {
                "complete": True,
                "total_steps": step_count,
                "final_assessment": reasoning_result.get("final_assessment", {}),
                "processing_time_ms": reasoning_result.get("processing_time_ms", 0)
            }

            yield f"data: {json.dumps(completion_data)}\n\n"

        return StreamingResponse(
            generate_reasoning_steps(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except Exception as e:
        logger.error(f"Sequential reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reasoning execution failed: {str(e)}")


@ucm_router.get("/health")
async def ucm_integration_health():
    """UCM integration health check"""
    try:
        connector = get_ucm_connector()
        ucm_health = await connector.health_check()
        
        return {
            "status": "healthy" if ucm_health.get("status") == "healthy" else "degraded",
            "ucm_service": ucm_health,
            "caleon_gateway": security_layer.get_security_status(),
            "founder_authority": "retained",
            "timestamp": security_layer.get_stardate()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "ucm_service": "unavailable",
            "fallback_mode": "standalone"
        }

"""
Gyro-Cortical Harmonizer API
=============================
API endpoints for the Gyro-Cortical Harmonizer - Final Verdict Engine

The Harmonizer implements 5+1 combinatorial reasoning cycles with philosophical
guidance and convergence validation within ±3 standard deviations.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

from ..harmonizer.harmonizer import get_harmonizer, GyroCorticalHarmonizer, LogicPacket, LogicPacketType
from ..core.caleon_security_layer import CaleonSecurityLayer


logger = logging.getLogger("DALS.Harmonizer.API")

# Initialize router
harmonizer_router = APIRouter(prefix="/api/harmonizer", tags=["Gyro-Cortical Harmonizer"])

# Initialize security layer
security_layer = CaleonSecurityLayer()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class LogicPacketModel(BaseModel):
    """Logic packet from UCM modules"""
    packet_type: str = Field(..., description="Type of logic packet (helices, echo_stack, drift, vault, security)")
    content: Dict[str, Any] = Field(..., description="Packet content and data")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    source_module: str = Field(..., description="Source UCM module name")


class HarmonizerRequest(BaseModel):
    """Harmonizer reasoning request with 5 logic packets"""
    logic_packets: List[LogicPacketModel] = Field(..., min_items=5, max_items=5,
                                                   description="Exactly 5 logic packets required")
    context: Dict[str, Any] = Field(default_factory=dict, description="Request context and metadata")
    request_id: Optional[str] = Field(None, description="Unique request identifier")


class HarmonizerResponse(BaseModel):
    """Harmonizer verdict response"""
    verdict: Dict[str, Any] = Field(..., description="Final harmonized verdict")
    processing_time_ms: float = Field(..., description="Total processing time")
    convergence_cycles: int = Field(..., description="Number of cycles to convergence")
    philosophical_guide: Optional[str] = Field(None, description="Final philosophical guide used")
    stability_achieved: bool = Field(..., description="Whether convergence was achieved")
    security_gate: Dict[str, Any] = Field(..., description="Security validation result")
    timestamp: str = Field(..., description="Response timestamp (stardate)")


class HarmonizerStatus(BaseModel):
    """Harmonizer status response - DALS-001 compliant"""
    status: str = Field(..., description="Harmonizer status")
    active_cycles: int = Field(..., description="Number of active reasoning cycles")
    last_convergence: Optional[str] = Field(None, description="Last convergence timestamp")
    current_verdict_confidence: float = Field(default=0.0, description="Current verdict confidence")
    stability_threshold: float = Field(..., description="Stability threshold (±σ)")
    philosophical_guides_used: int = Field(..., description="Number of philosophical guides used")


# ==========================================
# API ENDPOINTS
# ==========================================

@harmonizer_router.post("/reason", response_model=HarmonizerResponse)
async def process_harmonizer_reasoning(
    request: HarmonizerRequest
) -> HarmonizerResponse:
    """
    Process reasoning request through Gyro-Cortical Harmonizer

    Runs 5+1 combinatorial reasoning cycles until convergence within ±3σ.
    Requires exactly 5 logic packets from UCM modules.

    Returns final harmonized verdict after convergence validation.
    """
    try:
        harmonizer = get_harmonizer()

        # Convert request models to internal logic packets
        logic_packets = []
        for packet_model in request.logic_packets:
            try:
                packet_type = LogicPacketType(packet_model.packet_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid packet type: {packet_model.packet_type}"
                )

            packet = LogicPacket(
                packet_type=packet_type,
                content=packet_model.content,
                confidence=packet_model.confidence,
                timestamp=request.context.get('timestamp', 'unknown'),
                source_module=packet_model.source_module
            )
            logic_packets.append(packet)

        # Add request ID to context
        context = request.context.copy()
        context['request_id'] = request.request_id or f"harmonizer_{request.context.get('timestamp', 'unknown')}"

        # Process through harmonizer
        result = await harmonizer.process_reasoning_request(logic_packets, context)

        # Convert to response model
        response = HarmonizerResponse(**result)

        logger.info(f"Harmonizer reasoning completed for request {request.request_id}")
        return response

    except ValueError as e:
        logger.error(f"Validation error in harmonizer request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Harmonizer processing error: {e}")
        raise HTTPException(status_code=500, detail="Harmonizer processing failed")


@harmonizer_router.get("/status", response_model=HarmonizerStatus)
async def get_harmonizer_status() -> HarmonizerStatus:
    """
    Get Gyro-Cortical Harmonizer status

    Returns current harmonizer state including active cycles,
    convergence status, and stability metrics.

    DALS-001 compliant - returns real data or zeros for inactive state.
    """
    try:
        harmonizer = get_harmonizer()
        status = await harmonizer.get_status()

        response = HarmonizerStatus(**status)
        return response

    except Exception as e:
        logger.error(f"Error getting harmonizer status: {e}")
        # DALS-001 compliant fallback
        return HarmonizerStatus(
            status="error",
            active_cycles=0,
            last_convergence=None,
            current_verdict_confidence=0.0,
            stability_threshold=3.0,
            philosophical_guides_used=0
        )


@harmonizer_router.post("/reset")
async def reset_harmonizer_state(
    confirmation: str = Body(..., description="Confirmation token for reset")
) -> Dict[str, str]:
    """
    Reset Gyro-Cortical Harmonizer state

    Clears all active cycles and convergence history.
    Requires confirmation token for security.

    Returns success confirmation.
    """
    if confirmation != "CONFIRM_HARMONIZER_RESET":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation token"
        )

    try:
        harmonizer = get_harmonizer()
        harmonizer.reset_state()

        logger.info("Harmonizer state reset completed")
        return {"status": "reset", "message": "Harmonizer state cleared successfully"}

    except Exception as e:
        logger.error(f"Error resetting harmonizer state: {e}")
        raise HTTPException(status_code=500, detail="Reset failed")


@harmonizer_router.get("/health")
async def harmonizer_health_check() -> Dict[str, Any]:
    """
    Harmonizer health check endpoint

    Returns basic health status for load balancer monitoring.
    """
    try:
        harmonizer = get_harmonizer()
        status = await harmonizer.get_status()

        return {
            "status": "healthy" if status["status"] == "active" else "inactive",
            "timestamp": status.get("last_convergence"),
            "service": "gyro_cortical_harmonizer"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "gyro_cortical_harmonizer"
        }


# ==========================================
# DEPENDENCY INJECTION
# ==========================================

async def get_harmonizer_dependency() -> GyroCorticalHarmonizer:
    """Dependency injection for harmonizer instance"""
    return get_harmonizer()


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def validate_logic_packet_completeness(packets: List[LogicPacketModel]) -> bool:
    """
    Validate that all required logic packet types are present

    Args:
        packets: List of logic packet models

    Returns:
        True if all required types present, False otherwise
    """
    required_types = {pt.value for pt in LogicPacketType}
    provided_types = {p.packet_type for p in packets}

    return required_types.issubset(provided_types)

# ==========================================
# CANS AUTONOMIC SYNC INTEGRATION
# ==========================================

# Import and include CANS compatibility router
try:
    from .cans_sync import router as cans_sync_router
    harmonizer_router.include_router(cans_sync_router, prefix="/sync", tags=["CANS Sync"])
    logger.info("CANS autonomic sync endpoints enabled for Gyro-Cortical Harmonizer")
except ImportError as e:
    logger.warning(f"CANS sync router not available: {e}")
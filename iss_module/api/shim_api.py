"""
SHiM v1.1 API Router for DALS
Advisory-Only Spherical Harmonic Integrity Module

Provides REST endpoints for SHiM advisory analysis.
All operations are advisory only with zero execution authority.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

# Import SHiM Advisor
try:
    import sys
    import os
    # Add the project root to path
    project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
    sys.path.insert(0, project_root)
    from dals.shim.v1_1.shim_advisor import DALSAdvisor, validate_shim_output
    SHIM_AVAILABLE = True
    shim_advisor = DALSAdvisor()
except ImportError as e:
    logging.warning(f"SHiM v1.1 not available: {e}")
    SHIM_AVAILABLE = False
    DALSAdvisor = None
    validate_shim_output = None

# Pydantic models for request/response
class SHIMAnalysisRequest(BaseModel):
    """Request model for SHiM analysis."""
    claim: str = Field(..., description="The asset claim to analyze")
    evidence: List[str] = Field(..., description="List of evidence types present")

    class Config:
        schema_extra = {
            "example": {
                "claim": "Ownership transfer: Alice → Bob",
                "evidence": ["alice_signature_valid", "bob_identity_verified", "asset_provenance_intact"]
            }
        }

class SHIMAnalysisResponse(BaseModel):
    """Response model for SHiM analysis."""
    shim_advisory: Dict[str, Any] = Field(..., description="SHiM advisory output")
    dals_final_decision: Optional[Any] = Field(None, description="Always null - human authority preserved")

    class Config:
        schema_extra = {
            "example": {
                "shim_advisory": {
                    "version": "shim_v1.1_spherical",
                    "timestamp": "2025-11-15T10:30:00Z",
                    "asset_id": "DAL-2025-11-ABC",
                    "claim": "Ownership transfer: Alice → Bob",
                    "shim_score": 0.87,
                    "verdict": "HIGH_SUPPORT",
                    "confidence_band": "NARROW",
                    "evidence_weighting": {
                        "alice_signature_valid": 0.96,
                        "bob_identity_verified": 0.98,
                        "asset_provenance_intact": 0.93
                    },
                    "explanation": [
                        "Strong harmonic overlap detected in: alice_signature_valid, bob_identity_verified",
                        "Dominant spherical harmonics: ℓ=2, m=1, ℓ=2, m=-1, ℓ=1, m=0",
                        "High coherence indicates strong evidence alignment",
                        "Provenance audit depth: 7 blocks analyzed"
                    ],
                    "risk_flags": [
                        {
                            "risk_type": "regulatory_gaps",
                            "severity": "MEDIUM",
                            "description": "Potential regulatory compliance gaps detected",
                            "recommendation": "Conduct regulatory compliance check and add required evidence"
                        }
                    ],
                    "advisory_mode": True,
                    "enforcement": "NONE",
                    "recommended_action": "Proceed to human review and multi-sig approval",
                    "audit_trace_id": "SHIM-ADV-2025-11-15-XYZ"
                },
                "dals_final_decision": None
            }
        }

# Create router
shim_router = APIRouter(
    prefix="/api/shim",
    tags=["SHiM v1.1 - Advisory"],
    responses={404: {"description": "SHiM not available"}}
)

@shim_router.post("/analyze", response_model=SHIMAnalysisResponse)
async def analyze_claim(request: SHIMAnalysisRequest):
    """
    Perform SHiM v1.1 advisory analysis of an asset claim.

    **IMPORTANT**: This endpoint provides ADVISORY ANALYSIS ONLY.
    - Zero execution authority
    - Human review required for all decisions
    - Final authority remains with human operators

    Returns hybrid verbose output with full audit trail.
    """
    if not SHIM_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="SHiM v1.1 advisory subsystem not available"
        )

    try:
        # Perform SHiM analysis
        result = shim_advisor.analyze(
            claim=request.claim,
            evidence=request.evidence
        )

        # Validate output against schema
        if validate_shim_output and not validate_shim_output(result):
            logging.error("SHiM output failed schema validation")
            raise HTTPException(
                status_code=500,
                detail="SHiM analysis produced invalid output"
            )

        return result

    except Exception as e:
        logging.error(f"SHiM analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"SHiM analysis failed: {str(e)}"
        )

@shim_router.get("/status")
async def shim_status():
    """Get SHiM v1.1 status and availability."""
    return {
        "shim_available": SHIM_AVAILABLE,
        "version": "shim_v1.1_spherical" if SHIM_AVAILABLE else None,
        "advisory_mode": True,
        "enforcement": "NONE",
        "human_authority": "PRESERVED",
        "description": "Spherical Harmonic Integrity Module - Advisory Only"
    }

@shim_router.get("/health")
async def shim_health():
    """Health check for SHiM v1.1 subsystem."""
    if not SHIM_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "SHiM v1.1 not loaded"
        }

    try:
        # Quick health check - analyze a test claim
        test_result = shim_advisor.analyze(
            claim="Health check claim",
            evidence=["test_evidence"]
        )

        # Validate the response
        if validate_shim_output and validate_shim_output(test_result):
            return {
                "status": "healthy",
                "version": "shim_v1.1_spherical",
                "advisory_mode": test_result["shim_advisory"]["advisory_mode"],
                "enforcement": test_result["shim_advisory"]["enforcement"],
                "last_check": test_result["shim_advisory"]["timestamp"]
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Schema validation failed"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }
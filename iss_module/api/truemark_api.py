"""
TrueMark Mint API Router - Enterprise Certificate Platform
FastAPI router for TrueMark enterprise operations in DALS

TrueMark Mint: Scale with Trust.
Enterprise bulk minting, compliance verification, license management.
7 enterprise endpoints with DALS-001 compliance.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator

from .truemark_connector import get_truemark_connector

logger = logging.getLogger("DALS.TrueMark.API")

# Pydantic models for request/response validation
class BulkMintRequest(BaseModel):
    """Request model for bulk certificate minting."""
    certificates: List[Dict[str, Any]] = Field(..., description="List of certificate data to mint")
    organization_id: str = Field(..., description="Enterprise organization identifier")
    compliance_level: str = Field("enterprise", description="Compliance level: enterprise, compliance, standard")

    @validator("certificates")
    def validate_certificates(cls, v):
        if not v:
            raise ValueError("At least one certificate required")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 certificates per bulk request")
        return v

class ComplianceVerificationRequest(BaseModel):
    """Request model for compliance verification."""
    certificate_ids: List[str] = Field(..., description="List of certificate IDs to verify")
    organization_id: str = Field(..., description="Enterprise organization identifier")

    @validator("certificate_ids")
    def validate_certificate_ids(cls, v):
        if not v:
            raise ValueError("At least one certificate ID required")
        if len(v) > 500:
            raise ValueError("Maximum 500 certificate IDs per request")
        return v

class InvoiceGenerationRequest(BaseModel):
    """Request model for invoice generation."""
    organization_id: str = Field(..., description="Enterprise organization identifier")
    billing_period: str = Field(..., description="Billing period (e.g., '2025-11', 'Q4-2025')")

# Response models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    truemark_available: bool
    service: str
    market: str
    capabilities: List[str]
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class BulkMintResponse(BaseModel):
    """Bulk mint response."""
    operation: str
    certificates_requested: int
    certificates_minted: int
    organization_id: str
    compliance_level: str
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class ComplianceResponse(BaseModel):
    """Compliance verification response."""
    operation: str
    certificates_checked: int
    compliant_count: int
    non_compliant_count: int
    compliance_score: int
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class LicenseValidationResponse(BaseModel):
    """License validation response."""
    operation: str
    license_valid: bool
    license_type: str
    users_allowed: int
    users_active: int
    expires_at: Optional[str]
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class AuditTrailResponse(BaseModel):
    """Audit trail response."""
    operation: str
    organization_id: str
    days_back: int
    total_events: int
    events: List[Dict[str, Any]]
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class ComplianceStatusResponse(BaseModel):
    """Compliance status response."""
    operation: str
    organization_id: str
    overall_score: int
    certificates_total: int
    certificates_compliant: int
    last_audit: Optional[str]
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class ActiveLicensesResponse(BaseModel):
    """Active licenses response."""
    operation: str
    total_licenses: int
    active_licenses: int
    expired_licenses: int
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

class InvoiceResponse(BaseModel):
    """Invoice generation response."""
    operation: str
    organization_id: str
    billing_period: str
    total_amount: float
    certificates_minted: int
    invoice_url: Optional[str]
    timestamp_iso: str
    timestamp_stardate: float
    timestamp_julian: float
    timestamp_epoch: int

# Create router
truemark_router = APIRouter(
    prefix="/api/truemark",
    tags=["TrueMark Mint Enterprise"],
    responses={404: {"description": "TrueMark endpoint not found"}}
)

@truemark_router.get("/health", response_model=HealthResponse)
async def truemark_health():
    """
    Check TrueMark backend connectivity and status.
    DALS-001 compliant: Returns real data or zeros.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.health_check()
        return result
    except Exception as e:
        logger.error(f"TrueMark health check failed: {e}")
        raise HTTPException(status_code=503, detail="TrueMark service unavailable")

@truemark_router.post("/mint-bulk", response_model=BulkMintResponse)
async def truemark_bulk_mint(request: BulkMintRequest):
    """
    Bulk mint enterprise certificates.
    Supports up to 1000 certificates per request.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.mint_bulk_certificates(
            certificates=request.certificates,
            organization_id=request.organization_id,
            compliance_level=request.compliance_level
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Bulk mint failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark bulk mint failed: {e}")
        raise HTTPException(status_code=500, detail="Bulk mint operation failed")

@truemark_router.post("/verify", response_model=ComplianceResponse)
async def truemark_verify_compliance(request: ComplianceVerificationRequest):
    """
    Verify compliance status for enterprise certificates.
    Supports up to 500 certificate IDs per request.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.verify_compliance(
            certificate_ids=request.certificate_ids,
            organization_id=request.organization_id
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Compliance verification failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark compliance verification failed: {e}")
        raise HTTPException(status_code=500, detail="Compliance verification failed")

@truemark_router.get("/compliance/status", response_model=ComplianceStatusResponse)
async def truemark_compliance_status(organization_id: str = Query(..., description="Enterprise organization identifier")):
    """
    Get overall compliance status for enterprise organization.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.get_compliance_status(organization_id)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Compliance status check failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark compliance status failed: {e}")
        raise HTTPException(status_code=500, detail="Compliance status check failed")

@truemark_router.get("/licenses/active", response_model=ActiveLicensesResponse)
async def truemark_active_licenses():
    """
    Get count of active enterprise licenses across all organizations.
    DALS-001 compliant: Returns real license counts or zeros.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.get_active_licenses()

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "License check failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark active licenses check failed: {e}")
        raise HTTPException(status_code=500, detail="License check failed")

@truemark_router.get("/licenses/validate", response_model=LicenseValidationResponse)
async def truemark_validate_license(
    license_key: str = Query(..., description="License key to validate"),
    organization_id: str = Query(..., description="Enterprise organization identifier")
):
    """
    Validate enterprise license status and details.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.validate_license(license_key, organization_id)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "License validation failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark license validation failed: {e}")
        raise HTTPException(status_code=500, detail="License validation failed")

@truemark_router.get("/audit/trail", response_model=AuditTrailResponse)
async def truemark_audit_trail(
    organization_id: str = Query(..., description="Enterprise organization identifier"),
    days_back: int = Query(30, description="Number of days to look back", ge=1, le=365)
):
    """
    Get enterprise audit trail for compliance reporting.
    Returns up to 30 days of audit events.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.get_audit_trail(organization_id, days_back)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Audit trail retrieval failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark audit trail failed: {e}")
        raise HTTPException(status_code=500, detail="Audit trail retrieval failed")

@truemark_router.post("/invoice/generate", response_model=InvoiceResponse)
async def truemark_generate_invoice(request: InvoiceGenerationRequest):
    """
    Generate enterprise invoice for billing period.
    """
    try:
        connector = get_truemark_connector()
        result = await connector.generate_invoice(
            organization_id=request.organization_id,
            billing_period=request.billing_period
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Invoice generation failed"))

        return result
    except Exception as e:
        logger.error(f"TrueMark invoice generation failed: {e}")
        raise HTTPException(status_code=500, detail="Invoice generation failed")
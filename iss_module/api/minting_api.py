#!/usr/bin/env python3
"""
Minting API Router
Alpha CertSig and TrueMark minting endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..core.caleon_security_layer import CaleonSecurityLayer
from ..minting import (
    mint_alpha_certificate,
    verify_alpha_certificate,
    mint_truemark_asset,
    verify_truemark_asset,
    start_live_mint_session
)

logger = logging.getLogger("DALS.MintingAPI")
security = CaleonSecurityLayer()

# Pydantic models
class MintRequest(BaseModel):
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class VerifyRequest(BaseModel):
    id: str

class LiveMintRequest(BaseModel):
    session_data: Dict[str, Any]

# Router
minting_router = APIRouter(prefix="/api/minting", tags=["Minting"])

# Alpha CertSig endpoints
@minting_router.post("/alpha-certsig/mint", summary="Mint Alpha CertSig Certificate")
async def api_mint_alpha_certificate(request: MintRequest):
    """Mint an Alpha CertSig Elite certificate"""
    try:
        result = await mint_alpha_certificate(request.data)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Alpha CertSig mint failed: {e}")
        raise HTTPException(status_code=500, detail="Minting failed")

@minting_router.get("/alpha-certsig/verify/{cert_id}", summary="Verify Alpha CertSig Certificate")
async def api_verify_alpha_certificate(cert_id: str):
    """Verify an Alpha CertSig certificate"""
    try:
        result = await verify_alpha_certificate(cert_id)
        return result
    except Exception as e:
        logger.error(f"Alpha CertSig verify failed: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

# TrueMark endpoints
@minting_router.post("/truemark/mint", summary="Mint TrueMark Asset")
async def api_mint_truemark_asset(request: MintRequest):
    """Mint a TrueMark asset token"""
    try:
        result = await mint_truemark_asset(request.data)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"TrueMark mint failed: {e}")
        raise HTTPException(status_code=500, detail="Minting failed")

@minting_router.get("/truemark/verify/{asset_id}", summary="Verify TrueMark Asset")
async def api_verify_truemark_asset(asset_id: str):
    """Verify a TrueMark asset"""
    try:
        result = await verify_truemark_asset(asset_id)
        return result
    except Exception as e:
        logger.error(f"TrueMark verify failed: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

@minting_router.post("/truemark/live-session", summary="Start Live Minting Session")
async def api_start_live_mint_session(request: LiveMintRequest):
    """Start a live minting session"""
    try:
        result = await start_live_mint_session(request.session_data)
        return result
    except Exception as e:
        logger.error(f"Live mint session failed: {e}")
        raise HTTPException(status_code=500, detail="Session creation failed")
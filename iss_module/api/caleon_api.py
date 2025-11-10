"""
CALEON Security Layer API Endpoints
===================================
API routes for UCM connection and security monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Header
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from ..core.caleon_security_layer import CaleonSecurityLayer, ThreatType, SecurityLevel


logger = logging.getLogger("DALS.CALEON.API")

# Initialize security layer
security_layer = CaleonSecurityLayer()

# Create router
caleon_router = APIRouter(prefix="/api/caleon", tags=["CALEON Security"])


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class UCMConnectionRequest(BaseModel):
    """UCM connection credentials"""
    ucm_id: str
    api_key: str
    signature: str


class UCMCommandRequest(BaseModel):
    """UCM command relay request"""
    session_id: str
    command: Dict[str, Any]


class FounderOverrideRequest(BaseModel):
    """Founder override authentication"""
    founder_id: str
    passphrase: str
    signature: str


class DriftCheckRequest(BaseModel):
    """Request to check philosophical drift"""
    decision: Dict[str, Any]


# ==========================================
# UCM CONNECTION ENDPOINTS
# ==========================================

@caleon_router.post("/ucm/connect")
async def ucm_connect(credentials: UCMConnectionRequest):
    """
    UCM Plugin Connection Gateway
    
    Authenticate and establish UCM connection through CALEON security layer
    """
    try:
        result = await security_layer.ucm_connect_request(credentials.dict())
        return result
    except Exception as e:
        logger.error(f"UCM connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.post("/ucm/handshake")
async def ucm_handshake(session_id: str = Body(..., embed=True)):
    """
    UCM periodic handshake
    
    Maintains UCM connection health and security status
    """
    try:
        result = await security_layer.ucm_handshake(session_id)
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Handshake error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.post("/ucm/command")
async def ucm_command_relay(request: UCMCommandRequest):
    """
    UCM Command Relay
    
    All UCM commands pass through CALEON for security validation
    """
    try:
        result = await security_layer.ucm_command_relay(
            request.session_id,
            request.command
        )
        
        if not result["success"]:
            if result.get("blocked"):
                raise HTTPException(
                    status_code=403,
                    detail=result.get("error", "Command blocked by security layer")
                )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Command relay error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# SECURITY MONITORING ENDPOINTS
# ==========================================

@caleon_router.get("/security/status")
async def get_security_status():
    """
    Get comprehensive security status
    
    Returns current security level, threats, and monitoring data
    """
    try:
        return security_layer.get_security_status()
    except Exception as e:
        logger.error(f"Security status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/security/report")
async def get_security_report():
    """
    Generate comprehensive security report
    
    Includes recent events, performance metrics, and recommendations
    """
    try:
        return await security_layer.get_security_report()
    except Exception as e:
        logger.error(f"Security report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/security/performance")
async def get_performance_metrics():
    """Get UCM performance metrics"""
    try:
        return security_layer.get_performance_metrics()
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# DRIFT MONITOR ENDPOINTS
# ==========================================

@caleon_router.post("/drift/check")
async def check_philosophical_drift(request: DriftCheckRequest):
    """
    Check UCM decision for philosophical drift
    
    Analyzes alignment with Kant, Locke, and symbolic logic
    """
    try:
        result = await security_layer.check_philosophical_drift(request.decision)
        return result
    except Exception as e:
        logger.error(f"Drift check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/drift/metrics")
async def get_drift_metrics():
    """Get current drift monitoring metrics"""
    try:
        from dataclasses import asdict
        return asdict(security_layer.drift_metrics)
    except Exception as e:
        logger.error(f"Drift metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# TAMPER SEAL ENDPOINTS
# ==========================================

@caleon_router.post("/tamper/snapshot")
async def create_tamper_snapshot():
    """
    Create system integrity snapshot
    
    Captures cryptographic hashes for tamper detection
    """
    try:
        from dataclasses import asdict
        snapshot = await security_layer.create_tamper_seal_snapshot()
        return asdict(snapshot)
    except Exception as e:
        logger.error(f"Snapshot creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.post("/tamper/verify")
async def verify_tamper_seal(snapshot_id: Optional[str] = Body(None, embed=True)):
    """
    Verify system integrity against snapshot
    
    Detects any tampering with logs, memory, ports, or configurations
    """
    try:
        result = await security_layer.verify_tamper_seal(snapshot_id)
        return result
    except Exception as e:
        logger.error(f"Tamper verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# HONEYPOT ENDPOINTS
# ==========================================

@caleon_router.post("/honeypot/activate")
async def activate_honeypot(reason: str = Body(..., embed=True)):
    """
    Activate honeypot mode
    
    Deploys intrusion traps when attack suspected
    """
    try:
        await security_layer.activate_honeypot(reason)
        return {
            "success": True,
            "message": "Honeypot mode activated",
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Honeypot activation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/honeypot/report")
async def get_honeypot_report():
    """
    Get honeypot forensic report
    
    Returns attacker behavior data and analysis
    """
    try:
        return security_layer.get_honeypot_report()
    except Exception as e:
        logger.error(f"Honeypot report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.post("/honeypot/trigger")
async def log_honeypot_trigger(
    endpoint: str = Body(...),
    request_data: Dict[str, Any] = Body(...)
):
    """
    Log honeypot endpoint access (internal use)
    
    Called when attacker accesses honeypot trap
    """
    try:
        await security_layer.log_honeypot_trigger(endpoint, request_data)
        return {
            "logged": True,
            "alert_level": "critical"
        }
    except Exception as e:
        logger.error(f"Honeypot trigger logging error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# FOUNDER OVERRIDE ENDPOINTS
# ==========================================

@caleon_router.post("/founder/override/activate")
async def activate_founder_override(credentials: FounderOverrideRequest):
    """
    Activate Founder Override
    
    Emergency control bypass - UCM suspended
    Requires Founder authentication
    """
    try:
        result = await security_layer.founder_override_authenticate(credentials.dict())
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Founder override error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.post("/founder/override/deactivate")
async def deactivate_founder_override(session_token: str = Body(..., embed=True)):
    """
    Deactivate Founder Override
    
    Resume normal UCM operations
    """
    try:
        result = await security_layer.founder_override_deactivate(session_token)
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result.get("error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Founder deactivation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/founder/override/status")
async def get_founder_override_status():
    """Check if Founder override is active"""
    try:
        return {
            "override_active": security_layer.founder_override_active,
            "ucm_suspended": security_layer.founder_override_active
        }
    except Exception as e:
        logger.error(f"Override status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# HONEYPOT TRAP ENDPOINTS (Fake/Decoy)
# ==========================================
# These are intentional traps that log access attempts

@caleon_router.get("/admin/backdoor")
async def honeypot_backdoor():
    """Honeypot trap endpoint"""
    await security_layer.log_honeypot_trigger("/admin/backdoor", {"method": "GET"})
    raise HTTPException(status_code=404, detail="Not found")


@caleon_router.post("/debug/exec")
async def honeypot_exec(command: str = Body(..., embed=True)):
    """Honeypot trap endpoint"""
    await security_layer.log_honeypot_trigger("/debug/exec", {"command": command})
    raise HTTPException(status_code=403, detail="Forbidden")


@caleon_router.get("/auth/bypass")
async def honeypot_auth_bypass():
    """Honeypot trap endpoint"""
    await security_layer.log_honeypot_trigger("/auth/bypass", {"method": "GET"})
    raise HTTPException(status_code=404, detail="Not found")


# ==========================================
# STATUS ENDPOINTS FOR DASHBOARD
# ==========================================

@caleon_router.get("/ucm/status")
async def get_ucm_status():
    """Get UCM connection and performance status - DALS-001 compliant"""
    try:
        metrics = security_layer.get_performance_metrics()
        return {
            "status": "connected" if security_layer.ucm_session_id else "disconnected",
            "connection_time": security_layer.ucm_connection_time,  # None if not connected
            "commands_processed": metrics.get("total_commands", 0),
            "commands_blocked": metrics.get("blocked_commands", 0),
            "avg_response_time": metrics.get("avg_response_time", 0.0),
            "last_handshake": security_layer.ucm_last_handshake  # None if never connected
        }
    except Exception as e:
        logger.error(f"UCM status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/threats/status")
async def get_threats_status():
    """Get current threat monitoring status - DALS-001 compliant"""
    try:
        behavior_metrics = security_layer.get_behavior_metrics()
        
        # Get recent threats with real data only
        recent_threats = []
        for event in list(security_layer.active_threats)[:5]:
            recent_threats.append({
                "description": event.description,
                "threat_type": event.threat_type.value,
                "severity": event.severity.value,
                "timestamp": datetime.fromtimestamp(event.timestamp).isoformat()
            })
        
        return {
            "security_level": security_layer.security_level.value,
            "malevolence_score": behavior_metrics.get("malevolence_score", 0.0),
            "active_threats": len(security_layer.active_threats),
            "intrusion_attempts": security_layer.intrusion_attempt_count,
            "honeypot_active": security_layer.honeypot_active,
            "attacker_sessions": len(security_layer.honeypot_log),
            "recent_threats": recent_threats  # Empty list if no threats
        }
    except Exception as e:
        logger.error(f"Threats status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/drift/status")
async def get_drift_status():
    """Get philosophical drift alignment status - DALS-001 compliant"""
    try:
        drift_data = security_layer.get_drift_data()
        return {
            "kant_alignment": drift_data.get("kant_alignment", 100.0),
            "locke_alignment": drift_data.get("locke_alignment", 100.0),
            "logic_alignment": drift_data.get("logic_alignment", 100.0),
            "drift_detected": drift_data.get("drift_detected", False),
            "last_check": drift_data.get("last_check")  # None if never checked
        }
    except Exception as e:
        logger.error(f"Drift status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/tamper/status")
async def get_tamper_status():
    """Get tamper seal and integrity status - DALS-001 compliant"""
    try:
        tamper_data = security_layer.get_tamper_data()
        return {
            "last_snapshot": tamper_data.get("last_snapshot"),  # None if no snapshots
            "integrity_status": "INTACT" if tamper_data.get("integrity_intact", True) else "COMPROMISED",
            "memory_hash": tamper_data.get("memory_hash", ""),
            "log_hash": tamper_data.get("log_hash", ""),
            "config_hash": tamper_data.get("config_hash", ""),
            "tamper_alerts": tamper_data.get("tamper_alerts", 0),
            "tamper_detected": tamper_data.get("tamper_detected", False)
        }
    except Exception as e:
        logger.error(f"Tamper status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/vault/status")
async def get_vault_status():
    """Get signed vault status - DALS-001 compliant"""
    try:
        vault_data = security_layer.get_vault_data()
        total = vault_data.get("total_entries", 0)
        return {
            "vault_status": "SECURED" if total > 0 else "EMPTY",
            "total_entries": total,
            "verification_status": "VERIFIED" if vault_data.get("chain_valid", True) else "FAILED",
            "last_entry": vault_data.get("last_entry"),  # None if no entries
            "chain_integrity": vault_data.get("chain_integrity", 0.0),  # 0.0 if empty
            "failed_verifications": vault_data.get("failed_verifications", 0)
        }
    except Exception as e:
        logger.error(f"Vault status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@caleon_router.get("/founder/override/status")
async def get_founder_override_status_detailed():
    """Get detailed founder override status - DALS-001 compliant"""
    try:
        return {
            "override_active": security_layer.founder_override_active,
            "active_since": security_layer.founder_override_time,  # None if not active
            "override_level": "FULL CONTROL" if security_layer.founder_override_active else "None",
            "ucm_suspended": security_layer.founder_override_active
        }
    except Exception as e:
        logger.error(f"Override status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

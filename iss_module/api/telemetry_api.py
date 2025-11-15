"""
DALS Phase 1 Telemetry Ingress API
Unified telemetry console for Alpha CertSig Mint Engine, Caleon AI Core, and ISS Module
"""

from fastapi import APIRouter, HTTPException, Header, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import json
import hashlib
import hmac
import time
import logging
from enum import Enum
import sys
import os

# Import seed reference for telemetry
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Unified-Cognition-Module-Caleon-Prime-full-System', 'reference_seed'))
from seed_loader import get_seed_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create telemetry router
telemetry_router = APIRouter(prefix="/api/v1", tags=["telemetry"])

# Data Models for Phase 1 Integration

class NFTType(str, Enum):
    """CertSig NFT Types"""
    K_NFT = "K-NFT"
    L_NFT = "L-NFT"
    M_NFT = "M-NFT"
    N_NFT = "N-NFT"
    O_NFT = "O-NFT"
    P_NFT = "P-NFT"
    Q_NFT = "Q-NFT"
    R_NFT = "R-NFT"
    S_NFT = "S-NFT"
    T_NFT = "T-NFT"
    U_NFT = "U-NFT"
    V_NFT = "V-NFT"
    X_NFT = "X-NFT"

class MintStatus(str, Enum):
    """CertSig Mint Status"""
    PENDING = "pending"
    MINTING = "minting"
    MINTED = "minted"
    FAILED = "failed"
    VALIDATED = "validated"

class HarmonizerVerdict(str, Enum):
    """Caleon AI Harmonizer Verdicts"""
    STABLE = "Stable"
    FLUCTUATING = "Fluctuating"
    DRIFT_DETECTED = "Drift_Detected"
    CALIBRATING = "Calibrating"
    ERROR_STATE = "Error_State"

# 4.1 CertSig Mint Telemetry Schema
class CertSigTelemetry(BaseModel):
    token_id: str = Field(..., description="Unique NFT token identifier")
    nft_type: NFTType = Field(..., description="CertSig NFT type classification")
    status: MintStatus = Field(..., description="Current mint status")
    timestamp_iso: str = Field(..., description="ISO 8601 timestamp")
    stardate_iss: str = Field(..., description="ISS Stardate at mint time")
    royalty_amount: float = Field(..., ge=0, description="Royalty amount in USD")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    mint_duration_ms: int = Field(..., ge=0, description="Mint duration in milliseconds")
    node: str = Field(..., description="Mint node identifier")
    metadata_layers: int = Field(default=20, description="Number of metadata layers")
    validation_score: float = Field(default=1.0, ge=0, le=1.0, description="Validation confidence score")

# 4.2 Caleon AI Telemetry Schema
class CaleonTelemetry(BaseModel):
    sequence_id: str = Field(..., description="Unique sequence identifier")
    drift_score: float = Field(..., ge=0, le=1.0, description="Current drift score")
    harmonizer_verdict: HarmonizerVerdict = Field(..., description="Harmonizer stability assessment")
    reasoning_cycles: int = Field(..., ge=0, description="Number of reasoning cycles completed")
    logs_processed: int = Field(..., ge=0, description="Total logs processed in session")
    memory_usage: float = Field(..., ge=0, le=1.0, description="Memory usage percentage")
    cpu_load: float = Field(..., ge=0, le=1.0, description="CPU load percentage")
    timestamp_iso: str = Field(..., description="ISO 8601 timestamp")
    symbolic_coherence: float = Field(default=0.947, ge=0, le=1.0, description="Symbolic reasoning coherence")
    axiom_validation_count: int = Field(default=0, ge=0, description="Axioms validated this cycle")

# 4.3 ISS Pulse Schema
class ISSPulse(BaseModel):
    timestamp_iso: str = Field(..., description="ISO 8601 timestamp")
    timestamp_julian: float = Field(..., description="Julian date timestamp")
    timestamp_epoch: int = Field(..., description="Unix epoch timestamp")
    stardate_iss: str = Field(..., description="ISS Stardate calculation")
    phase: str = Field(..., description="Current chronometer phase")
    signal_strength: float = Field(..., ge=0, le=1.0, description="Temporal signal strength")
    drift_correction: float = Field(default=0.0001, description="Applied drift correction")
    anchor_stability: float = Field(default=0.997, ge=0, le=1.0, description="Temporal anchor stability")

# Module Authentication Schema
class ModuleAuth(BaseModel):
    module_id: str
    signature: str
    timestamp: int

# In-memory telemetry storage for Phase 1 (Redis integration in Phase 2)
telemetry_cache = {
    "certsig": [],
    "caleon": [],
    "iss": []
}

# Module secret keys (in production, these would be in Vault)
MODULE_SECRETS = {
    "certsig-mint-engine": "certsig_secret_key_phase1",
    "caleon-ai-core": "caleon_secret_key_phase1", 
    "iss-module": "iss_secret_key_phase1"
}

def verify_module_signature(
    module_id: str,
    payload: str,
    signature: str,
    x_module_sig: Optional[str] = Header(None)
) -> bool:
    """Verify HMAC-SHA256 signature for module authentication"""
    try:
        if module_id not in MODULE_SECRETS:
            return False
        
        secret = MODULE_SECRETS[module_id].encode()
        expected_signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        
        # Check both header and body signature
        return (signature == expected_signature) or (x_module_sig == expected_signature)
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        return False

async def store_telemetry(module: str, data: Dict[Any, Any]):
    """Store telemetry data in cache with timestamp and broadcast to WebSocket clients"""
    try:
        # Add ingestion timestamp
        data["ingested_at"] = datetime.now(timezone.utc).isoformat()
        
        # Store in module-specific cache
        if module in telemetry_cache:
            telemetry_cache[module].append(data)
            
            # Keep only last 100 entries per module
            if len(telemetry_cache[module]) > 100:
                telemetry_cache[module] = telemetry_cache[module][-100:]
        
        # Broadcast to WebSocket clients
        try:
            from .ws_stream import broadcast_telemetry_update
            await broadcast_telemetry_update(module, data)
        except ImportError:
            pass  # WebSocket not available
        
        logger.info(f"Stored telemetry for {module}: {data.get('sequence_id', data.get('token_id', 'unknown'))}")
    except Exception as e:
        logger.error(f"Failed to store telemetry for {module}: {e}")

# 🔹 CertSig Mint Engine Telemetry Endpoint
@telemetry_router.post("/mint/telemetry")
async def receive_certsig_telemetry(
    telemetry: CertSigTelemetry,
    background_tasks: BackgroundTasks,
    x_module_sig: Optional[str] = Header(None)
):
    """
    Receive telemetry from Alpha CertSig Mint Engine
    
    Data includes: NFT mint events, royalty updates, validation status
    Frequency: Every mint + 30 sec heartbeat
    """
    try:
        # Convert to dict for signature verification
        payload_dict = telemetry.dict()
        payload_str = json.dumps(payload_dict, sort_keys=True)
        
        # Verify module signature (simplified for Phase 1)
        if not verify_module_signature("certsig-mint-engine", payload_str, "", x_module_sig):
            logger.warning("Invalid signature for CertSig telemetry")
            # In development, allow unsigned requests
        
        # Store telemetry data
        background_tasks.add_task(store_telemetry, "certsig", payload_dict)
        
        return {
            "status": "received",
            "token_id": telemetry.token_id,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "message": "CertSig telemetry processed successfully"
        }
        
    except Exception as e:
        logger.error(f"CertSig telemetry processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Telemetry processing error: {str(e)}")

# 🔹 Caleon AI Core Telemetry Endpoint  
@telemetry_router.post("/caleon/telemetry")
async def receive_caleon_telemetry(
    telemetry: CaleonTelemetry,
    background_tasks: BackgroundTasks,
    x_module_sig: Optional[str] = Header(None)
):
    """
    Receive telemetry from Caleon AI Core
    
    Data includes: Drift scores, reasoning cycles, harmonizer verdicts, Gepetto logs
    Frequency: 5-sec stream via WebSocket (REST for Phase 1)
    """
    try:
        # Convert to dict for processing
        payload_dict = telemetry.dict()
        payload_str = json.dumps(payload_dict, sort_keys=True)
        
        # Verify module signature (simplified for Phase 1)
        if not verify_module_signature("caleon-ai-core", payload_str, "", x_module_sig):
            logger.warning("Invalid signature for Caleon telemetry")
            # In development, allow unsigned requests
        
        # Store telemetry data
        background_tasks.add_task(store_telemetry, "caleon", payload_dict)
        
        return {
            "status": "received",
            "sequence_id": telemetry.sequence_id,
            "drift_score": telemetry.drift_score,
            "harmonizer_verdict": telemetry.harmonizer_verdict,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "message": "Caleon telemetry processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Caleon telemetry processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Telemetry processing error: {str(e)}")

# 🔹 ISS Module Pulse Endpoint
@telemetry_router.post("/iss/pulse")
async def receive_iss_pulse(
    pulse: ISSPulse,
    background_tasks: BackgroundTasks,
    x_module_sig: Optional[str] = Header(None)
):
    """
    Receive chronometric pulse from ISS Module
    
    Data includes: ISO/Julian/Epoch/Stardate sync pulses
    Frequency: 1 Hz pulse (default)
    """
    try:
        # Convert to dict for processing
        payload_dict = pulse.dict()
        payload_str = json.dumps(payload_dict, sort_keys=True)
        
        # Verify module signature (simplified for Phase 1)
        if not verify_module_signature("iss-module", payload_str, "", x_module_sig):
            logger.warning("Invalid signature for ISS pulse")
            # In development, allow unsigned requests
        
        # Store pulse data
        background_tasks.add_task(store_telemetry, "iss", payload_dict)
        
        return {
            "status": "received",
            "stardate_iss": pulse.stardate_iss,
            "signal_strength": pulse.signal_strength,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "message": "ISS pulse processed successfully"
        }
        
    except Exception as e:
        logger.error(f"ISS pulse processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pulse processing error: {str(e)}")

# 🔹 Unified Telemetry Status Endpoint
@telemetry_router.get("/telemetry/status")
async def get_telemetry_status():
    """
    Get comprehensive telemetry status for all modules
    
    Returns: Last packet timestamps, data counts, system health
    """
    try:
        # Get seed status
        seed_hash = get_seed_hash()
        seed_active = bool(seed_hash)
        
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modules": {},
            "system_health": "optimal",
            "total_packets": 0,
            "seed_active": seed_active,
            "seed_hash": seed_hash
        }
        
        for module, data_list in telemetry_cache.items():
            packet_count = len(data_list)
            last_packet = data_list[-1] if data_list else None
            
            status["modules"][module] = {
                "packet_count": packet_count,
                "last_packet_time": last_packet.get("timestamp_iso") if last_packet else None,
                "status": "active" if packet_count > 0 else "no_data",
                "data_rate": f"{packet_count}/hour" if packet_count > 0 else "0/hour"
            }
            
            status["total_packets"] += packet_count
        
        # Determine system health
        active_modules = sum(1 for module_data in status["modules"].values() if module_data["status"] == "active")
        if active_modules < 2:
            status["system_health"] = "degraded"
        elif active_modules < 1:
            status["system_health"] = "offline"
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

# 🔹 Recent Telemetry Data Endpoint
@telemetry_router.get("/telemetry/recent/{module}")
async def get_recent_telemetry(module: str, limit: int = 10):
    """
    Get recent telemetry data for specific module
    
    Args:
        module: Module name (certsig, caleon, iss)
        limit: Number of recent entries to return
    """
    try:
        if module not in telemetry_cache:
            raise HTTPException(status_code=404, detail=f"Module '{module}' not found")
        
        recent_data = telemetry_cache[module][-limit:] if telemetry_cache[module] else []
        
        return {
            "module": module,
            "data_count": len(recent_data),
            "entries": recent_data,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recent telemetry retrieval failed for {module}: {e}")
        raise HTTPException(status_code=500, detail=f"Data retrieval error: {str(e)}")

# 🔹 Heartbeat Monitor Endpoint
@telemetry_router.get("/telemetry/heartbeat")
async def check_telemetry_heartbeat():
    """
    Watchdog endpoint checking for stale telemetry data
    
    Alerts if >90s delay from any module
    """
    try:
        current_time = datetime.now(timezone.utc)
        alerts = []
        
        for module, data_list in telemetry_cache.items():
            if not data_list:
                alerts.append({
                    "module": module,
                    "alert": "no_data",
                    "message": f"No telemetry data received from {module}"
                })
                continue
            
            last_packet = data_list[-1]
            last_time_str = last_packet.get("timestamp_iso")
            
            if last_time_str:
                try:
                    last_time = datetime.fromisoformat(last_time_str.replace('Z', '+00:00'))
                    time_delta = (current_time - last_time).total_seconds()
                    
                    if time_delta > 90:  # >90 seconds delay
                        alerts.append({
                            "module": module,
                            "alert": "stale_data",
                            "delay_seconds": time_delta,
                            "message": f"{module} telemetry is {time_delta:.1f}s behind"
                        })
                except Exception as e:
                    alerts.append({
                        "module": module,
                        "alert": "parse_error",
                        "message": f"Could not parse timestamp for {module}: {e}"
                    })
        
        return {
            "timestamp": current_time.isoformat(),
            "status": "healthy" if not alerts else "alerts",
            "alerts": alerts,
            "alert_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Heartbeat check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Heartbeat check error: {str(e)}")

# 🔹 Telemetry Simulation Endpoint (for testing)
@telemetry_router.post("/telemetry/simulate")
async def simulate_telemetry_data(
    module: str,
    count: int = 5
):
    """
    Generate synthetic telemetry data for testing
    
    Args:
        module: Module to simulate (certsig, caleon, iss)
        count: Number of events to generate
    """
    try:
        if module not in ["certsig", "caleon", "iss"]:
            raise HTTPException(status_code=400, detail="Module must be 'certsig', 'caleon', or 'iss'")
        
        generated_events = []
        
        for i in range(count):
            timestamp = datetime.now(timezone.utc).isoformat()
            
            if module == "certsig":
                event = {
                    "token_id": f"ALPHA-{str(int(time.time())).zfill(6)}",
                    "nft_type": "K-NFT",
                    "status": "minted",
                    "timestamp_iso": timestamp,
                    "stardate_iss": f"-297238.{i}",
                    "royalty_amount": 12.75 + i,
                    "transaction_hash": f"0x{hashlib.md5(f'{timestamp}{i}'.encode()).hexdigest()}",
                    "mint_duration_ms": 800 + i * 10,
                    "node": f"mint-node-{i % 3 + 1:02d}",
                    "metadata_layers": 20,
                    "validation_score": 0.95 + (i * 0.01)
                }
            elif module == "caleon":
                event = {
                    "sequence_id": f"gepetto_{int(time.time())}_{i}",
                    "drift_score": 0.020 + (i * 0.005),
                    "harmonizer_verdict": "Stable",
                    "reasoning_cycles": 100 + i * 5,
                    "logs_processed": 1000 + i * 100,
                    "memory_usage": 0.6 + (i * 0.02),
                    "cpu_load": 0.2 + (i * 0.05),
                    "timestamp_iso": timestamp,
                    "symbolic_coherence": 0.94 + (i * 0.002),
                    "axiom_validation_count": i * 3
                }
            else:  # iss
                event = {
                    "timestamp_iso": timestamp,
                    "timestamp_julian": 2460954.521238 + i,
                    "timestamp_epoch": int(time.time()) + i,
                    "stardate_iss": f"-297238.{i}",
                    "phase": f"cycle-{33 + i}",
                    "signal_strength": 1.0 - (i * 0.01),
                    "drift_correction": 0.0001 + (i * 0.00001),
                    "anchor_stability": 0.997 - (i * 0.001)
                }
            
            # Store the simulated event
            await store_telemetry(module, event)
            generated_events.append(event)
        
        return {
            "status": "simulation_complete",
            "module": module,
            "events_generated": count,
            "events": generated_events,
            "timestamp": timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telemetry simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
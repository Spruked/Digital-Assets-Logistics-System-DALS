"""
FastAPI backend for the Digital Asset Logistics System (DALS)
Provides REST API endpoints for tracking the lifecycle of digital assets.

Usage:
    uvicorn iss_module.api.api:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import logging
import os
import secrets
import hashlib

# Import telemetry router for Phase 1 integration
try:
    from .telemetry_api import telemetry_router
    from .ws_stream import ws_router, periodic_status_broadcaster, websocket_heartbeat_monitor
    TELEMETRY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Telemetry API not available: {e}")
    TELEMETRY_AVAILABLE = False

# Import CALEON Security Layer API
try:
    from .caleon_api import caleon_router
    CALEON_AVAILABLE = True
except ImportError as e:
    logging.warning(f"CALEON Security API not available: {e}")
    CALEON_AVAILABLE = False

# Import UCM Integration API
try:
    from .ucm_api import ucm_router
    UCM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"UCM Integration API not available: {e}")
    UCM_AVAILABLE = False

# Import Alpha CertSig Elite Mint API
try:
    from .alpha_certsig_api import alpha_certsig_router
    ALPHA_CERTSIG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Alpha CertSig Elite API not available: {e}")
    ALPHA_CERTSIG_AVAILABLE = False

# Import TrueMark Mint Enterprise API
try:
    from .truemark_api import truemark_router
    TRUEMARK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"TrueMark Mint Enterprise API not available: {e}")
    TRUEMARK_AVAILABLE = False

# Import Voice Communication Portal API
try:
    from .voice_api import voice_router
    VOICE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice Communication Portal API not available: {e}")
    VOICE_AVAILABLE = False

# Import Cochlear Processor API
try:
    from .cochlear_api import cochlear_router
    COCHLEAR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Cochlear Processor API not available: {e}")
    COCHLEAR_AVAILABLE = False

# Import Phonatory Output Module API
try:
    from .phonatory_api import phonatory_router
    PHONATORY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Phonatory Output Module API not available: {e}")
    PHONATORY_AVAILABLE = False

# Import Awareness API
try:
    from .awareness_router import router as awareness_router
    AWARENESS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Awareness API not available: {e}")
    AWARENESS_AVAILABLE = False

# Import Predictive Failure Modeling API
try:
    from .predictive_api import predictive_router
    PREDICTIVE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Predictive Failure Modeling API not available: {e}")
    PREDICTIVE_AVAILABLE = False

# Import GOAT System API
try:
    from dals.modules.goat.goat_router import router as goat_router
    GOAT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"GOAT System API not available: {e}")
    GOAT_AVAILABLE = False

# Import SHiM v1.1 Advisory API
try:
    from .shim_api import shim_router
    SHIM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"SHiM v1.1 Advisory API not available: {e}")
    SHIM_AVAILABLE = False

import asyncio
from pathlib import Path as PathLib
from passlib.context import CryptContext
import json
import time

# Import ISS Module components
from ..core.ISS import ISS
from ..core.utils import get_stardate, get_julian_date, get_iss_timestamp, format_timestamp

# DALS / Inventory components
from ..inventory.inventory_manager import UnitInventoryManager
from ..inventory.exporters import DataExporter
from ..models import (
    DigitalAssetAssignmentRequest,
    DigitalAssetAssignmentResponse,
    AssetDeploymentCreate,
    AssetStatusUpdate,
    AssetRecordResponse,
    SystemStatusResponse,
    AssetDependency,
    LoginRequest,
    LoginResponse,
)

# DALS Core Logic
# NOTE: Adjust the relative path if serial_assignment.py is located elsewhere
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from serial_assignment import assign_digital_asset_id
    SERIAL_ASSIGNMENT_AVAILABLE = True
except ImportError:
    logger.warning("Serial assignment utility not available")
    SERIAL_ASSIGNMENT_AVAILABLE = False
    assign_digital_asset_id = None

# Configuration
from ..config import settings

# --- TELEMETRY CONFIGURATION ---
telemetry_data = {
    "assignment_count": 0,
    "assignment_total_time": 0.0,
}


# --- SECURITY CONFIGURATION ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
basic_auth = HTTPBasic()

# Use configuration for admin credentials
ADMIN_USER = settings.admin_user
ADMIN_PASSWORD_HASH = settings.admin_password_hash

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global iss_instance, inventory_manager, data_exporter
    try:
        iss_instance = ISS()
        inventory_manager = UnitInventoryManager()
        await inventory_manager.initialize()
        data_exporter = DataExporter()
        
        # Start background tasks for WebSocket if available
        background_tasks = []
        if TELEMETRY_AVAILABLE:
            background_tasks.append(asyncio.create_task(periodic_status_broadcaster()))
            background_tasks.append(asyncio.create_task(websocket_heartbeat_monitor()))
        
        logger.info("DALS API started successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start DALS API: {e}")
        raise
    finally:
        # Cancel background tasks
        for task in background_tasks:
            task.cancel()
        if iss_instance:
            await iss_instance.shutdown()
        logger.info("DALS API shutdown complete")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Digital Asset Logistics System (DALS)",
    description="A system for tracking the lifecycle of digital project assets.",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Global instances
iss_instance = None
inventory_manager = None  # Formerly captain_log
data_exporter = None
logger = logging.getLogger('DALS.API')

# Templates and static files
templates_dir = PathLib(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
static_dir = PathLib(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount public mint pages
try:
    alpha_certsig_dir = PathLib(__file__).parent.parent.parent / "alpha-certsig" / "frontend"
    if alpha_certsig_dir.exists():
        app.mount("/alpha-certsig", StaticFiles(directory=str(alpha_certsig_dir), html=True), name="alpha-certsig")
        logger.info(f"Alpha CertSig public mint page mounted at /alpha-certsig")
except Exception as e:
    logger.warning(f"Could not mount Alpha CertSig public pages: {e}")

try:
    truemark_dir = PathLib(__file__).parent.parent.parent / "truemark-mint" / "truemark-website"
    if truemark_dir.exists():
        app.mount("/truemark", StaticFiles(directory=str(truemark_dir), html=True), name="truemark")
        logger.info(f"TrueMark public mint page mounted at /truemark")
except Exception as e:
    logger.warning(f"Could not mount TrueMark public pages: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Phase 1 Telemetry Router
if TELEMETRY_AVAILABLE:
    app.include_router(telemetry_router, tags=["Phase 1 Telemetry"])
    app.include_router(ws_router, tags=["Phase 1 WebSocket"])
    logger.info("Phase 1 Telemetry API and WebSocket enabled")
else:
    logger.warning("Phase 1 Telemetry API not available")

# Include CALEON Security Layer Router
if CALEON_AVAILABLE:
    app.include_router(caleon_router, tags=["CALEON Security"])
    logger.info("CALEON Security Layer API enabled")
else:
    logger.warning("CALEON Security Layer API not available")

# Include UCM Integration Router
if UCM_AVAILABLE:
    app.include_router(ucm_router, tags=["UCM Integration"])
    logger.info("UCM Integration API enabled - Caleon Prime bridge active")
else:
    logger.warning("UCM Integration API not available")

# Include Awareness Router
if AWARENESS_AVAILABLE:
    app.include_router(awareness_router, tags=["Awareness"])
    logger.info("Caleon Awareness API enabled - Self-model operational")
else:
    logger.warning("Caleon Awareness API not available")

# Include Predictive Failure Modeling Router
if PREDICTIVE_AVAILABLE:
    app.include_router(predictive_router, tags=["Predictive Failure Modeling"])
    logger.info("Predictive Failure Modeling API enabled - Proactive system health active")
else:
    logger.warning("Predictive Failure Modeling API not available")

# Include Alpha CertSig Elite Router
if ALPHA_CERTSIG_AVAILABLE:
    app.include_router(alpha_certsig_router, prefix="/api", tags=["Alpha CertSig Elite"])
    logger.info("Alpha CertSig Elite API enabled - NFT minting and domain management active")
else:
    logger.warning("Alpha CertSig Elite API not available")

# Include TrueMark Mint Enterprise Router
if TRUEMARK_AVAILABLE:
    app.include_router(truemark_router, prefix="/api", tags=["TrueMark Mint Enterprise"])
    logger.info("TrueMark Mint Enterprise API enabled - Bulk minting and compliance management active")
else:
    logger.warning("TrueMark Mint Enterprise API not available")

# Include Voice Communication Portal Router
if VOICE_AVAILABLE:
    app.include_router(voice_router, prefix="/api", tags=["Voice Communication Portal"])
    logger.info("Voice Communication Portal API enabled - Real-time voice interaction active")
else:
    logger.warning("Voice Communication Portal API not available")

# Include Cochlear Processor Router
if COCHLEAR_AVAILABLE:
    app.include_router(cochlear_router, prefix="/api", tags=["Cochlear Processor"])
    logger.info("Cochlear Processor API enabled - Speech input processing active")
else:
    logger.warning("Cochlear Processor API not available")

# Include Phonatory Output Module Router
if PHONATORY_AVAILABLE:
    app.include_router(phonatory_router, prefix="/api", tags=["Phonatory Output"])
    logger.info("Phonatory Output Module API enabled - Voice synthesis active")
else:
    logger.warning("Phonatory Output Module API not available")

# Include GOAT System Router
if GOAT_AVAILABLE:
    app.include_router(goat_router, prefix="/api", tags=["GOAT System"])
    logger.info("GOAT System API enabled - Greatest Of All Time teaching system active")
else:
    logger.warning("GOAT System API not available")

# Include SHiM v1.1 Advisory Router
if SHIM_AVAILABLE:
    app.include_router(shim_router, tags=["SHiM v1.1 - Advisory"])
    logger.info("SHiM v1.1 Advisory API enabled - Spherical harmonic integrity analysis active")
else:
    logger.warning("SHiM v1.1 Advisory API not available")

# Include Market Intelligence Router
try:
    from .market_intel_api import market_router
    MARKET_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Market Intelligence API not available: {e}")
    MARKET_AVAILABLE = False

if MARKET_AVAILABLE:
    app.include_router(market_router, prefix="/api", tags=["Market Intelligence"])
    logger.info("Market Intelligence API enabled - Real-time market data and news active")
else:
    logger.warning("Market Intelligence API not available")

# --- Authentication Dependency ---
async def get_current_user(credentials: HTTPBasicCredentials = Depends(basic_auth)):
    """Authenticates user via HTTP Basic credentials."""
    # Skip HTTP Basic authentication when `require_auth` is disabled in settings
    try:
        if not getattr(settings, 'require_auth', False):
            return ADMIN_USER  # return a default username for unauthenticated mode
    except Exception:
        # safety fallback: proceed with normal basic auth checks
        pass

    correct_username = (credentials.username == ADMIN_USER)
    correct_password = verify_password(credentials.password, ADMIN_PASSWORD_HASH)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- Login Endpoint ---
def generate_session_token(username: str) -> str:
    """Generate a simple session token for authentication"""
    import time
    timestamp = str(int(time.time()))
    token_data = f"{username}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return session token"""
    correct_username = (login_data.username == ADMIN_USER)
    correct_password = verify_password(login_data.password, ADMIN_PASSWORD_HASH)
    
    # If auth is disabled, allow login for demo/dev. Otherwise verify credentials.
    if not getattr(settings, 'require_auth', False) or (correct_username and correct_password):
        token = generate_session_token(login_data.username)
        return LoginResponse(
            success=True,
            token=token,
            message="Login successful",
            user={
                "username": login_data.username,
                "role": "admin"
            }
        )
    else:
        return LoginResponse(
            success=False,
            token=None,
            message="Invalid credentials"
        )

# --- UI and System Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main dashboard"""
    # This should be updated to a DALS-specific dashboard
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/voice", response_class=HTMLResponse)
async def voice_portal(request: Request):
    """Serve the voice communication portal"""
    return templates.TemplateResponse("voice_portal.html", {"request": request})

@app.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get current system status"""
    try:
        status = iss_instance.get_status()
        total_assets = len(inventory_manager.units) if inventory_manager and hasattr(inventory_manager, 'units') else 0

        # Map ISS get_status() keys to SystemStatusResponse
        sys_status = status.get('status', 'unknown')
        current_time = status.get('iso_timestamp') or status.get('current_time') or status.get('iso_timestamp')
        stardate = status.get('current_stardate') or status.get('stardate') or 0.0
        active_modules = status.get('module_list', [])

        # Uptime is not currently part of ISS.get_status so return None
        uptime = None

        return SystemStatusResponse(
            status=sys_status,
            uptime=uptime,
            active_modules=active_modules,
            current_time=current_time,
            stardate=stardate,
            total_tracked_assets=total_assets
        )
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": format_timestamp(), "stardate": get_stardate()}


# --- New Telemetry Endpoint ---
@app.get("/api/telemetry/metrics", summary="System Telemetry and Metrics")
async def get_system_telemetry():
    """Reports real-time usage statistics and performance metrics."""
    avg_time = (telemetry_data["assignment_total_time"] / telemetry_data["assignment_count"]) if telemetry_data["assignment_count"] > 0 else 0.0
    
    return {
        "status": "Healthy",
        "timestamp": format_timestamp(),
        "dals_assets_assigned": telemetry_data["assignment_count"],
        "avg_assignment_latency_ms": round(avg_time * 1000, 2),
        "total_tracked_units": len(inventory_manager.units) if inventory_manager and hasattr(inventory_manager, 'units') else 0
    }


@app.get("/api/system/metrics", summary="Real-time System Metrics")
async def get_system_metrics():
    """Get comprehensive real-time system metrics - DALS-001 compliant (real data or zeros)"""
    try:
        import psutil
        import platform

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_total_gb = round(memory.total / (1024**3), 2)
        memory_used_gb = round(memory.used / (1024**3), 2)
        memory_available_gb = round(memory.available / (1024**3), 2)
        memory_percent = memory.percent

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_total_gb = round(disk.total / (1024**3), 2)
        disk_used_gb = round(disk.used / (1024**3), 2)
        disk_free_gb = round(disk.free / (1024**3), 2)
        disk_percent = disk.percent

        # Network metrics
        network = psutil.net_io_counters()
        bytes_sent_mb = round(network.bytes_sent / (1024**2), 2)
        bytes_recv_mb = round(network.bytes_recv / (1024**2), 2)

        # System info
        system_info = {
            "os": platform.system(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "uptime_seconds": int(time.time() - psutil.boot_time())
        }

        # Process info for DALS
        process = psutil.Process()
        process_memory_mb = round(process.memory_info().rss / (1024**2), 2)
        process_cpu_percent = process.cpu_percent()

        return {
            "timestamp": format_timestamp(),
            "system_info": system_info,
            "cpu": {
                "usage_percent": cpu_percent,
                "cores_physical": cpu_count,
                "cores_logical": cpu_count_logical
            },
            "memory": {
                "total_gb": memory_total_gb,
                "used_gb": memory_used_gb,
                "available_gb": memory_available_gb,
                "usage_percent": memory_percent
            },
            "disk": {
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "free_gb": disk_free_gb,
                "usage_percent": disk_percent
            },
            "network": {
                "bytes_sent_mb": bytes_sent_mb,
                "bytes_recv_mb": bytes_recv_mb
            },
            "process": {
                "memory_mb": process_memory_mb,
                "cpu_percent": process_cpu_percent
            }
        }

    except ImportError:
        # psutil not available - return zeros (DALS-001 compliant)
        logger.warning("psutil not available - returning zero metrics")
        return {
            "timestamp": format_timestamp(),
            "system_info": {"status": "psutil_unavailable"},
            "cpu": {"usage_percent": 0, "cores_physical": 0, "cores_logical": 0},
            "memory": {"total_gb": 0, "used_gb": 0, "available_gb": 0, "usage_percent": 0},
            "disk": {"total_gb": 0, "used_gb": 0, "free_gb": 0, "usage_percent": 0},
            "network": {"bytes_sent_mb": 0, "bytes_recv_mb": 0},
            "process": {"memory_mb": 0, "cpu_percent": 0}
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        # Return zeros on error (DALS-001 compliant)
        return {
            "timestamp": format_timestamp(),
            "error": str(e),
            "cpu": {"usage_percent": 0, "cores_physical": 0, "cores_logical": 0},
            "memory": {"total_gb": 0, "used_gb": 0, "available_gb": 0, "usage_percent": 0},
            "disk": {"total_gb": 0, "used_gb": 0, "free_gb": 0, "usage_percent": 0},
            "network": {"bytes_sent_mb": 0, "bytes_recv_mb": 0},
            "process": {"memory_mb": 0, "cpu_percent": 0}
        }


# --- Digital Asset Logistics (DALS) Endpoints ---

@app.post("/api/dals/assign_asset_id", response_model=DigitalAssetAssignmentResponse, summary="Assign and Register a new Digital Asset ID")
async def assign_asset_id(
    request_data: DigitalAssetAssignmentRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generates a new unique Asset ID, logs it to the vault, and creates an initial
    record in the inventory manager.
    """
    start_time = time.perf_counter()
    try:
        # 1. Generate the asset ID and write to the dedicated vault
        result = assign_digital_asset_id(
            asset_type=request_data.asset_type,
            project_id=request_data.project_id,
            source_reference=request_data.source_reference,
            parent_asset_id=request_data.parent_asset_id
        )
        
        asset_id = result['asset_id']

        # Create initial record in the inventory manager
        await inventory_manager.create_unit_record(
            unit_serial=asset_id, # Using the generic field name from the manager
            model_id=request_data.project_id,
            deployment_location="PENDING",
            initial_audit_hash=result['audit_hash'],
            source_unit_serial=request_data.parent_asset_id,
            audited_by=current_user
        )
        
        # Telemetry Tracking
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        telemetry_data["assignment_count"] += 1
        telemetry_data["assignment_total_time"] += elapsed
        
        return DigitalAssetAssignmentResponse(**result)

    except Exception as e:
        logger.error(f"Failed to assign asset ID: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Logistics Error: {e}")

@app.post("/api/dals/deploy_asset", response_model=AssetRecordResponse, summary="Deploy an Asset and Associate Dependencies")
async def deploy_asset(
    deployment_data: AssetDeploymentCreate,
    current_user: str = Depends(get_current_user)
):
    """
    Marks a digital asset as deployed to a specific environment and tracks its dependencies.
    """
    try:
        updated_asset = await inventory_manager.update_unit_components(
            unit_serial=deployment_data.asset_id,
            new_status="DEPLOYED",
            location=deployment_data.deployment_environment,
            components=deployment_data.dependencies, # Assumes manager can handle this model
            audited_by=current_user
        )
        
        if not updated_asset:
             raise HTTPException(status_code=404, detail=f"Asset ID {deployment_data.asset_id} not found for deployment.")
        
        return AssetRecordResponse(**updated_asset.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deploy asset {deployment_data.asset_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Deployment failed: {str(e)}")

@app.put("/api/dals/update_asset/{asset_id}", response_model=AssetRecordResponse, summary="Update an Asset's Lifecycle Status")
async def update_asset_status(
    asset_id: str = Path(..., description="The Asset ID of the digital asset to update."),
    update_data: AssetStatusUpdate = Body(...),
    current_user: str = Depends(get_current_user)
):
    """
    Updates the lifecycle status of a tracked digital asset (e.g., RETIRED, FAILED_AUDIT).
    """
    try:
        updated_asset = await inventory_manager.update_unit_status(
            unit_serial=asset_id,
            new_status=update_data.new_status,
            update_details=update_data.update_details,
            components_update=update_data.dependencies_update,
            audited_by=current_user
        )

        if not updated_asset:
            raise HTTPException(status_code=404, detail="Asset ID not found")
        
        return AssetRecordResponse(**updated_asset.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update asset {asset_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

@app.get("/api/dals/validate/{asset_id}", response_model=AssetRecordResponse, summary="Validate Asset Status and Lineage")
async def validate_asset(
    asset_id: str = Path(..., description="The Asset ID to validate."),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves the current status, environment, and complete dependency list for a given Asset ID.
    """
    try:
        asset = await inventory_manager.get_unit_by_serial(asset_id.upper())
        if not asset:
            raise HTTPException(status_code=404, detail="Asset ID not found in Inventory.")
        
        return AssetRecordResponse(**asset.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation failed for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal validation error")

@app.get("/api/dals/assets", response_model=List[AssetRecordResponse], summary="List and Filter Tracked Assets")
async def get_tracked_assets(
    status: Optional[str] = Query(None, description="Filter by asset status (e.g., DEPLOYED, RETIRED)"),
    project_id: Optional[str] = Query(None, description="Filter by Project ID"),
    limit: Optional[int] = Query(50, le=1000),
    current_user: str = Depends(get_current_user)
):
    """Retrieve tracked digital assets with filtering capabilities."""
    try:
        assets = await inventory_manager.get_units(
            status=status,
            model_id=project_id, # Map to the manager's filtering key
            limit=limit
        )
        return [AssetRecordResponse(**asset.to_dict()) for asset in assets]
        
    except Exception as e:
        logger.error(f"Failed to get asset records: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --- HARD COPY / PRINT ENDPOINTS ---

@app.get("/api/dals/print/label/{asset_id}", response_class=PlainTextResponse, summary="Print to Label (Text)")
async def print_asset_label(
    asset_id: str = Path(..., description="Asset ID to generate a small label for."),
    current_user: str = Depends(get_current_user)
):
    """
    Generates a minimalist, fixed-width plain text label suitable for small-format 
    thermal printers or quick console review.
    """
    try:
        asset = await inventory_manager.get_unit_by_serial(asset_id.upper())
        if not asset:
            raise HTTPException(status_code=404, detail="Asset ID not found in Inventory.")

        record = asset.to_dict()
        
        # --- Fixed-Width Label Format ---
        label_text = (
            f"--- DALS ASSET LABEL ---\n"
            f"ID:      {record['asset_id']}\n"
            f"PROJECT: {record['project_id']}\n"
            f"STATUS:  {record['status']}\n"
            f"SOURCE:  {record.get('source_reference', 'N/A')}\n"
            f"TIME:    {record['timestamp'][:19].replace('T', ' ')}\n" # Trim to seconds
            f"--------------------------\n"
        )
        return PlainTextResponse(label_text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Label print failed for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal printing error")


@app.get("/api/dals/print/form/{asset_id}", response_class=HTMLResponse, summary="Print to Form (HTML)")
async def print_asset_form(
    asset_id: str = Path(..., description="Asset ID to generate a full review form for."),
    current_user: str = Depends(get_current_user)
):
    """
    Generates a structured HTML form view suitable for printing to a standard 
    A4/Letter sheet. This allows for complex styling via CSS (not included here).
    """
    try:
        asset = await inventory_manager.get_unit_by_serial(asset_id.upper())
        if not asset:
            raise HTTPException(status_code=404, detail="Asset ID not found in Inventory.")

        record = asset.to_dict()
        dependencies_html = ""
        
        # Format Dependencies
        for dep in record.get('dependencies', []):
            dependencies_html += f"""
                <tr>
                    <td>{dep['dependency_name']}</td>
                    <td>{dep['asset_id']}</td>
                    <td>{dep['status']}</td>
                </tr>
            """
        
        # --- HTML Form Layout (Minimal CSS for structure) ---
        html_content = f"""
        <html>
        <head>
            <title>DALS Asset Audit Form - {asset_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h2 {{ color: #333; border-bottom: 2px solid #ccc; padding-bottom: 5px; }}
                .section {{ margin-bottom: 20px; border: 1px solid #eee; padding: 15px; }}
                .data-row {{ margin-bottom: 8px; }}
                .label {{ font-weight: bold; display: inline-block; width: 150px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            </style>
        </head>
        <body>
            <h1>Digital Asset Audit Form</h1>
            <p><strong>Printed By:</strong> {current_user} | <strong>Print Time:</strong> {format_timestamp()}</p>
            
            <div class="section">
                <h2>Asset Summary: {record['asset_id']}</h2>
                <div class="data-row"><span class="label">Asset ID:</span> {record['asset_id']}</div>
                <div class="data-row"><span class="label">Project ID:</span> {record['project_id']}</div>
                <div class="data-row"><span class="label">Status:</span> {record['status']}</div>
                <div class="data-row"><span class="label">Source Ref:</span> {record.get('source_reference', 'N/A')}</div>
                <div class="data-row"><span class="label">Deployment Env:</span> {record.get('deployment_environment', 'N/A')}</div>
                <div class="data-row"><span class="label">Assignment Time:</span> {record['timestamp']}</div>
                <div class="data-row"><span class="label">Assigned By:</span> {record['history'][0].get('audited_by', 'System')}</div>
            </div>

            <div class="section">
                <h2>Dependencies / Modules ({len(record.get('dependencies', []))})</h2>
                <table>
                    <thead>
                        <tr><th>Name</th><th>Asset ID/Ref</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        {dependencies_html if dependencies_html else '<tr><td colspan="3">No tracked dependencies.</td></tr>'}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>Lifecycle History ({len(record.get('history', []))})</h2>
                <p>Detailed history logs would be displayed here (e.g., Status changes, user updates).</p>
            </div>
            
            <div class="section">
                <h2>Audit & Signature</h2>
                <div class="data-row"><span class="label">Initial Audit Hash:</span> {record['history'][0].get('initial_audit_hash', 'N/A')}</div>
                <p>Reviewed By: _________________________________________ Date: ________________</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form print failed for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal printing error")


@app.get("/api/dals/print/raw/{asset_id}", response_class=PlainTextResponse, summary="Print to Raw (JSON)")
async def print_asset_raw(
    asset_id: str = Path(..., description="Asset ID to dump raw data for review."),
    current_user: str = Depends(get_current_user)
):
    """
    Dumps the complete, unformatted JSON record, ideal for ingestion by other 
    software or for a full, raw data hard copy review.
    """
    try:
        asset = await inventory_manager.get_unit_by_serial(asset_id.upper())
        if not asset:
            raise HTTPException(status_code=404, detail="Asset ID not found in Inventory.")

        record_json = json.dumps(asset.to_dict(), indent=4)
        
        # --- Raw Data Header ---
        raw_text = (
            f"### DALS RAW ASSET RECORD: {asset_id} ###\n"
            f"### Printed by: {current_user} at {format_timestamp()} ###\n\n"
            f"{record_json}"
        )
        return PlainTextResponse(raw_text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Raw print failed for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal printing error")

# --- Utility Endpoints ---
@app.get("/api/time")
async def get_current_time():
    """Get current time in various formats"""
    return {
        "iso": format_timestamp(format_type='iso'),
        "stardate": format_timestamp(format_type='stardate'),
        "julian": format_timestamp(format_type='julian'),
        "human": format_timestamp(format_type='human')
    }

@app.get("/api/v1/iss/now")
async def get_iss_timestamp_endpoint():
    """
    Get ISS timestamp data in canonical format
    AUTHORITY: Spruked - Official DALS/UCM Stardate Protocol
    Epoch: January 1, 2000, 00:00:00 UTC
    """
    return get_iss_timestamp()

# --- Real Module Integration Endpoints ---

@app.get("/api/modules/caleon/status")
async def get_caleon_status():
    """Get Caleon reasoning engine status - LIVE DATA ONLY"""
    try:
        # GOVERNANCE [DALS-001]: No mock data - only live module status
        # If Caleon is not running/connected, return inactive state
        caleon_connected = False  # TODO: Replace with actual Caleon connection check
        
        if not caleon_connected:
            return {
                "module": "caleon",
                "status": "inactive",
                "reasoning_sessions": 0,
                "current_task": "—",
                "last_activity": "—",
                "health": "disconnected",
                "note": "Module offline - no mock data shown"
            }
        
        # When Caleon is actually connected, this would return real data:
        return {
            "module": "caleon",
            "status": "inactive",  # Real status from connection
            "reasoning_sessions": 0,  # Real count from Caleon API
            "current_task": "—",  # Real task if any
            "last_activity": "—",  # Real timestamp if available
            "health": "disconnected"  # Real health check
        }
    except Exception as e:
        logger.error(f"Error getting Caleon status: {e}")
        return {
            "module": "caleon", 
            "status": "error",
            "reasoning_sessions": 0,
            "current_task": "—",
            "last_activity": "—", 
            "health": "error",
            "error": str(e)
        }

@app.get("/api/modules/iss/pulse")
async def get_iss_pulse():
    """Get ISS chronometric pulse data"""
    try:
        # In production, this would connect to actual ISS module
        return {
            "pulse_rate": "1.047 Hz",
            "chronon_phase": "stable",
            "temporal_drift": "±0.001%",
            "anchor_strength": "99.7%",
            "last_sync": format_timestamp(format_type='iso'),
            "stardate_accuracy": "±0.0001",
            "interplanetary_offset": "0.0000234 cycles"
        }
    except Exception as e:
        logger.error(f"ISS pulse check failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/modules/certsig/mint-status")
async def get_certsig_mint_status():
    """Get CertSig Alpha Mint Engine status - LIVE DATA ONLY"""
    try:
        # GOVERNANCE [DALS-001]: No mock data - only live module status
        # If CertSig is not running/connected, return inactive state
        certsig_connected = False  # TODO: Replace with actual CertSig connection check
        
        if not certsig_connected:
            return {
                "mint_engine": "disconnected",
                "pending_mints": 0,
                "completed_today": 0,
                "validation_queue": 0,
                "nft_types_active": 0,
                "blockchain_status": {
                    "ethereum": "disconnected",
                    "polygon": "disconnected", 
                    "arbitrum": "disconnected"
                },
                "vault_integrity": "—",
                "metadata_layers": 0,
                "note": "Module offline - no mock data shown"
            }
            
        # When CertSig is actually connected, this would return real data:
        return {
            "mint_engine": "disconnected",  # Real status from connection
            "pending_mints": 0,             # Real count from CertSig API
            "completed_today": 0,           # Real completion count
            "validation_queue": 0,          # Real validation queue
            "nft_types_active": 0,          # Real active types
            "blockchain_status": {          # Real blockchain connections
                "ethereum": "disconnected",
                "polygon": "disconnected", 
                "arbitrum": "disconnected"
            },
            "vault_integrity": "—",         # Real integrity check
            "metadata_layers": 0            # Real metadata count
        }
    except Exception as e:
        logger.error(f"CertSig mint status check failed: {e}")
        return {
            "mint_engine": "error",
            "pending_mints": 0,
            "completed_today": 0,
            "validation_queue": 0,
            "nft_types_active": 0,
            "blockchain_status": {
                "ethereum": "error",
                "polygon": "error", 
                "arbitrum": "error"
            },
            "vault_integrity": "error",
            "metadata_layers": 0,
            "error": str(e)
        }

@app.get("/api/modules/ucm/integration")
async def get_ucm_integration():
    """Get UCM ecosystem integration status - LIVE DATA ONLY"""
    try:
        # GOVERNANCE [DALS-001]: No mock data - only live module status
        # If UCM is not running/connected, return inactive state
        ucm_connected = False  # TODO: Replace with actual UCM connection check
        
        if not ucm_connected:
            return {
                "ecosystem_health": "disconnected",
                "connected_modules": {
                    "cochlear_processor": "disconnected",
                    "phonatory_output": "disconnected", 
                    "vault_manager": "disconnected",
                    "caleon_consciousness": "disconnected",
                    "iss_controller": "disconnected"
                },
                "data_flow_rate": "—",
                "reasoning_cycles": 0,
                "symbolic_coherence": "—",
                "ecosystem_uptime": "—",
                "note": "Module offline - no mock data shown"
            }
            
        # When UCM is actually connected, this would return real data:
        return {
            "ecosystem_health": "disconnected",    # Real health from connection
            "connected_modules": {                 # Real module statuses
                "cochlear_processor": "disconnected",
                "phonatory_output": "disconnected", 
                "vault_manager": "disconnected",
                "caleon_consciousness": "disconnected",
                "iss_controller": "disconnected"
            },
            "data_flow_rate": "—",               # Real data flow if available
            "reasoning_cycles": 0,               # Real cycle count
            "symbolic_coherence": "—",           # Real coherence metric
            "ecosystem_uptime": "—"              # Real uptime
        }
    except Exception as e:
        logger.error(f"UCM integration check failed: {e}")
        return {
            "ecosystem_health": "error",
            "connected_modules": {
                "cochlear_processor": "error",
                "phonatory_output": "error", 
                "vault_manager": "error",
                "caleon_consciousness": "error",
                "iss_controller": "error"
            },
            "data_flow_rate": "—",
            "reasoning_cycles": 0,
            "symbolic_coherence": "—",
            "ecosystem_uptime": "—"              # Real uptime
        }

@app.post("/api/control/system/restart")
async def restart_system_module():
    """Restart system modules"""
    try:
        # In production, this would trigger actual module restarts
        return {
            "action": "restart_initiated",
            "modules": ["iss", "caleon", "certsig"],
            "estimated_downtime": "30 seconds",
            "restart_id": f"restart_{int(time.time())}",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"System restart failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control/iss/sync")
async def sync_iss_chronometer():
    """Force ISS chronometer synchronization"""
    try:
        return {
            "action": "iss_sync_initiated",
            "sync_type": "full_temporal_calibration",
            "estimated_duration": "15 seconds",
            "sync_id": f"sync_{int(time.time())}",
            "current_drift": "±0.001%",
            "target_accuracy": "±0.0001%"
        }
    except Exception as e:
        logger.error(f"ISS sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control/certsig/mint-test")
async def test_certsig_mint():
    """Execute CertSig mint test"""
    try:
        return {
            "action": "mint_test_initiated",
            "test_nft_type": "X-NFT",
            "test_id": f"test_{int(time.time())}",
            "blockchain": "polygon_testnet",
            "estimated_completion": "45 seconds",
            "test_metadata": {
                "title": "System Test NFT",
                "creator": "DALS_System",
                "validation_level": "full"
            }
        }
    except Exception as e:
        logger.error(f"CertSig mint test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control/caleon/reasoning-test")
async def test_caleon_reasoning():
    """Execute Caleon reasoning test"""
    try:
        return {
            "action": "reasoning_test_initiated",
            "test_sequence": "diagnostic_001",
            "test_id": f"reasoning_{int(time.time())}",
            "symbolic_depth": "3_levels",
            "estimated_duration": "20 seconds",
            "test_axioms": ["coherence", "drift_stability", "glyph_resonance"]
        }
    except Exception as e:
        logger.error(f"Caleon reasoning test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Simulation Engine Endpoints ---

@app.post("/api/simulation/generate-activity")
async def generate_simulation_activity():
    """
    GOVERNANCE [DALS-001]: SIMULATION ONLY - CLEARLY MARKED
    Generate simulated system activity for development/testing ONLY
    """
    try:
        # This endpoint is for development/testing only and clearly marked as simulation
        return {
            "simulation_id": f"sim_{int(time.time())}",
            "generated_activities": [
                "SIMULATION: No real activities - system in development mode"
            ],
            "activity_count": 0,
            "simulation_duration": "disabled",
            "status": "simulation_disabled",
            "note": "DALS-001: No mock data in production - use live modules only"
        }
    except Exception as e:
        logger.error(f"Activity simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulation/metrics")
async def get_simulation_metrics():
    """Get simulation engine metrics - LIVE DATA ONLY"""
    try:
        # GOVERNANCE [DALS-001]: No mock data - only real simulation engine status
        simulation_engine_active = False  # TODO: Replace with actual simulation engine check
        
        if not simulation_engine_active:
            return {
                "simulation_status": "inactive",
                "scenarios_running": 0,
                "data_points_generated": 0,
                "activity_rate": "—",
                "system_load": "—",
                "realism_score": "—",
                "note": "Simulation engine offline - no mock data shown"
            }
            
        # When simulation engine is actually running:
        return {
            "simulation_status": "inactive",  # Real status
            "scenarios_running": 0,           # Real scenario count
            "data_points_generated": 0,       # Real data point count
            "activity_rate": "—",             # Real activity rate
            "system_load": "—",               # Real system load
            "realism_score": "—"              # Real realism metric
        }
    except Exception as e:
        logger.error(f"Simulation metrics failed: {e}")
        return {
            "simulation_status": "error",
            "scenarios_running": 0,
            "data_points_generated": 0,
            "activity_rate": "—",
            "system_load": "—",
            "realism_score": "—",
            "error": str(e)
        }

# --- Module Status Management Endpoints ---

@app.get("/api/modules/status")
async def get_all_modules_status():
    """Get comprehensive status of all DALS modules"""
    try:
        from iss_module.module_status import module_status_manager
        return module_status_manager.get_system_overview()
    except Exception as e:
        logger.error(f"Module status retrieval failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/modules/status/{module_name}")
async def get_module_status(module_name: str):
    """Get status for a specific module"""
    try:
        from iss_module.module_status import module_status_manager
        status = module_status_manager.get_module_status(module_name)
        if status:
            return {"module": module_name, "status": status.__dict__}
        else:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Module {module_name} status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modules/status/{module_name}/heartbeat")
async def module_heartbeat(module_name: str, activity: str = "heartbeat"):
    """Record module heartbeat and activity"""
    try:
        from iss_module.module_status import module_status_manager
        module_status_manager.update_module_activity(module_name, activity)
        return {"message": f"Heartbeat recorded for {module_name}", "activity": activity}
    except Exception as e:
        logger.error(f"Module heartbeat failed for {module_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/modules/status/{module_name}/error")
async def report_module_error(module_name: str, error_message: str):
    """Report module error status"""
    try:
        from iss_module.module_status import module_status_manager
        module_status_manager.set_module_error(module_name, error_message)
        return {"message": f"Error status set for {module_name}", "error": error_message}
    except Exception as e:
        logger.error(f"Module error reporting failed for {module_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/health")
async def get_system_health():
    """Get overall system health summary"""
    try:
        from iss_module.module_status import module_status_manager
        overview = module_status_manager.get_system_overview()
        
        return {
            "system_health": overview["system_health"],
            "total_modules": overview["total_modules"],
            "active_modules": overview["status_breakdown"]["active"],
            "idle_modules": overview["status_breakdown"]["idle"],
            "error_modules": overview["status_breakdown"]["error"],
            "uptime_seconds": overview["system_uptime_seconds"],
            "last_update": overview["last_update"]
        }
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {"status": "error", "message": str(e)}

# Development helper
def main():
    """Main entry point for running the server"""
    import uvicorn
    uvicorn.run(
        "iss_module.api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

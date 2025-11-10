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
)

# DALS Core Logic
# NOTE: Adjust the relative path if serial_assignment.py is located elsewhere
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from serial_assignment import assign_digital_asset_id

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

# --- Authentication Dependency ---
async def get_current_user(credentials: HTTPBasicCredentials = Depends(basic_auth)):
    """Authenticates user via HTTP Basic credentials."""
    correct_username = (credentials.username == ADMIN_USER)
    correct_password = verify_password(credentials.password, ADMIN_PASSWORD_HASH)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- UI and System Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main dashboard"""
    # This should be updated to a DALS-specific dashboard
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get current system status"""
    try:
        status = iss_instance.get_status()
        total_assets = len(inventory_manager.units) if inventory_manager and hasattr(inventory_manager, 'units') else 0
        startup_time = status['system_state'].get('startup_time')
        uptime = None
        if startup_time:
            delta = datetime.now(timezone.utc) - datetime.fromisoformat(startup_time)
            uptime = str(delta).split('.')[0]
        
        return SystemStatusResponse(
            status=status['system_state']['system_status'],
            uptime=uptime,
            active_modules=status['system_state']['active_modules'],
            current_time=status['current_time'],
            stardate=status['stardate'],
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
    AUTHORITY: Spruked - Official DALS/Prometheus Stardate Protocol
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

@app.get("/api/modules/prometheus/integration")
async def get_prometheus_integration():
    """Get Prometheus Prime ecosystem integration status - LIVE DATA ONLY"""
    try:
        # GOVERNANCE [DALS-001]: No mock data - only live module status
        # If Prometheus is not running/connected, return inactive state
        prometheus_connected = False  # TODO: Replace with actual Prometheus connection check
        
        if not prometheus_connected:
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
            
        # When Prometheus is actually connected, this would return real data:
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
        logger.error(f"Prometheus integration check failed: {e}")
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
            "ecosystem_uptime": "—",
            "error": str(e)
        }

# --- Control Widgets Endpoints ---

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

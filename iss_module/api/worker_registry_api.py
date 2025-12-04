"""
DALS Worker Registry API
Endpoints for worker registration, heartbeat, and listing.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import the registry
try:
    from dals.registry import register_worker, update_heartbeat, list_workers, get_worker, MODEL_CATALOG
    REGISTRY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Worker registry not available: {e}")
    REGISTRY_AVAILABLE = False
    MODEL_CATALOG = {}

logger = logging.getLogger("DALS.Registry.API")
router = APIRouter(prefix="/workers", tags=["worker-registry"])


# Pydantic Models
class WorkerRegistration(BaseModel):
    """Worker registration request"""
    name: str = Field(..., description="Worker name", example="Josephine-01")
    worker_type: str = Field(..., description="Worker type from MODEL_CATALOG", example="truemark")
    api_url: str = Field(..., description="Worker API URL", example="http://josephine-01:8080")
    user_id: str = Field(..., description="Target user ID", example="user_123")


class WorkerHeartbeat(BaseModel):
    """Worker heartbeat request"""
    worker_name: str = Field(..., description="Worker name", example="Josephine-01")


class WorkerEntry(BaseModel):
    """Worker registry entry response"""
    worker_name: str
    worker_type: str
    model_number: str = Field(..., description="DALS Model Number (DMN)", example="DMN-TM-01")
    serial_number: str = Field(..., description="DALS Serial Number (DSN)", example="DMN-TM-01-A7F3B9E1-89F2C")
    api_url: str
    user_id: str
    deployed_at: float
    deployed_iso: str
    status: str
    heartbeat: float | None


class RegistryStatus(BaseModel):
    """Registry system status"""
    available: bool
    total_workers: int = 0
    active_workers: int = 0
    model_families: List[str] = Field(default_factory=list)


# Endpoints
@router.post("/register", response_model=WorkerEntry, summary="Register a new worker")
async def register_new_worker(req: WorkerRegistration):
    """
    Register a new worker with DALS model number and serial number.
    
    Workers self-register on startup using this endpoint.
    """
    if not REGISTRY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Worker registry not available")
    
    try:
        entry = register_worker(
            name=req.name,
            worker_type=req.worker_type,
            api_url=req.api_url,
            user_id=req.user_id
        )
        
        logger.info(f"Registered worker: {entry['worker_name']} ({entry['model_number']}) - Serial: {entry['serial_number']}")
        
        return WorkerEntry(**entry)
    except Exception as e:
        logger.error(f"Worker registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/heartbeat", summary="Update worker heartbeat")
async def worker_heartbeat(req: WorkerHeartbeat):
    """
    Update worker heartbeat to mark as active.
    
    Workers should call this every 30-60 seconds.
    """
    if not REGISTRY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Worker registry not available")
    
    success = update_heartbeat(req.worker_name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Worker {req.worker_name} not found in registry")
    
    return {"status": "updated", "worker": req.worker_name}


@router.get("/list", response_model=List[WorkerEntry], summary="List all workers")
async def list_all_workers():
    """
    List all registered workers with their model numbers and serials.
    
    Returns DALS-001 compliant data (real or zeros, never mock).
    """
    if not REGISTRY_AVAILABLE:
        return []
    
    try:
        workers = list_workers()
        return [WorkerEntry(**w) for w in workers]
    except Exception as e:
        logger.error(f"Failed to list workers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list workers: {str(e)}")


@router.get("/{worker_name}", response_model=WorkerEntry, summary="Get worker by name")
async def get_worker_details(worker_name: str):
    """
    Get detailed information about a specific worker.
    """
    if not REGISTRY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Worker registry not available")
    
    worker = get_worker(worker_name)
    
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker {worker_name} not found")
    
    return WorkerEntry(**worker)


@router.get("/status", response_model=RegistryStatus, summary="Registry system status")
async def registry_status():
    """
    Get worker registry system status.
    
    DALS-001 compliant: Returns real counts or zeros.
    """
    if not REGISTRY_AVAILABLE:
        return RegistryStatus(available=False)
    
    workers = list_workers()
    active = sum(1 for w in workers if w.get("status") == "active")
    
    # Extract unique model families (e.g., TM, RG, GT from DMN-TM-01, DMN-RG-01, etc.)
    families = set()
    for worker_type in MODEL_CATALOG.keys():
        model = MODEL_CATALOG[worker_type]
        family = model.split("-")[1] if "-" in model else "UNKNOWN"
        families.add(family)
    
    return RegistryStatus(
        available=True,
        total_workers=len(workers),
        active_workers=active,
        model_families=sorted(list(families))
    )


@router.get("/models/catalog", summary="Get model catalog")
async def get_model_catalog():
    """
    Get the complete MODEL_CATALOG showing all worker types and their DMN codes.
    """
    if not REGISTRY_AVAILABLE:
        return {}
    
    return MODEL_CATALOG

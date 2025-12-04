"""
Predicate Update API - Caleon → Worker Broadcasting
=====================================================
Enables Caleon to broadcast newly invented predicates to all active workers
in < 20ms for real-time cognitive evolution.

Part of the GOAT cognitive flywheel architecture.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
import asyncio
import logging
import os
import uuid

logger = logging.getLogger("DALS.PredicateUpdate")

# Router
predicate_router = APIRouter(prefix="/worker", tags=["Predicate Broadcasting"])

# Worker registry URL (DALS maintains this)
WORKER_REGISTRY_URL = os.getenv("WORKER_REGISTRY", "http://localhost:9999/registry")


# --- Models ---

class EvidenceItem(BaseModel):
    """Evidence for predicate invention"""
    user_id: str
    worker: str
    freq: int = Field(..., ge=1, description="Frequency of occurrence")


class PredicateModel(BaseModel):
    """Caleon-invented predicate"""
    predicate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., pattern=r'^[a-z_]+$', description="Predicate name (snake_case)")
    signature: List[str] = Field(..., min_length=2, max_length=2, description="[A, B] - edge signature")
    definition: Optional[str] = Field(None, description="Human-readable definition")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    evidence: List[EvidenceItem] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @validator('signature')
    def validate_signature(cls, v):
        if len(v) != 2:
            raise ValueError('Signature must have exactly 2 elements [A, B]')
        return v


class WorkerEndpoint(BaseModel):
    """Worker registration info"""
    url: str
    worker_id: str
    worker_name: str
    status: str = "active"


# --- Global State ---

# In-memory predicate cache (for deduplication)
_predicate_cache: Dict[str, PredicateModel] = {}

# Rate limiting: max 10 predicates/min
_broadcast_count = 0
_broadcast_window_start = datetime.utcnow()
MAX_BROADCASTS_PER_MINUTE = 10


# --- Endpoints ---

@predicate_router.post("/predicate_update", status_code=204, summary="Broadcast Predicate to Workers")
async def publish_predicate(pred: PredicateModel, background: BackgroundTasks):
    """
    Caleon → Workers: Broadcast newly invented predicate
    
    - Accepts predicate from Caleon fusion engine
    - Fans out to all active workers asynchronously
    - Returns 204 immediately (fire-and-forget)
    - Rate limited to 10/min to prevent flooding
    """
    global _broadcast_count, _broadcast_window_start
    
    # Rate limiting check
    now = datetime.utcnow()
    if (now - _broadcast_window_start).total_seconds() > 60:
        _broadcast_count = 0
        _broadcast_window_start = now
    
    if _broadcast_count >= MAX_BROADCASTS_PER_MINUTE:
        raise HTTPException(status_code=503, detail="Predicate broadcast rate limit exceeded")
    
    # Idempotency check
    if pred.predicate_id in _predicate_cache:
        logger.info(f"Predicate {pred.predicate_id} already broadcasted - skipping")
        return
    
    # Cache and broadcast
    _predicate_cache[pred.predicate_id] = pred
    _broadcast_count += 1
    
    logger.info(f"Broadcasting predicate: {pred.name}({pred.signature[0]}, {pred.signature[1]}) "
                f"confidence={pred.confidence:.2f}")
    
    # Background task for async fan-out
    background.add_task(_broadcast_to_workers, pred.dict())
    
    return None


@predicate_router.get("/predicates", response_model=List[PredicateModel])
async def list_predicates(limit: int = 100):
    """List recently broadcasted predicates"""
    predicates = list(_predicate_cache.values())
    return sorted(predicates, key=lambda p: p.created_at, reverse=True)[:limit]


@predicate_router.get("/predicates/{predicate_id}", response_model=PredicateModel)
async def get_predicate(predicate_id: str):
    """Get specific predicate by ID"""
    if predicate_id not in _predicate_cache:
        raise HTTPException(status_code=404, detail="Predicate not found")
    return _predicate_cache[predicate_id]


# --- Broadcasting Logic ---

async def _broadcast_to_workers(payload: dict):
    """
    Fan-out predicate to all active workers
    Fire-and-forget with < 20ms target latency
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch active worker registry
            workers = await _fetch_workers(session)
            
            if not workers:
                logger.warning("No active workers found in registry")
                return
            
            # Fire parallel requests with 500ms timeout
            tasks = [
                _send_to_worker(session, worker, payload)
                for worker in workers
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            success_count = sum(1 for r in results if r is True)
            logger.info(f"Predicate broadcast: {success_count}/{len(workers)} workers updated")
            
    except Exception as e:
        logger.error(f"Predicate broadcast failed: {e}")


async def _fetch_workers(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    """Fetch active workers from DALS registry"""
    try:
        async with session.get(
            WORKER_REGISTRY_URL,
            timeout=aiohttp.ClientTimeout(total=1.0)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Filter only active workers
                return [w for w in data if w.get("status") == "active"]
            else:
                logger.warning(f"Worker registry returned {resp.status}")
                return []
    except Exception as e:
        logger.error(f"Failed to fetch worker registry: {e}")
        return []


async def _send_to_worker(session: aiohttp.ClientSession, worker: dict, payload: dict) -> bool:
    """
    Send predicate to single worker
    Returns True on success, False on failure
    """
    url = worker.get("url", "").rstrip("/") + "/predicate"
    worker_id = worker.get("worker_id", "unknown")
    
    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=0.5)  # 500ms max
        ) as resp:
            if resp.status in (200, 204):
                logger.debug(f"Predicate sent to worker {worker_id}")
                return True
            else:
                logger.warning(f"Worker {worker_id} rejected predicate: {resp.status}")
                return False
    except asyncio.TimeoutError:
        logger.warning(f"Worker {worker_id} timeout - predicate delivery failed")
        return False
    except Exception as e:
        logger.warning(f"Worker {worker_id} unreachable: {e}")
        return False


# --- Stats & Monitoring ---

@predicate_router.get("/stats")
async def get_broadcast_stats():
    """Get predicate broadcasting statistics"""
    return {
        "total_predicates": len(_predicate_cache),
        "broadcasts_this_minute": _broadcast_count,
        "window_start": _broadcast_window_start.isoformat(),
        "rate_limit": MAX_BROADCASTS_PER_MINUTE,
        "status": "healthy" if _broadcast_count < MAX_BROADCASTS_PER_MINUTE else "throttled"
    }

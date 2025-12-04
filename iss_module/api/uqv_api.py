"""
Unanswered Query Vault (UQV) API
FastAPI routes for storing and retrieving unanswered queries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger("DALS.UQV")

uqv_router = APIRouter(prefix="/api/uqv", tags=["Unanswered Query Vault"])

# In-memory vault (replace with DB in production)
uqv_store: List[dict] = []

class UQVStoreRequest(BaseModel):
    """Request to store an unanswered query."""
    user_id: str = Field(..., description="User who asked the query")
    session_id: str = Field(..., description="Session identifier")
    query_text: str = Field(..., description="The unanswered query")
    query_vec: Optional[List[float]] = Field(None, description="Optional query embedding")
    skg_clusters_returned: int = Field(0, description="Number of clusters found")
    max_cluster_conf: float = Field(0.0, description="Maximum cluster confidence")
    worker_name: Optional[str] = Field("unknown", description="Worker that handled query")
    vault_reason: str = Field("no_cluster", description="Reason for vaulting")

class UQVQueryResponse(BaseModel):
    """Vaulted query with metadata."""
    id: int
    user_id: str
    session_id: str
    query_text: str
    skg_clusters_returned: int
    max_cluster_conf: float
    worker_name: str
    vault_reason: str
    created_at: str

@uqv_router.post("/store", status_code=204)
async def store_unanswered_query(req: UQVStoreRequest):
    """
    Store an unanswered query for later analysis and SKG training.
    Fire-and-forget endpoint - always returns 204.
    """
    entry = req.dict()
    entry["id"] = len(uqv_store) + 1
    entry["created_at"] = datetime.utcnow().isoformat()
    uqv_store.append(entry)
    
    logger.info(f"UQV stored: worker={req.worker_name}, reason={req.vault_reason}, clusters={req.skg_clusters_returned}")
    return None

@uqv_router.get("/queries", response_model=List[UQVQueryResponse])
async def get_vaulted_queries(
    reason: Optional[str] = None,
    worker: Optional[str] = None,
    limit: int = 100
):
    """
    Retrieve vaulted queries for review and training.
    
    - **reason**: Filter by vault reason (no_cluster, low_conf, escalated)
    - **worker**: Filter by worker name
    - **limit**: Maximum queries to return
    """
    filtered = uqv_store.copy()
    
    if reason:
        filtered = [q for q in filtered if q.get("vault_reason") == reason]
    if worker:
        filtered = [q for q in filtered if q.get("worker_name") == worker]
    
    return filtered[:limit]

@uqv_router.get("/stats")
async def get_uqv_stats():
    """
    Get statistics about vaulted queries.
    Used for monitoring SKG health and training needs.
    """
    total = len(uqv_store)
    by_reason = {}
    by_worker = {}
    
    for q in uqv_store:
        reason = q.get("vault_reason", "unknown")
        worker = q.get("worker_name", "unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_worker[worker] = by_worker.get(worker, 0) + 1
    
    return {
        "total_queries": total,
        "by_reason": by_reason,
        "by_worker": by_worker,
        "last_updated": datetime.utcnow().isoformat()
    }

@uqv_router.post("/bootstrap")
async def bootstrap_from_vault():
    """
    Trigger SKG bootstrap from vaulted queries.
    Weekly cron job endpoint for continuous learning.
    """
    no_cluster_queries = [q for q in uqv_store if q.get("vault_reason") == "no_cluster"]
    
    # TODO: Send to SKG for predicate invention
    # TODO: Flag for human trainer review
    
    logger.info(f"UQV bootstrap triggered: {len(no_cluster_queries)} queries pending")
    
    return {
        "queries_to_process": len(no_cluster_queries),
        "status": "bootstrap_queued"
    }

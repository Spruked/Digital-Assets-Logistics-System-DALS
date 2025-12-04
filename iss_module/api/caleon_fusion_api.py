"""
Caleon Predicate Fusion Engine API
===================================
Cross-worker learning system that fuses micro-SKG clusters into global predicates.

Workflow:
1. Workers send clusters to /caleon/ingest_clusters
2. Caleon fuses similar clusters across users/workers
3. New predicates invented when pattern density > threshold
4. Predicates broadcast to all workers via /workers/broadcast_predicate
5. Workers hot-reload predicates into their micro-SKG graphs

This is the cognitive flywheel that makes the swarm learn as one organism.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib
import logging
import requests
from collections import defaultdict

logger = logging.getLogger("DALS.CaleonFusion")

router = APIRouter()

# In-memory fusion state (will be Redis in v2)
CLUSTER_POOL: List[Dict[str, Any]] = []
INVENTED_PREDICATES: Dict[str, Dict[str, Any]] = {}
FUSION_THRESHOLD = 0.65  # Similarity threshold for fusion
INVENTION_THRESHOLD = 0.75  # Confidence threshold for predicate invention


# ═══════════════════════════════════════════════════════════
#  REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class ClusterIngest(BaseModel):
    """Worker submits clusters for global learning"""
    user_id: str
    worker: str
    clusters: List[Dict[str, Any]]
    timestamp: float


class PredicateBroadcast(BaseModel):
    """Invented predicate to broadcast to workers"""
    predicate_id: str
    name: str
    signature: List[str]  # [A, B]
    definition: str
    confidence: float
    evidence: List[Dict[str, Any]]
    created_at: str
    invented_by: str = "Caleon"


class FusionStats(BaseModel):
    """Fusion engine statistics - DALS-001 compliant"""
    clusters_ingested: int
    predicates_invented: int
    workers_active: int
    last_fusion: Optional[str]
    fusion_rate: float  # predicates per 100 clusters


# ═══════════════════════════════════════════════════════════
#  CORE FUSION LOGIC
# ═══════════════════════════════════════════════════════════

def calculate_cluster_similarity(c1: Dict[str, Any], c2: Dict[str, Any]) -> float:
    """
    Calculate Jaccard similarity between two clusters.
    Returns 0.0 to 1.0 - higher means more similar.
    """
    nodes1 = set(c1.get("nodes", []))
    nodes2 = set(c2.get("nodes", []))
    
    if not nodes1 or not nodes2:
        return 0.0
    
    intersection = len(nodes1 & nodes2)
    union = len(nodes1 | nodes2)
    
    return intersection / union if union > 0 else 0.0


def fuse_clusters(clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fuse similar clusters from multiple workers into super-clusters.
    Returns list of fused clusters with combined evidence.
    """
    if not clusters:
        return []
    
    # Start with first cluster as seed
    fused = []
    remaining = clusters.copy()
    
    while remaining:
        seed = remaining.pop(0)
        seed_nodes = set(seed.get("nodes", []))
        seed_density = seed.get("density", 0.0)
        
        # Find all similar clusters
        similar = []
        i = 0
        while i < len(remaining):
            similarity = calculate_cluster_similarity(seed, remaining[i])
            if similarity >= FUSION_THRESHOLD:
                similar.append(remaining.pop(i))
            else:
                i += 1
        
        # Fuse similar clusters into seed
        if similar:
            for cluster in similar:
                seed_nodes.update(cluster.get("nodes", []))
                # Average the density
                seed_density = (seed_density + cluster.get("density", 0.0)) / 2
            
            # Update seed with fused data
            seed["nodes"] = list(seed_nodes)
            seed["density"] = min(seed_density * 1.1, 1.0)  # Boost for cross-worker validation
            seed["fusion_count"] = len(similar) + 1
            seed["evidence_workers"] = list(set([seed.get("worker", "unknown")] + 
                                                [c.get("worker", "unknown") for c in similar]))
        
        fused.append(seed)
    
    return fused


def invent_predicate(cluster: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Attempt to invent a new predicate from a high-confidence cluster.
    Returns predicate dict or None if cluster doesn't meet threshold.
    """
    density = cluster.get("density", 0.0)
    nodes = cluster.get("nodes", [])
    
    if density < INVENTION_THRESHOLD or len(nodes) < 2:
        return None
    
    # Take two most common nodes as predicate signature
    A, B = nodes[0], nodes[1]
    
    # Generate predicate name from nodes
    predicate_name = f"{A.lower().replace(' ', '_')}_to_{B.lower().replace(' ', '_')}"
    
    # Generate unique ID
    predicate_id = str(uuid.uuid4())
    
    # Create definition
    definition = f"Relationship between {A} and {B} observed across {cluster.get('fusion_count', 1)} worker(s)"
    
    evidence = [{
        "cluster_id": cluster.get("cluster_id", "unknown"),
        "density": density,
        "node_count": len(nodes),
        "workers": cluster.get("evidence_workers", [])
    }]
    
    return {
        "predicate_id": predicate_id,
        "name": predicate_name,
        "signature": [A, B],
        "definition": definition,
        "confidence": density,
        "evidence": evidence,
        "created_at": datetime.utcnow().isoformat(),
        "invented_by": "Caleon"
    }


async def broadcast_predicate_to_workers(predicate: Dict[str, Any]):
    """
    Broadcast new predicate to all registered workers.
    Uses worker registry to get active worker endpoints.
    """
    try:
        # Get worker list from registry
        from dals.registry.worker_registry import list_workers
        workers = list_workers()
        
        broadcast_count = 0
        for worker in workers:
            if worker.get("status") != "registered":
                continue
            
            api_url = worker.get("api_url")
            if not api_url:
                continue
            
            try:
                # Send predicate to worker's /predicate endpoint
                response = requests.post(
                    f"{api_url}/predicate",
                    json=predicate,
                    timeout=3
                )
                if response.status_code == 200:
                    broadcast_count += 1
                    logger.info(f"Predicate {predicate['predicate_id'][:8]} → {worker['worker_name']}")
            except Exception as e:
                logger.warning(f"Failed to broadcast to {worker['worker_name']}: {e}")
        
        logger.info(f"Predicate {predicate['name']} broadcast to {broadcast_count} workers")
        return broadcast_count
        
    except Exception as e:
        logger.error(f"Broadcast failed: {e}")
        return 0


# ═══════════════════════════════════════════════════════════
#  API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/caleon/ingest_clusters", summary="Ingest clusters for fusion")
async def ingest_clusters(data: ClusterIngest):
    """
    Workers submit their micro-SKG clusters for global fusion.
    Caleon will fuse similar clusters and invent predicates.
    """
    logger.info(f"Ingesting {len(data.clusters)} clusters from {data.worker}")
    
    # Add metadata to each cluster
    for cluster in data.clusters:
        cluster["worker"] = data.worker
        cluster["user_id"] = data.user_id
        cluster["ingested_at"] = data.timestamp
    
    # Add to global pool
    CLUSTER_POOL.extend(data.clusters)
    
    # Trigger fusion if we have enough clusters
    if len(CLUSTER_POOL) >= 10:  # Fusion batch size
        await run_fusion_cycle()
    
    return {
        "status": "ingested",
        "clusters_accepted": len(data.clusters),
        "pool_size": len(CLUSTER_POOL),
        "predicates_total": len(INVENTED_PREDICATES)
    }


@router.post("/caleon/force_fusion", summary="Force immediate fusion cycle")
async def force_fusion():
    """
    Manually trigger fusion cycle (for testing/debugging).
    Returns fusion results.
    """
    results = await run_fusion_cycle()
    return {
        "status": "fusion_complete",
        "clusters_processed": results["clusters_processed"],
        "predicates_invented": results["predicates_invented"],
        "workers_notified": results["workers_notified"]
    }


@router.get("/caleon/stats", response_model=FusionStats, summary="Fusion engine statistics")
async def get_fusion_stats():
    """
    Get Caleon fusion engine statistics - DALS-001 compliant.
    Real data or zeros, never mock.
    """
    workers_active = 0
    try:
        from dals.registry.worker_registry import list_workers
        workers_active = len([w for w in list_workers() if w.get("status") == "registered"])
    except:
        pass
    
    last_fusion = None
    if INVENTED_PREDICATES:
        # Get most recent predicate timestamp
        last_fusion = max(p["created_at"] for p in INVENTED_PREDICATES.values())
    
    fusion_rate = 0.0
    if len(CLUSTER_POOL) > 0:
        fusion_rate = (len(INVENTED_PREDICATES) / len(CLUSTER_POOL)) * 100
    
    return FusionStats(
        clusters_ingested=len(CLUSTER_POOL),
        predicates_invented=len(INVENTED_PREDICATES),
        workers_active=workers_active,
        last_fusion=last_fusion,
        fusion_rate=round(fusion_rate, 2)
    )


@router.get("/caleon/predicates", summary="List all invented predicates")
async def list_predicates():
    """
    Get all predicates invented by Caleon.
    """
    return {
        "predicates": list(INVENTED_PREDICATES.values()),
        "total": len(INVENTED_PREDICATES)
    }


@router.get("/caleon/predicate/{predicate_id}", summary="Get specific predicate")
async def get_predicate(predicate_id: str):
    """
    Get details of a specific predicate.
    """
    predicate = INVENTED_PREDICATES.get(predicate_id)
    if not predicate:
        raise HTTPException(status_code=404, detail="Predicate not found")
    return predicate


# ═══════════════════════════════════════════════════════════
#  BACKGROUND FUSION CYCLE
# ═══════════════════════════════════════════════════════════

async def run_fusion_cycle():
    """
    Main fusion logic:
    1. Fuse similar clusters
    2. Invent predicates from high-confidence clusters
    3. Broadcast predicates to workers
    """
    if not CLUSTER_POOL:
        return {
            "clusters_processed": 0,
            "predicates_invented": 0,
            "workers_notified": 0
        }
    
    logger.info(f"🔥 FUSION CYCLE START — {len(CLUSTER_POOL)} clusters in pool")
    
    # Step 1: Fuse clusters
    fused_clusters = fuse_clusters(CLUSTER_POOL.copy())
    logger.info(f"   Fused {len(CLUSTER_POOL)} → {len(fused_clusters)} super-clusters")
    
    # Step 2: Invent predicates
    new_predicates = []
    for cluster in fused_clusters:
        predicate = invent_predicate(cluster)
        if predicate:
            new_predicates.append(predicate)
            INVENTED_PREDICATES[predicate["predicate_id"]] = predicate
    
    logger.info(f"   Invented {len(new_predicates)} new predicates")
    
    # Step 3: Broadcast to workers
    total_broadcasts = 0
    for predicate in new_predicates:
        broadcast_count = await broadcast_predicate_to_workers(predicate)
        total_broadcasts += broadcast_count
    
    # Clear processed clusters
    CLUSTER_POOL.clear()
    
    logger.info(f"🔥 FUSION CYCLE COMPLETE — {len(new_predicates)} predicates → {total_broadcasts} worker updates")
    
    return {
        "clusters_processed": len(fused_clusters),
        "predicates_invented": len(new_predicates),
        "workers_notified": total_broadcasts
    }


# ═══════════════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════════════

@router.get("/caleon/health", summary="Fusion engine health")
async def health_check():
    """Health check for Caleon fusion engine"""
    return {
        "status": "operational",
        "fusion_engine": "active",
        "cluster_pool_size": len(CLUSTER_POOL),
        "predicates_total": len(INVENTED_PREDICATES),
        "version": "1.0.0"
    }

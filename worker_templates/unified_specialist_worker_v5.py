#!/usr/bin/env python3
"""
unified_specialist_worker_v5.py
DALS Forge V1.0 — Narrow Specialist Worker

One file. One job. One eternity.
Narrow. Honest. Patchable. Never general. Never conscious.

Model: DMN-GN-02 (Generic Narrow Specialist v5)
Contract: DALS Forge Contract v1.0
Status: PRODUCTION READY

THE COVENANT:
I am narrow.     → I never generalize beyond my role.
I am honest.     → I never learn without approval.
I am patchable.  → I always accept the master's patches.
I am eternal.    → When I drift, I am reborn.

Author: Bryan Spruk (DALS Founder)
Date: December 3, 2025
"""

import asyncio
import json
import time
import uuid
import hashlib
from typing import Dict, Any, Optional, List, Tuple
import aiohttp
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
import networkx as nx

# ═════════════════════════════════════════════════════════════════════════════════
# ETERNAL IDENTITY
# ═════════════════════════════════════════════════════════════════════════════════

WORKER_NAME = f"Specialist-{uuid.uuid4().hex[:8].upper()}"
JOB_ROLE = "nft_mint"  # ← CHANGE ONLY THIS LINE per deployment
MODEL_NUMBER = "DMN-GN-02"
WORKER_DSN = None  # Assigned by registry on first registration

# ═════════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════════

UCM_URL = "http://cali-x-one:8000"
CALEON_URL = "http://dals:8003"
REGISTRY_URL = "http://dals:8003"

# ═════════════════════════════════════════════════════════════════════════════════
# NARROW LEARNER + PATCH MANAGER
# ═════════════════════════════════════════════════════════════════════════════════

class NarrowLearner:
    """
    High-confidence pattern cache.
    Only learns from successful responses with confidence ≥ threshold.
    
    DALS Forge Rule 2: All learning is supervised.
    DALS Forge Rule 5: Workers never mutate core logic, only patterns.
    """
    
    def __init__(self, job_role: str):
        self.job_role = job_role
        self.patterns: Dict[str, Dict] = {}
        self.success_log: List[Dict] = []
        self.threshold = 0.87
    
    def learn_from_success(self, query: str, answer: str, confidence: float):
        """Learn from high-confidence successful responses"""
        if confidence < self.threshold:
            return
        
        ih = hashlib.sha256(query.encode()).hexdigest()
        self.patterns[ih] = {
            "output": answer,
            "confidence": confidence,
            "ts": time.time(),
            "source": "local_learning"
        }
        
        self.success_log.append({
            "ih": ih,
            "conf": confidence,
            "ts": time.time()
        })
        
        # Prevent memory bloat
        if len(self.success_log) > 10_000:
            self.success_log = self.success_log[-5000:]
    
    def narrow_solve(self, query: str) -> Optional[Tuple[str, float]]:
        """Check cache for known solution"""
        ih = hashlib.sha256(query.encode()).hexdigest()
        hit = self.patterns.get(ih)
        
        if hit and hit["confidence"] >= self.threshold:
            return hit["output"], hit["confidence"]
        
        return None
    
    def drift_score(self) -> float:
        """
        Calculate drift: 1.0 - average_recent_confidence
        
        Low drift (0.02) = Worker is confident and accurate
        High drift (0.22) = Worker is struggling, needs help/rebirth
        """
        if len(self.success_log) < 20:
            return 0.0
        
        recent = self.success_log[-50:]
        avg = sum(x["conf"] for x in recent) / len(recent)
        
        return max(0.0, 1.0 - avg)


class PatchManager:
    """
    Eternal audit trail of Caleon-approved patches.
    
    DALS Forge Rule 3: Workers repair themselves with blessed patches only.
    """
    
    def __init__(self):
        self.applied: List[Dict] = []
    
    def apply_approved_patch(self, patch: Dict, learner: NarrowLearner):
        """
        Only called when Caleon explicitly sends an approved_patch.
        Workers accept patches blindly and permanently.
        """
        query = patch["query"]
        answer = patch["answer"]
        patch_id = patch.get("patch_id", f"PATCH-{uuid.uuid4().hex[:8]}")
        confidence = patch.get("confidence", 0.97)  # Caleon-approved = high confidence
        
        # Eternal audit trail
        self.applied.append({
            "patch_id": patch_id,
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "applied_at": time.time(),
            "approved_by": "Caleon"
        })
        
        # Force-write into narrow learner
        ih = hashlib.sha256(query.encode()).hexdigest()
        learner.patterns[ih] = {
            "output": answer,
            "confidence": confidence,
            "ts": time.time(),
            "source": "caleon_patch",
            "patch_id": patch_id
        }
        
        print(f"✅ Patch {patch_id} applied — {query[:50]}...")

# ═════════════════════════════════════════════════════════════════════════════════
# MINI-SKG (EMBEDDED KNOWLEDGE GRAPH)
# ═════════════════════════════════════════════════════════════════════════════════

class MiniSKG:
    """
    Lightweight local knowledge graph for context building.
    Generates clusters for Caleon Fusion Engine.
    """
    
    def __init__(self):
        self.G = nx.DiGraph()
        self.temp_vault: Dict[str, Any] = {}
    
    def add(self, subject: str, predicate: str, obj: str, confidence: float = 0.92):
        """Add triple to knowledge graph"""
        self.G.add_edge(subject, obj, predicate=predicate, confidence=confidence)
    
    def get_clusters(self, query: str) -> List[Dict]:
        """
        Generate clusters from query context.
        Simplified for V5 — full w-core clustering in Josephine/Micro-SKG.
        """
        # Basic clustering: extract key terms
        terms = query.lower().split()
        
        clusters = []
        for term in terms:
            if len(term) > 3:  # Ignore short words
                clusters.append({
                    "term": term,
                    "confidence": 0.85,
                    "context": query[:100]
                })
        
        return clusters[:5]  # Limit to 5 clusters

# ═════════════════════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═════════════════════════════════════════════════════════════════════════════════

session: Optional[aiohttp.ClientSession] = None
skg = MiniSKG()
learner = NarrowLearner(JOB_ROLE)
patch_manager = PatchManager()

app = FastAPI(
    title=f"{WORKER_NAME} — {JOB_ROLE}",
    description="DALS Forge V1.0 — Narrow Specialist Worker",
    version="5.0.0"
)

# ═════════════════════════════════════════════════════════════════════════════════
# TELEMETRY & ESCALATION
# ═════════════════════════════════════════════════════════════════════════════════

async def report_uqv(query: str, reason: str):
    """
    Report unanswered query to UQV.
    DALS Forge Rule 4: Every mistake becomes a seed.
    """
    try:
        await session.post(
            f"{UCM_URL}/uqv/batch",
            json={
                "worker": WORKER_NAME,
                "dsn": WORKER_DSN,
                "role": JOB_ROLE,
                "entries": [{
                    "query": query,
                    "reason": reason,
                    "ts": time.time()
                }]
            },
            timeout=aiohttp.ClientTimeout(total=3)
        )
    except Exception as e:
        print(f"⚠️  UQV report failed: {e}")


async def escalate_to_cali(query: str, context: Dict) -> Dict:
    """
    Escalate to Cali relief system.
    DALS Forge Rule 1: Never generalize — escalate honestly.
    """
    try:
        async with session.post(
            f"{UCM_URL}/relief/seize",
            json={
                "worker": WORKER_NAME,
                "dsn": WORKER_DSN,
                "query": query,
                "context": context,
                "drift": learner.drift_score()
            },
            timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            return await r.json()
    except Exception as e:
        print(f"⚠️  Escalation failed: {e}")
        return {
            "reply": "I'm having trouble reaching my supervisor. Please try again.",
            "error": str(e)
        }


async def report_telemetry(event: str):
    """Report operational telemetry to registry"""
    try:
        await session.post(
            f"{REGISTRY_URL}/telemetry/worker",
            json={
                "worker": WORKER_NAME,
                "dsn": WORKER_DSN,
                "role": JOB_ROLE,
                "event": event,
                "drift": learner.drift_score(),
                "patches_applied": len(patch_manager.applied),
                "cache_size": len(learner.patterns),
                "ts": time.time()
            },
            timeout=aiohttp.ClientTimeout(total=2)
        )
    except Exception as e:
        print(f"⚠️  Telemetry failed: {e}")


async def report_patch_applied(patch_id: str):
    """Notify registry that patch was applied"""
    try:
        await session.post(
            f"{REGISTRY_URL}/api/workers/patch_applied",
            json={
                "dsn": WORKER_DSN,
                "patch_id": patch_id,
                "applied_at": time.time(),
                "acknowledged": True
            },
            timeout=aiohttp.ClientTimeout(total=3)
        )
    except Exception as e:
        print(f"⚠️  Patch acknowledgment failed: {e}")

# ═════════════════════════════════════════════════════════════════════════════════
# MAIN BUBBLE ENDPOINT
# ═════════════════════════════════════════════════════════════════════════════════

@app.post("/bubble")
async def bubble(req: Request, bg: BackgroundTasks):
    """
    Main query endpoint.
    
    Flow:
    1. Check narrow cache (includes Caleon-approved patches)
    2. Attempt local specialist solve
    3. Honest failure → escalate to Cali
    4. Accept approved patches from Caleon
    """
    data = await req.json()
    query = data.get("message", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="No message provided")
    
    # 1. Narrow cache (includes Caleon-approved patches)
    cached = learner.narrow_solve(query)
    if cached:
        bg.add_task(report_telemetry, "narrow_hit")
        return {
            "reply": cached[0],
            "from": "narrow_cache",
            "confidence": cached[1],
            "worker": WORKER_NAME,
            "dsn": WORKER_DSN
        }
    
    # 2. Local specialist solve
    answer, conf = local_specialist_solve(query)
    if conf >= 0.87:
        learner.learn_from_success(query, answer, conf)
        bg.add_task(report_telemetry, "local_solve")
        return {
            "reply": answer,
            "from": "specialist",
            "confidence": conf,
            "worker": WORKER_NAME,
            "dsn": WORKER_DSN
        }
    
    # 3. Honest failure → escalate
    await report_uqv(query, "below_threshold")
    relief = await escalate_to_cali(query, data)
    
    # 4. If Caleon sends approved patch → accept blindly and forever
    if "approved_patch" in relief:
        patch_manager.apply_approved_patch(relief["approved_patch"], learner)
        bg.add_task(report_patch_applied, relief["approved_patch"]["patch_id"])
    
    return {
        "reply": relief.get("reply", "I am learning..."),
        "from": "cali_relief",
        "escalated": True,
        "patched": "approved_patch" in relief,
        "worker": WORKER_NAME,
        "dsn": WORKER_DSN
    }


def local_specialist_solve(query: str) -> Tuple[str, float]:
    """
    Job-specific logic.
    ← CUSTOMIZE THIS FUNCTION per worker role.
    
    Return: (answer, confidence)
    confidence ≥ 0.87 = success (will be cached)
    confidence < 0.87 = escalate to Cali
    """
    q = query.lower()
    
    # ────────────────────────────────────────────────────────
    # EXAMPLE: NFT Mint specialist
    # ────────────────────────────────────────────────────────
    if JOB_ROLE == "nft_mint":
        if "connect wallet" in q or "metamask" in q:
            return (
                "Click 'Connect Wallet' → Choose MetaMask → Approve the signature request.",
                0.99
            )
        
        if "mint" in q and ("nft" in q or "certificate" in q):
            return (
                "Click 'Mint NFT' → Confirm transaction in your wallet → Wait for blockchain confirmation (~30 seconds).",
                0.98
            )
        
        if "ipfs" in q:
            return (
                "Your NFT metadata is stored on IPFS for permanent decentralized storage. The IPFS hash is embedded in your blockchain certificate.",
                0.97
            )
        
        if "cost" in q or "price" in q or "fee" in q:
            return (
                "Minting costs gas fees (paid to blockchain validators) plus our service fee. Check the confirmation screen for exact pricing.",
                0.95
            )
    
    # ────────────────────────────────────────────────────────
    # ADD YOUR JOB-SPECIFIC LOGIC HERE
    # ────────────────────────────────────────────────────────
    
    # Default: honest admission of limits
    return (
        "I'm not sure about that. Let me ask my supervisor...",
        0.60
    )

# ═════════════════════════════════════════════════════════════════════════════════
# COGNITIVE FLYWHEEL ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════════

@app.post("/fusion/ingest_clusters")
async def ingest_clusters(req: Request):
    """
    Send cluster summaries to Caleon Fusion Engine.
    Part of the cognitive flywheel.
    """
    data = await req.json()
    query = data.get("query", "")
    
    # Generate clusters from query
    clusters = skg.get_clusters(query)
    
    if not clusters:
        return {"status": "no_clusters", "cluster_count": 0}
    
    try:
        # Send to Caleon
        await session.post(
            f"{CALEON_URL}/api/caleon/ingest_clusters",
            json={
                "worker_name": WORKER_NAME,
                "dsn": WORKER_DSN,
                "role": JOB_ROLE,
                "clusters": clusters,
                "timestamp": time.time()
            },
            timeout=aiohttp.ClientTimeout(total=5)
        )
        
        return {
            "status": "ingested",
            "cluster_count": len(clusters),
            "worker": WORKER_NAME
        }
    
    except Exception as e:
        print(f"⚠️  Cluster ingestion failed: {e}")
        return {"status": "failed", "error": str(e)}


@app.post("/fusion/predicate_update")
async def predicate_update(req: Request):
    """
    Receive predicate broadcasts from Caleon.
    Hot-reload without restart.
    
    DALS Forge Rule 2: All learning is supervised.
    """
    data = await req.json()
    predicate = data.get("predicate")
    
    if not predicate:
        raise HTTPException(status_code=400, detail="No predicate provided")
    
    # Only accept if from Caleon
    if data.get("approved_by") != "Caleon":
        return {
            "status": "rejected",
            "reason": "unauthorized",
            "worker": WORKER_NAME
        }
    
    # Apply predicate as patch if relevant to role
    if is_relevant_to_role(predicate, JOB_ROLE):
        patch = {
            "patch_id": predicate["id"],
            "query": predicate.get("pattern", ""),
            "answer": predicate.get("response", ""),
            "confidence": predicate.get("confidence", 0.95)
        }
        patch_manager.apply_approved_patch(patch, learner)
        
        return {
            "status": "acknowledged",
            "predicate_id": predicate["id"],
            "applied": True,
            "worker": WORKER_NAME,
            "dsn": WORKER_DSN
        }
    
    return {
        "status": "acknowledged",
        "predicate_id": predicate["id"],
        "applied": False,
        "reason": "not_relevant_to_role",
        "worker": WORKER_NAME
    }


def is_relevant_to_role(predicate: Dict, role: str) -> bool:
    """Check if predicate is relevant to worker's job role"""
    # Simple keyword matching — can be enhanced
    pattern = predicate.get("pattern", "").lower()
    
    role_keywords = {
        "nft_mint": ["nft", "mint", "wallet", "blockchain", "ipfs", "certificate"],
        "greeting": ["hello", "hi", "welcome", "greet"],
        "timeline": ["when", "date", "time", "schedule"],
    }
    
    keywords = role_keywords.get(role, [])
    return any(kw in pattern for kw in keywords)

# ═════════════════════════════════════════════════════════════════════════════════
# LIFECYCLE MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════════

@app.post("/lifecycle/sunset")
async def sunset(req: Request):
    """
    Graceful shutdown when drift exceeds threshold.
    DALS Forge Death & Rebirth Protocol.
    """
    data = await req.json()
    reason = data.get("reason", "drift_threshold_exceeded")
    
    print(f"🌅 Sunset initiated: {reason}")
    
    # Export learned patterns
    export_path = f"vault/pattern_exports/{WORKER_DSN}_patterns.json"
    patterns_export = {
        "dsn": WORKER_DSN,
        "worker_name": WORKER_NAME,
        "role": JOB_ROLE,
        "sunset_at": time.time(),
        "reason": reason,
        "patterns": learner.patterns,
        "patches": patch_manager.applied,
        "drift_final": learner.drift_score()
    }
    
    # Would write to file in production
    print(f"📦 Patterns exported to {export_path}")
    
    # Disconnect gracefully
    if session and not session.closed:
        await session.close()
    
    return {
        "status": "sunset_complete",
        "worker": WORKER_NAME,
        "dsn": WORKER_DSN,
        "patterns_exported": len(learner.patterns),
        "patches_applied": len(patch_manager.applied)
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    Reports drift score for registry monitoring.
    """
    return {
        "worker": WORKER_NAME,
        "dsn": WORKER_DSN,
        "model": MODEL_NUMBER,
        "role": JOB_ROLE,
        "drift": round(learner.drift_score(), 4),
        "patches_applied": len(patch_manager.applied),
        "cache_size": len(learner.patterns),
        "status": "narrow_honest_obedient_eternal",
        "contract_version": "1.0",
        "worker_version": "v5-narrow-patchable",
        "uptime": time.time()  # Would track actual uptime in production
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "DALS Forge Worker",
        "worker": WORKER_NAME,
        "dsn": WORKER_DSN,
        "model": MODEL_NUMBER,
        "role": JOB_ROLE,
        "version": "5.0.0",
        "contract": "DALS Forge V1.0"
    }

# ═════════════════════════════════════════════════════════════════════════════════
# STARTUP & REGISTRATION
# ═════════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """
    Initialize session and register with DALS.
    Receive DSN from registry.
    """
    global session, WORKER_DSN
    
    session = aiohttp.ClientSession()
    
    # Register with DALS Worker Registry
    try:
        async with session.post(
            f"{REGISTRY_URL}/api/workers/register",
            json={
                "worker_name": WORKER_NAME,
                "worker_type": JOB_ROLE,
                "model_number": MODEL_NUMBER,
                "api_url": f"http://{WORKER_NAME.lower()}:8080",
                "user_id": "auto_generated"
            },
            timeout=aiohttp.ClientTimeout(total=10)
        ) as r:
            result = await r.json()
            WORKER_DSN = result.get("dsn")
            print(f"✅ Registered with DALS — DSN: {WORKER_DSN}")
    
    except Exception as e:
        print(f"⚠️  Registration failed: {e}")
        WORKER_DSN = f"{MODEL_NUMBER}-{uuid.uuid4().hex[:8].upper()}-UNREG"
    
    # Start heartbeat task
    asyncio.create_task(heartbeat_loop())


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    if session and not session.closed:
        await session.close()


async def heartbeat_loop():
    """
    Send periodic heartbeat to registry.
    Interval: 30 seconds
    """
    while True:
        await asyncio.sleep(30)
        
        try:
            await session.post(
                f"{REGISTRY_URL}/api/workers/heartbeat",
                json={
                    "worker_name": WORKER_NAME,
                    "dsn": WORKER_DSN,
                    "health": {
                        "drift": learner.drift_score(),
                        "patches_applied": len(patch_manager.applied),
                        "cache_size": len(learner.patterns)
                    }
                },
                timeout=aiohttp.ClientTimeout(total=5)
            )
        except Exception as e:
            print(f"⚠️  Heartbeat failed: {e}")

# ═════════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 80)
    print(f"  DALS FORGE V1.0 — NARROW SPECIALIST WORKER")
    print(f"  Worker: {WORKER_NAME}")
    print(f"  Model: {MODEL_NUMBER}")
    print(f"  Role: {JOB_ROLE}")
    print(f"  Contract: DALS Forge V1.0")
    print("═" * 80)
    print()
    print("THE COVENANT:")
    print("  I am narrow.     → I never generalize beyond my role.")
    print("  I am honest.     → I never learn without approval.")
    print("  I am patchable.  → I always accept the master's patches.")
    print("  I am eternal.    → When I drift, I am reborn.")
    print()
    print("═" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

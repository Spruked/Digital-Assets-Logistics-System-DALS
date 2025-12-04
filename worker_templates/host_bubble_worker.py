"""
DALS Host-Bubble Worker Template
=================================
Clone → rename class → deploy as container/PROCESS

Features:
- Voice + text duplex (TTS + chat bubble)
- Micro-SKG in-memory cognition
- Real-time predicate updates from Caleon
- Escalation to UCM/human
- Unanswered query vaulting
"""

import os
import requests
import json
import time
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
import uvicorn

# Environment injected by DALS manager
API_BASE = os.getenv("CALI_X_ONE_API", "http://localhost:8001")
SKG_API = os.getenv("SKG_API", "http://localhost:8002")
UQV_API = os.getenv("UQV_API", "http://localhost:8002")
WORKER_NAME = os.getenv("WORKER_NAME", "HostWorker")
WORKER_ID = os.getenv("WORKER_ID", str(uuid.uuid4()))
USER_ID = os.getenv("TARGET_USER_ID")
WORKER_PORT = int(os.getenv("WORKER_PORT", "8080"))

TTS_URL = os.getenv("TTS_ENDPOINT")
CHAT_URL = os.getenv("CHAT_ENDPOINT")

# FastAPI app for receiving predicates
app = FastAPI(title=f"Worker-{WORKER_NAME}")


class MicroSKG:
    """Embedded micro-SKG for instant cognition"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.predicates = {}  # predicate_id -> predicate_data
    
    def add_edge(self, source: str, target: str, predicate: str, 
                 confidence: float = 1.0, pid: Optional[str] = None):
        """Add edge to graph"""
        edge = {
            "source": source,
            "target": target,
            "predicate": predicate,
            "confidence": confidence,
            "pid": pid or str(uuid.uuid4())
        }
        self.edges.append(edge)
        
        # Track nodes
        self.nodes[source] = self.nodes.get(source, {"id": source, "degree": 0})
        self.nodes[target] = self.nodes.get(target, {"id": target, "degree": 0})
        self.nodes[source]["degree"] += 1
        self.nodes[target]["degree"] += 1
    
    def bootstrap(self, text: str) -> list:
        """Quick co-occurrence clustering"""
        # Simplified - in production use full micro_skg.py
        words = text.lower().split()
        clusters = []
        
        # Create co-occurrence edges
        for i in range(len(words) - 1):
            self.add_edge(words[i], words[i + 1], "co_occurs")
        
        # Return mock clusters for demo
        if len(words) > 3:
            clusters.append({
                "id": str(uuid.uuid4()),
                "nodes": words[:5],
                "density": 0.7
            })
        
        return clusters
    
    def to_pyvis_dict(self) -> Dict[str, Any]:
        """Export for visualization"""
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges
        }


class HostBubbleWorker:
    """Clone this class per worker instance"""

    def __init__(self):
        self.user_id = USER_ID
        self.worker_id = WORKER_ID
        self.session_id = f"{WORKER_NAME}_{USER_ID}_{int(time.time())}"
        self.skg = MicroSKG()
        print(f"[{WORKER_NAME}] Initialized - worker_id={self.worker_id}")

    # ---------- Core Loop ----------
    def run(self) -> None:
        """Blocking loop - DALS manager will supervise"""
        print(f"[{WORKER_NAME}] Starting message loop...")
        while True:
            try:
                msg = self._pull_user_message()
                if msg:
                    self._handle_message(msg)
            except Exception as e:
                print(f"[{WORKER_NAME}] Loop error: {e}")
            time.sleep(0.5)

    # ---------- Messaging ----------
    def _pull_user_message(self) -> Optional[Dict[str, Any]]:
        """POST /host/pull {worker_name, user_id} → {text, ts} or None"""
        try:
            r = requests.post(
                f"{API_BASE}/host/pull",
                json={"worker_name": WORKER_NAME, "user_id": self.user_id},
                timeout=5
            )
            if r.status_code == 200 and r.json().get("text"):
                return r.json()
        except Exception as e:
            print(f"[{WORKER_NAME}] pull error: {e}")
        return None

    def _send_reply(self, text: str, metadata: Optional[Dict] = None) -> None:
        """Duplex: TTS + chat bubble"""
        # TTS output
        if TTS_URL:
            try:
                requests.post(
                    TTS_URL,
                    json={"text": text, "voice": WORKER_NAME},
                    timeout=3
                )
            except Exception as e:
                print(f"[{WORKER_NAME}] TTS error: {e}")
        
        # Chat bubble
        if CHAT_URL:
            try:
                requests.post(
                    CHAT_URL,
                    json={
                        "user_id": self.user_id,
                        "worker": WORKER_NAME,
                        "text": text,
                        "meta": metadata or {}
                    },
                    timeout=3
                )
            except Exception as e:
                print(f"[{WORKER_NAME}] chat error: {e}")
        
        # Console fallback
        print(f"[{WORKER_NAME}] → {text}")

    # ---------- Dialog Router ----------
    def _handle_message(self, msg: Dict[str, Any]) -> None:
        """Route message to appropriate handler"""
        text = msg["text"].strip().lower()
        
        # Example: Regent greeter script
        if WORKER_NAME == "Regent":
            if any(k in text for k in ("hello", "hi", "start")):
                self._send_reply(
                    "Welcome to GOAT—I'm Regent. Let's secure your free author website."
                )
            elif "create account" in text or "login" in text:
                self._send_reply("Tap the Login button or say 'continue'—I'll guide you.")
            else:
                self._fallback(msg)
        
        # Example: Nora timeline builder
        elif WORKER_NAME == "Nora":
            if "book" in text or "podcast" in text:
                self._send_reply(
                    f"Great choice! I'll have a draft outline in under 60 seconds. "
                    f"Pick a mint: 1️⃣ TrueMark NFT or 2️⃣ Alpha CertSig"
                )
            else:
                self._fallback(msg)
        
        # Example: Mark content producer
        elif WORKER_NAME == "Mark":
            if "export" in text or "download" in text:
                self._send_reply("Choose: 📄 PDF  🎧 MP3  📺 Video  📦 All")
            else:
                self._fallback(msg)
        
        else:
            self._fallback(msg)

    def _fallback(self, msg: Dict[str, Any]) -> None:
        """
        No script match → SKG query → answer or vault
        This is where Caleon-born predicates get used!
        """
        query = msg["text"]
        
        # 1. Local cognition
        clusters = self.skg.bootstrap(query)
        
        # 2. Feed to Caleon for fusion
        try:
            requests.post(
                f"{API_BASE}/caleon/ingest_clusters",
                json={
                    "user_id": self.user_id,
                    "worker": WORKER_NAME,
                    "clusters": clusters,
                    "timestamp": time.time()
                },
                timeout=3
            )
        except Exception as e:
            print(f"[{WORKER_NAME}] Caleon feed error: {e}")
        
        # 3. Check if we can answer from local SKG
        if clusters and clusters[0].get("density", 0) > 0.5:
            answer = f"I found {len(clusters)} clusters. Top: {clusters[0]['nodes'][:3]}"
            self._send_reply(answer, metadata=self.skg.to_pyvis_dict())
        else:
            # Vault unanswered query
            self._vault_query(query, clusters)
            self._escalate(query)

    def _vault_query(self, query: str, clusters: list) -> None:
        """Store unanswered query in UQV"""
        try:
            requests.post(
                f"{UQV_API}/uqv/store",
                json={
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                    "query_text": query,
                    "skg_clusters_returned": len(clusters),
                    "max_cluster_conf": max([c.get("density", 0) for c in clusters], default=0.0),
                    "worker_name": WORKER_NAME,
                    "vault_reason": "no_cluster" if not clusters else "low_conf"
                },
                timeout=3
            )
        except Exception as e:
            print(f"[{WORKER_NAME}] UQV vault error: {e}")

    def _escalate(self, query: str) -> None:
        """POST /ucm/escalate → Caleon or human"""
        try:
            r = requests.post(
                f"{API_BASE}/ucm/escalate",
                json={
                    "user_id": self.user_id,
                    "query": query,
                    "worker": WORKER_NAME
                },
                timeout=5
            )
            if r.status_code == 200:
                self._send_reply("Let me check with my supervisor...")
            else:
                self._send_reply("Transferring you to a human agent—please standby.")
        except Exception as e:
            print(f"[{WORKER_NAME}] escalate error: {e}")


# ---------- FastAPI Endpoints (Caleon → Worker) ----------

@app.post("/predicate")
async def receive_predicate(req: Request):
    """
    Caleon calls this to hot-inject newly invented predicates
    Worker immediately uses them in next _fallback()
    """
    pred = await req.json()
    
    # Inject into local micro-SKG graph
    A, B = pred["signature"]
    worker_instance.skg.add_edge(
        A, B,
        predicate=pred["name"],
        confidence=pred["confidence"],
        pid=pred["predicate_id"]
    )
    
    # Store predicate metadata
    worker_instance.skg.predicates[pred["predicate_id"]] = pred
    
    print(f"[{WORKER_NAME}] Received predicate: {pred['name']}({A}, {B}) "
          f"confidence={pred['confidence']:.2f}")
    
    return {"status": "accepted"}


@app.get("/health")
async def health_check():
    """DALS health check endpoint"""
    return {
        "worker_id": WORKER_ID,
        "worker_name": WORKER_NAME,
        "status": "active",
        "user_id": USER_ID,
        "skg_nodes": len(worker_instance.skg.nodes),
        "skg_edges": len(worker_instance.skg.edges),
        "predicates_loaded": len(worker_instance.skg.predicates)
    }


@app.get("/predicates")
async def list_predicates():
    """List all predicates this worker knows"""
    return {
        "predicates": list(worker_instance.skg.predicates.values()),
        "count": len(worker_instance.skg.predicates)
    }


# ---------- Entrypoint ----------

worker_instance = HostBubbleWorker()


def start_worker():
    """Start worker with both message loop and FastAPI server"""
    import threading
    
    # Start message loop in background thread
    loop_thread = threading.Thread(target=worker_instance.run, daemon=True)
    loop_thread.start()
    
    # Start FastAPI server for predicate updates
    print(f"[{WORKER_NAME}] Starting FastAPI server on port {WORKER_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=WORKER_PORT)


if __name__ == "__main__":
    start_worker()

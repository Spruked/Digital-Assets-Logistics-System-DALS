"""
UQV Collector - Lightweight helper for vaulting unanswered queries
~15 lines of production code
"""
import requests
import json
import os

UQV_API = os.getenv("UQV_API", "http://localhost:8003/api/uqv")

def vault_query(user_id, session_id, query_text,
                clusters_found=0, max_conf=0.0,
                worker="unknown", reason="no_cluster"):
    """
    Store an unanswered query for later SKG training.
    Fire-and-forget - failures are logged but don't block worker.
    """
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "query_text": query_text,
        "skg_clusters_returned": clusters_found,
        "max_cluster_conf": max_conf,
        "worker_name": worker,
        "vault_reason": reason
    }
    try:
        requests.post(f"{UQV_API}/store", json=payload, timeout=3)
    except Exception as e:
        print(f"[UQV] vault failed: {e}")

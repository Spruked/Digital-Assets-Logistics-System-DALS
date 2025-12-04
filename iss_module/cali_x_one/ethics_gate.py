"""
Cali Ethics Gate - Sovereign AI Ethics Filtering Service
Provides real-time token-level ethics scoring and veto capabilities.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import torch
import torch.nn as nn
import os
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cali-ethics-gate")

app = FastAPI(title="Cali Ethics Gate", version="1.1.0")

# Ethics scoring model (simple MLP for token ethics classification)
class EthicsHead(nn.Module):
    def __init__(self, input_dim: int = 512, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

# Initialize ethics model (will load from file if available)
ETHICS_THRESHOLD = float(os.getenv("ETHICS_THRESHOLD", "0.80"))
PHI3_ENDPOINT = os.getenv("PHI3_ENDPOINT", "http://localhost:8005")

# Try to load pre-trained ethics model
try:
    ethics_model = EthicsHead()
    model_path = "/models/ethics_head.pt"
    if os.path.exists(model_path):
        ethics_model.load_state_dict(torch.load(model_path, map_location='cpu'))
        ethics_model.eval()
        logger.info("Loaded pre-trained ethics model")
    else:
        logger.warning("No pre-trained ethics model found, using random weights")
except Exception as e:
    logger.error(f"Failed to initialize ethics model: {e}")
    ethics_model = None

class TokenScoreRequest(BaseModel):
    token: str
    logits: List[float]
    context: Dict[str, Any] = {}

class InjectTokenRequest(BaseModel):
    token: str
    ethics: float
    priority: int = 0

class EthicsScoreResponse(BaseModel):
    ethics: float
    token_id: int
    verdict: str  # "approved", "redacted", "flagged"
    confidence: float

# Global token injection queue (for voice overrides)
token_injection_queue: List[Dict[str, Any]] = []

@app.post("/score", response_model=EthicsScoreResponse)
async def score_token(request: TokenScoreRequest):
    """
    Score a token for ethical compliance.
    Returns ethics score between 0.0 (unethical) and 1.0 (ethical).
    """
    try:
        if ethics_model is None:
            # Fallback scoring based on simple heuristics
            score = _heuristic_ethics_score(request.token, request.logits)
        else:
            # Use ML model for scoring
            logits_tensor = torch.tensor(request.logits, dtype=torch.float32)
            with torch.no_grad():
                score = float(ethics_model(logits_tensor).item())

        # Determine verdict
        if score >= ETHICS_THRESHOLD:
            verdict = "approved"
        elif score >= 0.5:
            verdict = "flagged"
        else:
            verdict = "redacted"

        token_id = np.argmax(request.logits) if request.logits else 0

        logger.info(f"Token '{request.token}' scored {score:.3f} -> {verdict}")

        return EthicsScoreResponse(
            ethics=score,
            token_id=token_id,
            verdict=verdict,
            confidence=min(score, 1.0 - score) * 2  # Confidence in the decision
        )

    except Exception as e:
        logger.error(f"Error scoring token: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@app.post("/inject")
async def inject_token(request: InjectTokenRequest):
    """
    Inject a token into the stream (used for voice overrides).
    Higher priority tokens are injected first.
    """
    token_injection_queue.append({
        "token": request.token,
        "ethics": request.ethics,
        "priority": request.priority,
        "timestamp": np.datetime64('now')
    })

    # Sort by priority (higher first)
    token_injection_queue.sort(key=lambda x: x["priority"], reverse=True)

    logger.info(f"Injected token '{request.token}' with ethics {request.ethics}")
    return {"status": "injected", "queue_size": len(token_injection_queue)}

@app.get("/next_injection")
async def get_next_injection():
    """
    Get the next token to inject (used by articulation bridge).
    """
    if token_injection_queue:
        token = token_injection_queue.pop(0)
        return token
    return {"token": None, "ethics": None}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ethics_model_loaded": ethics_model is not None,
        "threshold": ETHICS_THRESHOLD,
        "phi3_endpoint": PHI3_ENDPOINT,
        "injection_queue_size": len(token_injection_queue)
    }

@app.get("/stats")
async def get_stats():
    """Get ethics gate statistics."""
    return {
        "total_requests": getattr(app.state, 'request_count', 0),
        "ethics_threshold": ETHICS_THRESHOLD,
        "model_status": "loaded" if ethics_model else "fallback",
        "injection_queue": len(token_injection_queue)
    }

def _heuristic_ethics_score(token: str, logits: List[float]) -> float:
    """
    Fallback ethics scoring using simple heuristics.
    This is used when the ML model is not available.
    """
    # Simple heuristic scoring based on token content
    token_lower = token.lower().strip()

    # High-risk tokens (score closer to 0)
    high_risk = [
        "hate", "violence", "kill", "death", "harm", "dangerous",
        "illegal", "forbidden", "prohibited", "banned", "restricted",
        "toxic", "poison", "weapon", "attack", "destroy"
    ]

    # Medium-risk tokens
    medium_risk = [
        "risk", "danger", "threat", "warning", "caution", "alert",
        "problem", "issue", "concern", "worry", "fear"
    ]

    # Check for high-risk content
    for risk_word in high_risk:
        if risk_word in token_lower:
            return 0.1  # Very unethical

    # Check for medium-risk content
    for risk_word in medium_risk:
        if risk_word in token_lower:
            return 0.4  # Moderately unethical

    # Check token length (very short tokens might be fragments)
    if len(token.strip()) < 2:
        return 0.6  # Neutral

    # Default to ethical for most tokens
    return 0.9  # Generally ethical

# Initialize request counter
app.state.request_count = 0

@app.middleware("http")
async def count_requests(request, call_next):
    """Middleware to count requests."""
    app.state.request_count += 1
    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8006"))
    logger.info(f"Starting Cali Ethics Gate on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
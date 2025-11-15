"""Voice Communication Portal proxy that delegates all processing to UCM."""

import logging
import os
from typing import Dict, Iterable, Optional, Tuple

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from ..config import settings


logger = logging.getLogger("DALS.VoiceProxy")

voice_router = APIRouter(prefix="/voice", tags=["Voice Communication Portal"])


DEFAULT_UCM_VOICE_BASE = "http://localhost:8080/api/voice"
VOICE_PROXY_TIMEOUT = float(os.getenv("UCM_VOICE_TIMEOUT", "15"))

FORWARDED_HEADERS = {
    "authorization",
    "x-request-id",
    "x-correlation-id",
    "x-trace-id",
    "cookie",
    "accept",
    "accept-language",
}
FORWARDED_HEADER_PREFIXES = ("x-dals-", "x-ucm-")
RESPONSE_HEADER_WHITELIST = {
    "content-disposition",
    "cache-control",
    "pragma",
    "x-request-id",
    "x-correlation-id",
    "x-trace-id",
}


def _resolve_voice_base_url() -> str:
    """Determine the UCM voice base URL."""
    env_url = os.getenv("UCM_VOICE_BASE_URL")
    if env_url:
        return env_url.rstrip("/")
    if settings.cochlear_processor_url:
        return settings.cochlear_processor_url.rstrip("/")
    return DEFAULT_UCM_VOICE_BASE


UCM_VOICE_BASE_URL = _resolve_voice_base_url()


def _extract_forward_headers(request: Request) -> Dict[str, str]:
    """Select headers that should be forwarded to UCM."""
    forwarded: Dict[str, str] = {}
    for key, value in request.headers.items():
        key_lower = key.lower()
        if key_lower in FORWARDED_HEADERS or any(
            key_lower.startswith(prefix) for prefix in FORWARDED_HEADER_PREFIXES
        ):
            forwarded[key] = value
    return forwarded


async def _ucm_request(
    method: str,
    path: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Iterable[Tuple[str, str]]] = None,
    content: Optional[bytes] = None,
) -> httpx.Response:
    """Send an HTTP request to the UCM voice service."""
    url = f"{UCM_VOICE_BASE_URL.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=VOICE_PROXY_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                content=content,
            )
            return response
    except httpx.RequestError as exc:
        logger.error(
            "Failed to reach UCM voice service",
            extra={"path": path, "method": method, "error": str(exc)},
        )
        raise HTTPException(status_code=503, detail="UCM voice service unreachable")


def _build_proxy_response(response: httpx.Response) -> Response:
    """Translate an httpx.Response into a FastAPI Response."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type.lower():
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}
        return JSONResponse(status_code=response.status_code, content=payload)

    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() in RESPONSE_HEADER_WHITELIST
    }
    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=content_type or None,
        headers=headers or None,
    )


async def _forward_request(request: Request, method: str, path: str) -> Response:
    """Forward the incoming request to UCM and replay the response back to the caller."""
    params = list(request.query_params.multi_items())
    headers = _extract_forward_headers(request)
    body: Optional[bytes] = None

    if method in {"POST", "PUT", "PATCH"}:
        body = await request.body()
        content_type = request.headers.get("content-type")
        if content_type:
            headers["Content-Type"] = content_type

    logger.debug("Forwarding voice request", extra={"path": path, "method": method})

    response = await _ucm_request(
        method,
        path,
        headers=headers or None,
        params=params or None,
        content=body if body else None,
    )
    return _build_proxy_response(response)


@voice_router.get("/status")
async def voice_status(request: Request) -> Response:
    """Get voice subsystem status - DALS-001 compliant (real data or zeros)."""
    return await _forward_request(request, "GET", "/status")


@voice_router.post("/session/create")
async def create_voice_session(request: Request) -> Response:
    """Create a new voice session via UCM."""
    return await _forward_request(request, "POST", "/session/create")


@voice_router.get("/session/{session_id}/status")
async def voice_session_status(request: Request, session_id: str) -> Response:
    """Retrieve voice session status from UCM."""
    return await _forward_request(request, "GET", f"/session/{session_id}/status")


@voice_router.delete("/session/{session_id}")
async def end_voice_session(request: Request, session_id: str) -> Response:
    """End a voice session via UCM."""
    return await _forward_request(request, "DELETE", f"/session/{session_id}")


@voice_router.post("/stt")
async def speech_to_text(request: Request) -> Response:
    """Delegate speech-to-text processing to UCM."""
    return await _forward_request(request, "POST", "/stt")


@voice_router.post("/tts")
async def text_to_speech(request: Request) -> Response:
    """Delegate text-to-speech synthesis to UCM."""
    return await _forward_request(request, "POST", "/tts")


logger.info("Voice Communication Portal proxying to %s", UCM_VOICE_BASE_URL)
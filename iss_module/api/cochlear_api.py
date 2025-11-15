"""Cochlear Processor API - Speech Input Processing for UCM."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from ..integrations.ucm_connector import get_ucm_connector
from ..core.utils import get_stardate

logger = logging.getLogger("DALS.CochlearProcessor")

cochlear_router = APIRouter(prefix="/cochlear", tags=["Cochlear Processor"])


class SpeechInput(BaseModel):
    """Speech input for processing."""
    text: Optional[str] = Field(None, description="Transcribed text if already processed")
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class CochlearResponse(BaseModel):
    """Response from cochlear processor."""
    success: bool
    session_id: str
    stardate: float
    transcription: Optional[str] = None
    ucm_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CochlearStatus(BaseModel):
    """Cochlear processor status - DALS-001 compliant."""
    available: bool
    service: str = "cochlear_processor"
    last_activity: Optional[str] = None
    sessions_active: int = 0
    total_processed: int = 0


# Session tracking (in-memory for now)
active_sessions: Dict[str, Dict[str, Any]] = {}
total_processed = 0


@cochlear_router.get("/status", response_model=CochlearStatus)
async def get_cochlear_status() -> CochlearStatus:
    """
    Get cochlear processor status - DALS-001 compliant (real data or zeros).
    
    Returns real session counts and activity, or zeros if no activity.
    """
    global active_sessions, total_processed
    
    last_activity = None
    if active_sessions:
        # Get most recent session timestamp
        last_timestamps = [s.get("last_activity") for s in active_sessions.values() if s.get("last_activity")]
        if last_timestamps:
            last_activity = max(last_timestamps)
    
    return CochlearStatus(
        available=True,
        last_activity=last_activity,
        sessions_active=len(active_sessions),
        total_processed=total_processed
    )


@cochlear_router.post("/session/create")
async def create_cochlear_session(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new cochlear processing session.
    
    Args:
        user_id: Optional user identifier
        
    Returns:
        Session details including session_id
    """
    session_id = f"cochlear_{get_stardate():.4f}"
    
    active_sessions[session_id] = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat(),
        "messages_processed": 0
    }
    
    logger.info(f"Created cochlear session: {session_id}", extra={"user_id": user_id})
    
    return {
        "success": True,
        "session_id": session_id,
        "stardate": get_stardate(),
        "message": "Cochlear session created - ready to process speech"
    }


@cochlear_router.post("/stt/audio", response_model=CochlearResponse)
async def speech_to_text_audio(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, OGG, etc.)"),
    session_id: str = Form(..., description="Session ID"),
    send_to_ucm: bool = Form(True, description="Send transcription to UCM for processing")
) -> CochlearResponse:
    """
    Process audio file through speech-to-text and optionally send to UCM.
    
    Args:
        audio: Audio file upload
        session_id: Active session ID
        send_to_ucm: Whether to forward transcription to UCM
        
    Returns:
        Transcription and optional UCM response
    """
    global total_processed
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Read audio data
        audio_data = await audio.read()
        logger.info(f"Received audio: {len(audio_data)} bytes, type: {audio.content_type}")
        
        # TODO: Implement actual STT processing
        # For now, return placeholder
        transcription = "[Audio transcription would appear here - STT engine needed]"
        
        # Update session
        active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
        active_sessions[session_id]["messages_processed"] += 1
        total_processed += 1
        
        ucm_response = None
        if send_to_ucm and transcription:
            # Send to UCM for reasoning
            try:
                ucm = get_ucm_connector()
                await ucm.connect()
                ucm_response = await ucm.submit_reasoning_request(
                    content=transcription,
                    priority="normal",
                    context={
                        "source": "cochlear_processor",
                        "session_id": session_id,
                        "input_type": "audio"
                    }
                )
            except Exception as ucm_error:
                logger.warning(f"UCM unavailable: {ucm_error}")
                ucm_response = {"error": "UCM offline", "message": str(ucm_error)}
        
        return CochlearResponse(
            success=True,
            session_id=session_id,
            stardate=get_stardate(),
            transcription=transcription,
            ucm_response=ucm_response
        )
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return CochlearResponse(
            success=False,
            session_id=session_id,
            stardate=get_stardate(),
            error=str(e)
        )


@cochlear_router.post("/stt/text", response_model=CochlearResponse)
async def speech_to_text_from_text(speech_input: SpeechInput) -> CochlearResponse:
    """
    Process text input (simulating speech or pre-transcribed text) and send to UCM.
    
    Args:
        speech_input: Speech input data
        
    Returns:
        UCM processing response
    """
    global total_processed
    
    if speech_input.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Update session
        active_sessions[speech_input.session_id]["last_activity"] = datetime.utcnow().isoformat()
        active_sessions[speech_input.session_id]["messages_processed"] += 1
        total_processed += 1
        
        # Send to UCM
        ucm = get_ucm_connector()
        await ucm.connect()
        ucm_response = await ucm.submit_reasoning_request(
            content=speech_input.text,
            priority="normal",
            context={
                "source": "cochlear_processor",
                "session_id": speech_input.session_id,
                "user_id": speech_input.user_id,
                "input_type": "text",
                **speech_input.context
            }
        )
        
        return CochlearResponse(
            success=True,
            session_id=speech_input.session_id,
            stardate=get_stardate(),
            transcription=speech_input.text,
            ucm_response=ucm_response
        )
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}")
        return CochlearResponse(
            success=False,
            session_id=speech_input.session_id,
            stardate=get_stardate(),
            error=str(e)
        )


@cochlear_router.delete("/session/{session_id}")
async def end_cochlear_session(session_id: str) -> Dict[str, Any]:
    """
    End a cochlear processing session.
    
    Args:
        session_id: Session to terminate
        
    Returns:
        Session summary
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = active_sessions.pop(session_id)
    
    logger.info(f"Ended cochlear session: {session_id}", extra={
        "messages_processed": session_data["messages_processed"]
    })
    
    return {
        "success": True,
        "session_id": session_id,
        "summary": session_data
    }


logger.info("Cochlear Processor API initialized")

# obs_bridge/models.py
# Pydantic models for OBS Bridge API

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class OBSConnectRequest(BaseModel):
    host: str = "localhost"
    port: int = 4455
    password: Optional[str] = None

class OBSCommandRequest(BaseModel):
    command: str  # e.g., "start_stream", "stop_stream", "switch_scene"
    params: Optional[Dict[str, Any]] = None

class OBSStatusResponse(BaseModel):
    connected: bool
    streaming: bool
    recording: bool
    current_scene: Optional[str] = None
    available_scenes: List[str] = []
    health: str = "unknown"

class OBSResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Platform Profile Models
class PlatformProfile(BaseModel):
    name: str
    platform: str  # "tiktok", "youtube", "facebook", "twitch", "custom"
    rtmp_url: str
    stream_key: Optional[str] = None
    description: Optional[str] = None

class PlatformSelectorRequest(BaseModel):
    platform: str

class PlatformProfilesResponse(BaseModel):
    profiles: List[PlatformProfile]
    current_platform: Optional[str] = None
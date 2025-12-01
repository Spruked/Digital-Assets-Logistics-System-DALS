# obs_bridge/api.py
# FastAPI router for OBS Bridge endpoints

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from .obs_bridge import OBSBridge
from .models import OBSConnectRequest, OBSCommandRequest, OBSStatusResponse, OBSResponse, PlatformProfilesResponse, PlatformSelectorRequest, PlatformProfile

router = APIRouter(prefix="/obs", tags=["OBS Control"])

# Global OBS bridge instance (in production, use dependency injection)
obs_bridge = OBSBridge()

@router.post("/connect", response_model=OBSResponse)
async def connect_to_obs(request: OBSConnectRequest):
    """Connect to OBS WebSocket."""
    obs_bridge.host = request.host
    obs_bridge.port = request.port
    obs_bridge.password = request.password

    success = await obs_bridge.connect()
    if success:
        return OBSResponse(success=True, message="Connected to OBS")
    else:
        raise HTTPException(status_code=500, detail="Failed to connect to OBS")

@router.post("/disconnect", response_model=OBSResponse)
async def disconnect_from_obs():
    """Disconnect from OBS."""
    await obs_bridge.disconnect()
    return OBSResponse(success=True, message="Disconnected from OBS")

@router.post("/start-stream", response_model=OBSResponse)
async def start_stream():
    """Start OBS streaming."""
    success = await obs_bridge.start_stream()
    if success:
        return OBSResponse(success=True, message="Streaming started")
    else:
        raise HTTPException(status_code=500, detail="Failed to start streaming")

@router.post("/stop-stream", response_model=OBSResponse)
async def stop_stream():
    """Stop OBS streaming."""
    success = await obs_bridge.stop_stream()
    if success:
        return OBSResponse(success=True, message="Streaming stopped")
    else:
        raise HTTPException(status_code=500, detail="Failed to stop streaming")

@router.post("/start-recording", response_model=OBSResponse)
async def start_recording():
    """Start OBS recording."""
    success = await obs_bridge.start_recording()
    if success:
        return OBSResponse(success=True, message="Recording started")
    else:
        raise HTTPException(status_code=500, detail="Failed to start recording")

@router.post("/stop-recording", response_model=OBSResponse)
async def stop_recording():
    """Stop OBS recording."""
    success = await obs_bridge.stop_recording()
    if success:
        return OBSResponse(success=True, message="Recording stopped")
    else:
        raise HTTPException(status_code=500, detail="Failed to stop recording")

@router.post("/switch-scene", response_model=OBSResponse)
async def switch_scene(request: OBSCommandRequest):
    """Switch to a specific scene."""
    scene_name = request.params.get("scene_name") if request.params else None
    if not scene_name:
        raise HTTPException(status_code=400, detail="scene_name required in params")

    success = await obs_bridge.switch_scene(scene_name)
    if success:
        return OBSResponse(success=True, message=f"Switched to scene: {scene_name}")
    else:
        raise HTTPException(status_code=500, detail=f"Failed to switch to scene: {scene_name}")

@router.post("/start-service", response_model=OBSResponse)
async def start_obs_service():
    """Start OBS Studio service."""
    success = await obs_bridge.start_obs_service()
    if success:
        return OBSResponse(success=True, message="OBS service started successfully")
    else:
        # Get more detailed error information
        error_msg = "Failed to start OBS service"
        
        if obs_bridge._is_obs_running():
            # OBS is running but we couldn't connect
            error_msg += ": OBS is running but WebSocket connection failed. Please ensure OBS WebSocket plugin is enabled and running on port 4455."
        elif obs_bridge.obs_process:
            if obs_bridge.obs_process.poll() is not None:
                # Process exited, try to get error output
                try:
                    stdout, stderr = obs_bridge.obs_process.communicate(timeout=1)
                    stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
                    stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""
                    if "locale" in stderr_str.lower() or "locale" in stdout_str.lower():
                        error_msg += ": OBS locale files not found. Please ensure OBS Studio is properly installed."
                    elif stderr_str or stdout_str:
                        error_msg += f": {stderr_str.strip() or stdout_str.strip()}"
                except:
                    error_msg += ": OBS process exited unexpectedly"
            else:
                error_msg += ": OBS process started but WebSocket connection failed"
        else:
            error_msg += ": Could not launch OBS process"
        
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/stop-service", response_model=OBSResponse)
async def stop_obs_service():
    """Stop OBS Studio service."""
    success = await obs_bridge.stop_obs_service()
    if success:
        return OBSResponse(success=True, message="OBS service stopped")
    else:
        raise HTTPException(status_code=500, detail="Failed to stop OBS service")

@router.get("/status", response_model=OBSStatusResponse)
async def get_obs_status():
    """Get OBS connection and service status."""
    return OBSStatusResponse(
        connected=obs_bridge.connected,
        host=obs_bridge.host,
        port=obs_bridge.port,
        current_scene=obs_bridge.current_scene,
        available_scenes=obs_bridge.available_scenes,
        streaming=obs_bridge.ws is not None and obs_bridge.connected,
        recording=False  # TODO: implement recording status check
    )

# Platform Profile Endpoints
@router.get("/platforms", response_model=PlatformProfilesResponse)
async def get_platform_profiles():
    """Get all available platform profiles."""
    profiles = []
    for key, profile in obs_bridge.platform_profiles.items():
        profiles.append(PlatformProfile(**profile))
    
    return PlatformProfilesResponse(
        profiles=profiles,
        current_platform=obs_bridge.current_platform
    )

@router.post("/set-platform", response_model=OBSResponse)
async def set_platform_profile(request: PlatformSelectorRequest):
    """Set OBS stream settings for the selected platform."""
    success = await obs_bridge.set_platform_profile(request.platform)
    if success:
        return OBSResponse(
            success=True, 
            message=f"Platform set to {request.platform}",
            data={"platform": request.platform}
        )
    else:
        raise HTTPException(status_code=500, detail=f"Failed to set platform to {request.platform}")

@router.post("/set-platform-with-key", response_model=OBSResponse)
async def set_platform_with_stream_key(platform: str, stream_key: str):
    """Set platform profile with custom stream key."""
    success = await obs_bridge.set_platform_profile(platform, stream_key)
    if success:
        return OBSResponse(
            success=True,
            message=f"Platform {platform} configured with stream key",
            data={"platform": platform, "has_stream_key": bool(stream_key)}
        )
    else:
        raise HTTPException(status_code=500, detail=f"Failed to configure platform {platform}")
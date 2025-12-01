# obs_bridge/__init__.py
# OBS Bridge Module for DALS
# Controls OBS Studio via WebSocket API

from .obs_bridge import OBSBridge
from .api import router as obs_router

__all__ = ["OBSBridge", "obs_router"]
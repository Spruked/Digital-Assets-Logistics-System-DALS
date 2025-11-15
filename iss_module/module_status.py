"""
DALS Module Status Manager
Provides comprehensive visibility into all system modules without faking data
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("DALS.ModuleStatus")

@dataclass
class ModuleStatus:
    """Status information for a DALS module"""
    name: str
    status: str  # "active", "idle", "disabled", "error"
    version: str
    last_heartbeat: str
    uptime_seconds: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    error_message: Optional[str] = None
    data_points_processed: int = 0
    last_activity: Optional[str] = None

class ModuleStatusManager:
    """Manages status reporting for all DALS modules"""
    
    def __init__(self):
        self.modules: Dict[str, ModuleStatus] = {}
        self.system_start_time = time.time()
        self.last_update = None
        
        # Initialize core modules
        self._initialize_core_modules()
    
    def _initialize_core_modules(self):
        """Initialize status for core DALS modules"""
        core_modules = [
            {
                "name": "ISS_Chronometer",
                "version": "1.0.0",
                "status": "active",
                "description": "Interplanetary Stardate Synchronizer"
            },
            {
                "name": "CertSig_Alpha_Mint",
                "version": "1.4.0", 
                "status": "idle",
                "description": "Alpha NFT Minting Engine"
            },
            {
                "name": "Caleon_AI_Core",
                "version": "2.0.0",
                "status": "idle", 
                "description": "Cognitive Reasoning Engine"
            },
            {
                "name": "UCM_Integration",
                "version": "1.2.0",
                "status": "active",
                "description": "Prime Ecosystem Integration"
            },
            {
                "name": "DALS_API_Gateway",
                "version": "1.0.0",
                "status": "active",
                "description": "Main API and Dashboard Server"
            },
            {
                "name": "Telemetry_Engine",
                "version": "1.0.0",
                "status": "active",
                "description": "Phase 1 Telemetry Collection"
            },
            {
                "name": "WebSocket_Broker",
                "version": "1.0.0", 
                "status": "active",
                "description": "Real-time Data Streaming"
            },
            {
                "name": "Simulation_Engine",
                "version": "1.0.0",
                "status": "idle",
                "description": "Activity Generation for Testing"
            },
            {
                "name": "Vault_Manager",
                "version": "1.0.0",
                "status": "idle", 
                "description": "Signature and Asset Vault"
            },
            {
                "name": "Inventory_Manager",
                "version": "1.0.0",
                "status": "idle",
                "description": "Digital Asset Tracking"
            },
            {
                "name": "feedback_cochlear_monitor",
                "version": "1.0.0",
                "status": "idle",
                "description": "Speech Drift Detection and Harmonizer Feedback"
            }
        ]
        
        for module_info in core_modules:
            self.register_module(
                name=module_info["name"],
                version=module_info["version"],
                status=module_info["status"]
            )
    
    def register_module(self, name: str, version: str, status: str = "idle") -> None:
        """Register a new module or update existing one"""
        now = datetime.utcnow().isoformat() + "Z"
        
        if name in self.modules:
            # Update existing module
            module = self.modules[name]
            module.status = status
            module.last_heartbeat = now
            module.version = version
        else:
            # Create new module
            self.modules[name] = ModuleStatus(
                name=name,
                status=status,
                version=version,
                last_heartbeat=now,
                uptime_seconds=time.time() - self.system_start_time
            )
        
        logger.info(f"Module registered: {name} v{version} - {status}")
    
    def update_module_activity(self, name: str, activity_description: str, data_points: int = 1) -> None:
        """Update module activity without changing core status"""
        if name in self.modules:
            module = self.modules[name]
            module.last_activity = activity_description
            module.data_points_processed += data_points
            module.last_heartbeat = datetime.utcnow().isoformat() + "Z"
            
            # Only change to active if it was idle (not if disabled/error)
            if module.status == "idle":
                module.status = "active"
    
    def set_module_error(self, name: str, error_message: str) -> None:
        """Set a module to error status"""
        if name in self.modules:
            module = self.modules[name]
            module.status = "error"
            module.error_message = error_message
            module.last_heartbeat = datetime.utcnow().isoformat() + "Z"
            logger.error(f"Module error: {name} - {error_message}")
    
    def set_module_idle(self, name: str) -> None:
        """Set a module to idle status (healthy but no current activity)"""
        if name in self.modules:
            module = self.modules[name]
            module.status = "idle"
            module.error_message = None
            module.last_heartbeat = datetime.utcnow().isoformat() + "Z"
    
    def disable_module(self, name: str, reason: str = "Manually disabled") -> None:
        """Disable a module"""
        if name in self.modules:
            module = self.modules[name]
            module.status = "disabled"
            module.error_message = reason
            module.last_heartbeat = datetime.utcnow().isoformat() + "Z"
            logger.warning(f"Module disabled: {name} - {reason}")
    
    def get_module_status(self, name: str) -> Optional[ModuleStatus]:
        """Get status for a specific module"""
        return self.modules.get(name)
    
    def get_all_modules(self) -> Dict[str, ModuleStatus]:
        """Get status for all modules"""
        # Update uptime for all modules
        current_time = time.time()
        for module in self.modules.values():
            module.uptime_seconds = current_time - self.system_start_time
        
        return self.modules
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        modules = self.get_all_modules()
        
        status_counts = {
            "active": len([m for m in modules.values() if m.status == "active"]),
            "idle": len([m for m in modules.values() if m.status == "idle"]),
            "disabled": len([m for m in modules.values() if m.status == "disabled"]),
            "error": len([m for m in modules.values() if m.status == "error"])
        }
        
        total_data_points = sum(m.data_points_processed for m in modules.values())
        
        system_health = "optimal"
        if status_counts["error"] > 0:
            system_health = "degraded" 
        elif status_counts["active"] == 0:
            system_health = "idle"
        
        return {
            "system_health": system_health,
            "total_modules": len(modules),
            "status_breakdown": status_counts,
            "total_data_processed": total_data_points,
            "system_uptime_seconds": time.time() - self.system_start_time,
            "last_update": datetime.utcnow().isoformat() + "Z",
            "modules": {name: asdict(module) for name, module in modules.items()}
        }
    
    def save_status_snapshot(self, filepath: str = "iss_module/data/modules_status.json") -> None:
        """Save current status to JSON file"""
        try:
            overview = self.get_system_overview()
            
            # Ensure data directory exists
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(overview, f, indent=2, default=str)
                
            logger.info(f"Module status snapshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save status snapshot: {e}")
    
    def load_status_snapshot(self, filepath: str = "iss_module/data/modules_status.json") -> bool:
        """Load status from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Restore module states
            if "modules" in data:
                for name, module_data in data["modules"].items():
                    self.modules[name] = ModuleStatus(**module_data)
            
            logger.info(f"Module status loaded from {filepath}")
            return True
        except FileNotFoundError:
            logger.warning(f"Status file not found: {filepath}")
            return False
        except Exception as e:
            logger.error(f"Failed to load status snapshot: {e}")
            return False

# Global module status manager instance
module_status_manager = ModuleStatusManager()

# Convenience functions for easy access
def get_module_status(name: str) -> Optional[ModuleStatus]:
    """Get status for a specific module"""
    return module_status_manager.get_module_status(name)

def update_module_activity(name: str, activity: str, data_points: int = 1):
    """Update module activity"""
    module_status_manager.update_module_activity(name, activity, data_points)

def set_module_error(name: str, error: str):
    """Set module to error status"""
    module_status_manager.set_module_error(name, error)

def get_system_overview() -> Dict[str, Any]:
    """Get comprehensive system overview"""
    return module_status_manager.get_system_overview()
"""
Cali_X_One Monitoring Dashboard API
Real-time system monitoring with Server-Sent Events for Cali_X_One sovereign AI supervisor
"""

import asyncio
import json
import logging
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from ..core.utils import get_stardate, current_timecodes
from ..core.caleon_security_layer import CaleonSecurityLayer

logger = logging.getLogger("Cali_X_One.Monitor")

# Initialize security layer for monitoring
security_layer = CaleonSecurityLayer()

# Create router
monitor_router = APIRouter(prefix="/monitor", tags=["Cali_X_One Monitoring"])

# Monitoring data models
class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    process_count: int
    uptime_seconds: float

class EthicsMetrics(BaseModel):
    ethics_score: float
    tokens_filtered: int
    veto_count: int
    consent_overrides: int
    last_check: Optional[str]

class ModuleStatus(BaseModel):
    name: str
    status: str  # "active", "inactive", "error"
    health_score: float
    last_update: Optional[str]
    error_message: Optional[str]

class MonitoringSnapshot(BaseModel):
    stardate: float
    timestamp: str
    system: SystemMetrics
    ethics: EthicsMetrics
    modules: Dict[str, ModuleStatus]
    alerts: list[str]

# Global monitoring state
monitoring_state = {
    "last_snapshot": None,
    "alerts": [],
    "ethics_metrics": {
        "ethics_score": 0.0,
        "tokens_filtered": 0,
        "veto_count": 0,
        "consent_overrides": 0,
        "last_check": None
    }
}

def collect_system_metrics() -> SystemMetrics:
    """Collect real-time system metrics - DALS-001 compliant (real data only)"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = len(psutil.net_connections())
        process_count = len(psutil.pids())
        uptime_seconds = time.time() - psutil.boot_time()

        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            network_connections=network,
            process_count=process_count,
            uptime_seconds=uptime_seconds
        )
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        # Return zeros for inactive monitoring - DALS-001 compliant
        return SystemMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_percent=0.0,
            network_connections=0,
            process_count=0,
            uptime_seconds=0.0
        )

def collect_ethics_metrics() -> EthicsMetrics:
    """Collect ethics gate metrics - DALS-001 compliant"""
    try:
        # Get current ethics state from security layer
        ethics_status = security_layer.get_ethics_status()
        if ethics_status:
            return EthicsMetrics(
                ethics_score=ethics_status.get("score", 0.0),
                tokens_filtered=ethics_status.get("filtered_tokens", 0),
                veto_count=ethics_status.get("vetoes", 0),
                consent_overrides=ethics_status.get("overrides", 0),
                last_check=ethics_status.get("last_check")
            )
        else:
            # Return zeros for inactive ethics monitoring
            return EthicsMetrics(
                ethics_score=0.0,
                tokens_filtered=0,
                veto_count=0,
                consent_overrides=0,
                last_check=None
            )
    except Exception as e:
        logger.error(f"Failed to collect ethics metrics: {e}")
        return EthicsMetrics(
            ethics_score=0.0,
            tokens_filtered=0,
            veto_count=0,
            consent_overrides=0,
            last_check=None
        )

def collect_module_status() -> Dict[str, ModuleStatus]:
    """Collect status of all Cali_X_One modules - DALS-001 compliant"""
    modules = {}

    # Check ethics gate
    try:
        ethics_health = security_layer.get_health_status()
        modules["ethics_gate"] = ModuleStatus(
            name="Ethics Gate",
            status="active" if ethics_health.get("healthy", False) else "inactive",
            health_score=ethics_health.get("score", 0.0),
            last_update=ethics_health.get("last_check"),
            error_message=None
        )
    except Exception as e:
        modules["ethics_gate"] = ModuleStatus(
            name="Ethics Gate",
            status="error",
            health_score=0.0,
            last_update=None,
            error_message=str(e)
        )

    # Check articulation bridge
    try:
        # Import and check articulation bridge status
        from ..cali_x_one.articulation_bridge import ArticulationBridge
        bridge = ArticulationBridge()
        bridge_status = bridge.get_status()
        modules["articulation_bridge"] = ModuleStatus(
            name="Articulation Bridge",
            status="active" if bridge_status.get("active", False) else "inactive",
            health_score=bridge_status.get("health_score", 0.0),
            last_update=bridge_status.get("last_update"),
            error_message=None
        )
    except Exception as e:
        modules["articulation_bridge"] = ModuleStatus(
            name="Articulation Bridge",
            status="error",
            health_score=0.0,
            last_update=None,
            error_message=str(e)
        )

    # Check consent manager
    try:
        from ..cali_x_one.caleon_consent import CaleonConsentManager
        consent = CaleonConsentManager()
        consent_status = consent.get_status()
        modules["consent_manager"] = ModuleStatus(
            name="Consent Manager",
            status="active" if consent_status.get("active", False) else "inactive",
            health_score=consent_status.get("health_score", 0.0),
            last_update=consent_status.get("last_update"),
            error_message=None
        )
    except Exception as e:
        modules["consent_manager"] = ModuleStatus(
            name="Consent Manager",
            status="error",
            health_score=0.0,
            last_update=None,
            error_message=str(e)
        )

    # Check worker vault system
    try:
        # Worker vault system may not be implemented yet
        modules["worker_vault"] = ModuleStatus(
            name="Worker Vault System",
            status="inactive",
            health_score=0.0,
            last_update=None,
            error_message="Module not yet implemented"
        )
    except Exception as e:
        modules["worker_vault"] = ModuleStatus(
            name="Worker Vault System",
            status="error",
            health_score=0.0,
            last_update=None,
            error_message=str(e)
        )

    return modules

def collect_snapshot() -> MonitoringSnapshot:
    """Collect complete monitoring snapshot - DALS-001 compliant"""
    timecodes = current_timecodes()

    snapshot = MonitoringSnapshot(
        stardate=timecodes["stardate"],
        timestamp=timecodes["iso_timestamp"],
        system=collect_system_metrics(),
        ethics=collect_ethics_metrics(),
        modules=collect_module_status(),
        alerts=monitoring_state["alerts"].copy()
    )

    monitoring_state["last_snapshot"] = snapshot
    return snapshot

# Simple HTML Dashboard Template
MONITOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cali_X_One Sovereign AI Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .status-active { color: green; }
        .status-inactive { color: orange; }
        .status-error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Cali_X_One Sovereign AI Monitor</h1>
            <div id="stardate">Loading...</div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>🖥️ System Metrics</h3>
                <div class="metric"><span>CPU:</span> <span id="cpu">--</span></div>
                <div class="metric"><span>Memory:</span> <span id="memory">--</span></div>
                <div class="metric"><span>Disk:</span> <span id="disk">--</span></div>
                <div class="metric"><span>Processes:</span> <span id="processes">--</span></div>
            </div>

            <div class="card">
                <h3>⚖️ Ethics Gate</h3>
                <div class="metric"><span>Score:</span> <span id="ethics-score">--</span></div>
                <div class="metric"><span>Filtered:</span> <span id="filtered">--</span></div>
                <div class="metric"><span>Vetoes:</span> <span id="vetoes">--</span></div>
            </div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h3>🔧 Module Status</h3>
            <div id="modules">Loading modules...</div>
        </div>
    </div>

    <script>
        function updateDashboard(data) {
            document.getElementById('stardate').textContent = `Stardate: ${data.stardate.toFixed(4)}`;
            document.getElementById('cpu').textContent = `${data.system.cpu_percent.toFixed(1)}%`;
            document.getElementById('memory').textContent = `${data.system.memory_percent.toFixed(1)}%`;
            document.getElementById('disk').textContent = `${data.system.disk_percent.toFixed(1)}%`;
            document.getElementById('processes').textContent = data.system.process_count;
            document.getElementById('ethics-score').textContent = data.ethics.ethics_score.toFixed(2);
            document.getElementById('filtered').textContent = data.ethics.tokens_filtered;
            document.getElementById('vetoes').textContent = data.ethics.veto_count;

            const modulesDiv = document.getElementById('modules');
            modulesDiv.innerHTML = '';
            Object.values(data.modules).forEach(module => {
                const div = document.createElement('div');
                div.className = `metric status-${module.status}`;
                div.innerHTML = `<span>${module.name}:</span> <span>${module.status}</span>`;
                modulesDiv.appendChild(div);
            });
        }

        // Connect to Server-Sent Events
        const eventSource = new EventSource('/monitor/stream');
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
    </script>
</body>
</html>
"""

@monitor_router.get("/", response_class=HTMLResponse)
async def get_monitor_dashboard():
    """Serve the Cali_X_One monitoring dashboard"""
    return MONITOR_HTML

@monitor_router.get("/stream")
async def stream_monitoring_data():
    """Server-Sent Events endpoint for real-time monitoring data"""

    async def event_generator():
        while True:
            try:
                # Collect fresh snapshot
                snapshot = collect_snapshot()

                # Convert to dict for JSON serialization
                data = {
                    "stardate": snapshot.stardate,
                    "timestamp": snapshot.timestamp,
                    "system": {
                        "cpu_percent": snapshot.system.cpu_percent,
                        "memory_percent": snapshot.system.memory_percent,
                        "disk_percent": snapshot.system.disk_percent,
                        "network_connections": snapshot.system.network_connections,
                        "process_count": snapshot.system.process_count,
                        "uptime_seconds": snapshot.system.uptime_seconds
                    },
                    "ethics": {
                        "ethics_score": snapshot.ethics.ethics_score,
                        "tokens_filtered": snapshot.ethics.tokens_filtered,
                        "veto_count": snapshot.ethics.veto_count,
                        "consent_overrides": snapshot.ethics.consent_overrides,
                        "last_check": snapshot.ethics.last_check
                    },
                    "modules": {
                        name: {
                            "name": module.name,
                            "status": module.status,
                            "health_score": module.health_score,
                            "last_update": module.last_update,
                            "error_message": module.error_message
                        }
                        for name, module in snapshot.modules.items()
                    },
                    "alerts": snapshot.alerts
                }

                # Send data as Server-Sent Event
                yield f"data: {json.dumps(data)}\n\n"

                # Wait before next update (5 seconds)
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in monitoring stream: {e}")
                # Send error data
                error_data = {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                await asyncio.sleep(10)  # Wait longer on error

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@monitor_router.get("/snapshot")
async def get_monitoring_snapshot():
    """Get current monitoring snapshot"""
    try:
        snapshot = collect_snapshot()
        return snapshot.dict()
    except Exception as e:
        logger.error(f"Failed to get monitoring snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Monitoring error: {str(e)}")

@monitor_router.get("/health")
async def get_monitor_health():
    """Health check for monitoring system"""
    try:
        snapshot = collect_snapshot()
        return {
            "status": "healthy",
            "stardate": snapshot.stardate,
            "modules_active": len([m for m in snapshot.modules.values() if m.status == "active"]),
            "ethics_score": snapshot.ethics.ethics_score
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
#!/usr/bin/env python3
"""
CANS - Cognitive Autonomous Neural Synchronizer
Main service entry point for the CANS microservice

CANS maintains real-time synchronization between UCM and all cognitive submodules,
serving as the heartbeat manager and autonomic nervous system for the AI brain.
"""

import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
from cans.core.config import CANSConfig
from cans.core.state import CANSState
from cans.api.heartbeat_router import router as heartbeat_router, set_cans_state as set_heartbeat_state
from cans.api.sync_router import router as sync_router, set_cans_state as set_sync_state
from cans.api.monitor_router import router as monitor_router, set_cans_state as set_monitor_state
from cans.services.heartbeat_emitter import HeartbeatEmitter
from cans.services.sync_beacon import SyncBeacon
from cans.services.module_monitor import ModuleMonitor
from cans.services.cycle_aligner import CycleAligner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CANS.Main")

# Global CANS state
cans_state = CANSState()
config = CANSConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    logger.info("🚀 CANS Cognitive Autonomous Neural Synchronizer starting...")

    # Initialize core services
    await initialize_cans_services()

    logger.info("✅ CANS fully operational - monitoring cognitive modules")
    yield

    # Shutdown cleanup
    logger.info("🛑 CANS shutting down...")
    await shutdown_cans_services()
    logger.info("✅ CANS shutdown complete")

async def initialize_cans_services():
    """Initialize all CANS core services"""
    try:
        # Start heartbeat emitter
        heartbeat_emitter = HeartbeatEmitter(cans_state, config)
        asyncio.create_task(heartbeat_emitter.start_emitting())

        # Start synchronization beacon
        sync_beacon = SyncBeacon(cans_state, config)
        asyncio.create_task(sync_beacon.start_broadcasting())

        # Start module monitor
        module_monitor = ModuleMonitor(cans_state, config)
        asyncio.create_task(module_monitor.start_monitoring())

        # Start cycle aligner
        cycle_aligner = CycleAligner(cans_state, config)
        asyncio.create_task(cycle_aligner.start_alignment())

        logger.info("🎯 All CANS services initialized and running")

    except Exception as e:
        logger.error(f"❌ Failed to initialize CANS services: {e}")
        raise

async def shutdown_cans_services():
    """Clean shutdown of all CANS services"""
    try:
        # Set shutdown flag
        cans_state.is_shutting_down = True

        # Wait for services to acknowledge shutdown
        await asyncio.sleep(1.0)

        logger.info("🧹 CANS services shutdown complete")

    except Exception as e:
        logger.error(f"Error during CANS shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="CANS - Cognitive Autonomous Neural Synchronizer",
    description="Autonomic nervous system for AI cognitive modules - maintains synchronization, heartbeat, and stability",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(heartbeat_router, prefix="/api/cans", tags=["heartbeat"])
app.include_router(sync_router, prefix="/api/cans", tags=["sync"])
app.include_router(monitor_router, prefix="/api/cans", tags=["monitor"])

# Set CANS state in routers
set_heartbeat_state(cans_state)
set_sync_state(cans_state)
set_monitor_state(cans_state)

@app.get("/")
async def root():
    """Root endpoint with CANS status"""
    return {
        "service": "CANS - Cognitive Autonomous Neural Synchronizer",
        "status": "operational",
        "version": "1.0.0",
        "description": "AI autonomic nervous system - heartbeat, sync, and stability monitor"
    }

@app.get("/health")
async def health_check():
    """CANS health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "heartbeat_emitter": "active",
            "sync_beacon": "active",
            "module_monitor": "active",
            "cycle_aligner": "active"
        },
        "monitored_modules": len(cans_state.module_states),
        "sync_cycles": cans_state.sync_cycle_count
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info"
    )
"""
UCM (Unified Cognition Module) Connector
=========================================
Integrates Caleon Prime (UCM) as the sovereign cognitive manager of DALS.

Architecture:
- UCM: Sovereign AI manager with full DALS authority
- CALEON: Security gateway validating UCM commands
- Founder: Ultimate authority with override capability

UCM runs independently on port 8080 (configurable)
All DALS operations route through UCM for cognitive processing
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

# ✅ ISS Timestamp Integration
from ..core.utils import current_timecodes

logger = logging.getLogger("DALS.UCM.Connector")


class UCMConnectionState(Enum):
    """UCM connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    FOUNDER_OVERRIDE = "founder_override"


class UCMConnector:
    """
    UCM Connector - Bridge between DALS and Unified Cognition Module
    
    Responsibilities:
    1. Maintain connection to UCM service
    2. Forward DALS queries to UCM for cognitive processing
    3. Route UCM commands through CALEON security layer
    4. Monitor UCM health and performance
    5. Handle failover and error recovery
    """
    
    def __init__(
        self,
        ucm_host: str = "localhost",
        ucm_port: int = 8080,
        api_prefix: str = "/api/v1",
        timeout: int = 30
    ):
        self.ucm_host = ucm_host
        self.ucm_port = ucm_port
        self.api_prefix = api_prefix
        self.timeout = timeout
        
        # Connection state
        self.state = UCMConnectionState.DISCONNECTED
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Performance tracking
        self.request_count = 0
        self.error_count = 0
        self.last_request_time: Optional[datetime] = None
        self.avg_response_time = 0.0
        
        # Health monitoring
        self.last_health_check: Optional[datetime] = None
        self.health_status = "unknown"
        
        logger.info(
            f"UCM Connector initialized",
            extra={
                "ucm_host": ucm_host,
                "ucm_port": ucm_port,
                "api_prefix": api_prefix
            }
        )
    
    @property
    def base_url(self) -> str:
        """Get UCM base URL"""
        return f"http://{self.ucm_host}:{self.ucm_port}{self.api_prefix}"
    
    async def connect(self) -> Dict[str, Any]:
        """
        Establish connection to UCM
        
        Returns:
            Connection status and details
        """
        try:
            self.state = UCMConnectionState.CONNECTING
            
            # Create aiohttp session
            if self.session is None or self.session.closed:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            # Verify UCM is accessible
            health = await self.health_check()
            
            if health.get("status") == "healthy":
                self.state = UCMConnectionState.CONNECTED
                timecodes = current_timecodes()  # ✅ ISS timestamp
                logger.info("UCM connection established", extra={"health": health})
                return {
                    "success": True,
                    "state": self.state.value,
                    "ucm_health": health,
                    "connected_at_iso": timecodes['iso_timestamp'],
                    "connected_at_stardate": timecodes['stardate'],
                    "connected_at_epoch": timecodes['unix_timestamp']
                }
            else:
                self.state = UCMConnectionState.ERROR
                return {
                    "success": False,
                    "state": self.state.value,
                    "error": "UCM health check failed"
                }
                
        except Exception as e:
            self.state = UCMConnectionState.ERROR
            self.error_count += 1
            logger.error(f"UCM connection failed: {e}")
            return {
                "success": False,
                "state": self.state.value,
                "error": str(e)
            }
    
    async def disconnect(self):
        """Close UCM connection"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        self.state = UCMConnectionState.DISCONNECTED
        logger.info("UCM connection closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check UCM health status
        
        Returns:
            UCM health information
        """
        try:
            url = f"http://{self.ucm_host}:{self.ucm_port}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        # ✅ ISS timestamp for health check
                        self.last_health_check = datetime.now(timezone.utc)
                        self.health_status = health_data.get("status", "unknown")
                        return health_data
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            logger.error(f"UCM health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def submit_reasoning_request(
        self,
        content: str,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit cognitive reasoning request to UCM
        
        Args:
            content: Query or problem to process
            priority: Request priority (low, normal, high, critical)
            metadata: Additional context and parameters
            
        Returns:
            UCM reasoning response
        """
        if self.state != UCMConnectionState.CONNECTED:
            return {
                "success": False,
                "error": f"UCM not connected (state: {self.state.value})"
            }
        
        try:
            # ✅ ISS Timestamp Integration - Use canonical timecodes
            start_timecodes = current_timecodes()
            start_time = datetime.fromisoformat(start_timecodes['iso_timestamp'])
            
            # Prepare request with full ISS timestamp suite
            request_data = {
                "content": content,
                "priority": priority,
                "metadata": metadata or {
                    "source": "DALS",
                    "timestamp_iso": start_timecodes['iso_timestamp'],
                    "timestamp_stardate": start_timecodes['stardate'],
                    "timestamp_julian": start_timecodes['julian_date'],
                    "timestamp_epoch": start_timecodes['unix_timestamp'],
                    "anchor_hash": start_timecodes['anchor_hash']
                }
            }
            
            # Send to UCM
            url = f"{self.base_url}/reason"
            
            async with self.session.post(url, json=request_data) as response:
                end_timecodes = current_timecodes()
                end_time = datetime.fromisoformat(end_timecodes['iso_timestamp'])
                response_time = (end_time - start_time).total_seconds()
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Update metrics
                    self.request_count += 1
                    self.last_request_time = end_time
                    self.avg_response_time = (
                        (self.avg_response_time * (self.request_count - 1) + response_time)
                        / self.request_count
                    )
                    
                    logger.info(
                        "UCM reasoning completed",
                        extra={
                            "priority": priority,
                            "response_time": response_time,
                            "request_count": self.request_count
                        }
                    )
                    
                    return {
                        "success": True,
                        "result": result,
                        "response_time": response_time,
                        "timestamp_iso": end_timecodes['iso_timestamp'],
                        "timestamp_stardate": end_timecodes['stardate'],
                        "timestamp_julian": end_timecodes['julian_date'],
                        "timestamp_epoch": end_timecodes['unix_timestamp']
                    }
                else:
                    error_text = await response.text()
                    self.error_count += 1
                    
                    logger.error(
                        f"UCM reasoning failed: HTTP {response.status}",
                        extra={"error": error_text}
                    )
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except asyncio.TimeoutError:
            self.error_count += 1
            logger.error("UCM reasoning request timed out")
            return {
                "success": False,
                "error": "Request timeout"
            }
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"UCM reasoning request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_reasoning(
        self,
        reasoning_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute sequential reasoning through UCM cerebral cortex

        This method handles step-by-step reasoning with ethical oversight
        and drift detection, streaming results for real-time UI updates.

        Args:
            reasoning_context: Complete reasoning context including query,
                             mode, ethical checks, and security validation

        Returns:
            Reasoning execution results with steps and final assessment
        """
        if self.state != UCMConnectionState.CONNECTED:
            return {
                "success": False,
                "error": f"UCM not connected (state: {self.state.value})",
                "steps": [],
                "final_assessment": {}
            }

        try:
            start_time = datetime.now(timezone.utc)
            start_timecodes = current_timecodes()

            # Prepare sequential reasoning request
            request_data = {
                "query": reasoning_context["query"],
                "mode": reasoning_context.get("mode", "sequential"),
                "ethical_check": reasoning_context.get("ethical_check", True),
                "drift_detection": reasoning_context.get("drift_detection", True),
                "max_steps": reasoning_context.get("max_steps", 10),
                "context": reasoning_context.get("context", {}),
                "security_validation": reasoning_context.get("security_validation", {}),
                "stardate": reasoning_context.get("stardate", start_timecodes['stardate']),
                "metadata": {
                    "source": "DALS.SequentialThinking",
                    "timestamp_iso": start_timecodes['iso_timestamp'],
                    "timestamp_stardate": start_timecodes['stardate'],
                    "caleon_approved": reasoning_context.get("security_validation", {}).get("approved", False)
                }
            }

            # Execute reasoning through UCM
            url = f"{self.base_url}/reason/sequential"

            async with self.session.post(url, json=request_data) as response:
                end_time = datetime.now(timezone.utc)
                processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

                if response.status == 200:
                    result = await response.json()

                    # Update metrics
                    self.request_count += 1
                    self.last_request_time = end_time

                    # Extract reasoning steps
                    steps = result.get("steps", [])
                    final_assessment = result.get("final_assessment", {})

                    # Add ethical and drift analysis to steps
                    enhanced_steps = []
                    for i, step in enumerate(steps):
                        enhanced_step = {
                            "content": step.get("content", ""),
                            "type": step.get("type", "analysis"),
                            "confidence": step.get("confidence", 0.8),
                            "ethical_score": step.get("ethical_score"),
                            "drift_score": step.get("drift_score"),
                            "requires_review": step.get("requires_review", False),
                            "metadata": step.get("metadata", {})
                        }
                        enhanced_steps.append(enhanced_step)

                    logger.info(
                        f"Sequential reasoning completed: {len(enhanced_steps)} steps",
                        extra={
                            "processing_time_ms": processing_time_ms,
                            "ethical_concerns": any(s.get("requires_review", False) for s in enhanced_steps)
                        }
                    )

                    return {
                        "success": True,
                        "steps": enhanced_steps,
                        "final_assessment": final_assessment,
                        "processing_time_ms": processing_time_ms,
                        "timestamp_iso": current_timecodes()['iso_timestamp'],
                        "timestamp_stardate": current_timecodes()['stardate'],
                        "security_validated": reasoning_context.get("security_validation", {}).get("approved", False)
                    }

                else:
                    error_text = await response.text()
                    self.error_count += 1

                    logger.error(
                        f"UCM sequential reasoning failed: HTTP {response.status}",
                        extra={"error": error_text}
                    )

                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "steps": [],
                        "final_assessment": {}
                    }

        except Exception as e:
            self.error_count += 1
            logger.error(f"UCM sequential reasoning failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "steps": [],
                "final_assessment": {}
            }

    async def execute_dals_command(
        self,
        command: str,
        parameters: Dict[str, Any],
        ucm_authorization: str
    ) -> Dict[str, Any]:
        """
        Execute DALS command via UCM cognitive processing
        
        This method sends DALS commands to UCM for cognitive evaluation,
        then routes validated commands through CALEON security layer.
        
        Args:
            command: DALS command to execute
            parameters: Command parameters
            ucm_authorization: UCM session authorization token
            
        Returns:
            Command execution result
        """
        # First, submit to UCM for cognitive processing
        reasoning_request = f"Execute DALS command: {command} with parameters: {parameters}"
        
        ucm_response = await self.submit_reasoning_request(
            content=reasoning_request,
            priority="high",
            metadata={
                "command_type": "dals_execution",
                "command": command,
                "parameters": parameters,
                "authorization": ucm_authorization
            }
        )
        
        if not ucm_response.get("success"):
            return {
                "success": False,
                "error": "UCM cognitive processing failed",
                "details": ucm_response
            }
        
        # UCM has approved - return for CALEON validation
        return {
            "success": True,
            "ucm_approved": True,
            "ucm_reasoning": ucm_response.get("result"),
            "command": command,
            "parameters": parameters,
            "requires_caleon_validation": True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get connector status and metrics
        
        Returns:
            Current status, metrics, and health information
        """
        return {
            "connection_state": self.state.value,
            "ucm_endpoint": f"{self.ucm_host}:{self.ucm_port}",
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "metrics": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "success_rate": (
                    ((self.request_count - self.error_count) / self.request_count * 100)
                    if self.request_count > 0 else 0.0
                ),
                "avg_response_time": self.avg_response_time,
                "last_request": self.last_request_time.isoformat() if self.last_request_time else None
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Global UCM connector instance
_ucm_connector: Optional[UCMConnector] = None


def get_ucm_connector(
    ucm_host: str = "localhost",
    ucm_port: int = 8080
) -> UCMConnector:
    """
    Get or create global UCM connector instance
    
    Args:
        ucm_host: UCM hostname
        ucm_port: UCM port number
        
    Returns:
        UCM connector instance
    """
    global _ucm_connector
    
    if _ucm_connector is None:
        _ucm_connector = UCMConnector(
            ucm_host=ucm_host,
            ucm_port=ucm_port
        )
    
    return _ucm_connector

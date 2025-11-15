"""
Diagnostic Engine

Automatically detects and analyzes system failures and issues.
Integrates with existing DALS monitoring systems.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from iss_module.core.utils import get_stardate, current_timecodes
from iss_module.core.caleon_security_layer import CaleonSecurityLayer
from iss_module.integrations.ucm_connector import get_ucm_connector
from iss_module.csmm.models.csmm_models import (
    DiagnosticResult,
    ComponentIssue,
    DiagnosticSeverity,
    SystemHealth
)

logger = logging.getLogger("DALS.CSMM.Diagnostics")

class DiagnosticEngine:
    """
    CSMM Diagnostic Engine

    Performs comprehensive system diagnostics including:
    - Component health checks
    - Service availability verification
    - Performance monitoring
    - Error pattern detection
    - Integration with UCM cognitive analysis
    """

    def __init__(self):
        self.security_layer = CaleonSecurityLayer()
        self.ucm_connector = get_ucm_connector()
        self.diagnostic_history: List[DiagnosticResult] = []

        # Component check configurations
        self.component_checks = {
            "dals_api": self._check_dals_api,
            "ucm_service": self._check_ucm_service,
            "caleon_security": self._check_caleon_security,
            "database": self._check_database,
            "telemetry": self._check_telemetry,
            "inventory": self._check_inventory,
            "voice_routes": self._check_voice_routes,
            "thinker_orchestrator": self._check_thinker_orchestrator,
            "task_orchestrator": self._check_task_orchestrator,
            "reflection_vault": self._check_reflection_vault,
            "voice_console": self._check_voice_console,
            "dashboard": self._check_dashboard
        }

    async def run_diagnostics(self, target_component: Optional[str] = None) -> DiagnosticResult:
        """
        Run comprehensive system diagnostics

        Args:
            target_component: Specific component to diagnose, or None for full system

        Returns:
            DiagnosticResult: Complete diagnostic results
        """
        start_time = datetime.utcnow()
        diagnostic_id = f"diag_{get_stardate()}_{start_time.timestamp()}"

        logger.info("Starting system diagnostics", extra={
            "correlation_id": diagnostic_id,
            "target_component": target_component,
            "stardate": get_stardate()
        })

        try:
            # Validate security permissions
            security_check = await self.security_layer.validate_reasoning_request(
                query=f"CSMM diagnostic run: {diagnostic_id}",
                mode="sequential",
                ethical_check=True
            )

            if not security_check.get("approved", False):
                logger.warning("Diagnostic blocked by Caleon security", extra={
                    "correlation_id": diagnostic_id,
                    "reason": security_check.get("reason", "unknown")
                })
                return self._create_error_result(diagnostic_id, "Security authorization failed")

            # Determine which components to check
            components_to_check = [target_component] if target_component else list(self.component_checks.keys())

            # Run all component checks
            issues = []
            for component in components_to_check:
                if component in self.component_checks:
                    component_issues = await self.component_checks[component]()
                    issues.extend(component_issues)

            # Assess overall system health
            system_health = await self._assess_overall_health(issues)

            # Create diagnostic result
            result = DiagnosticResult(
                diagnostic_id=diagnostic_id,
                timestamp=current_timecodes()["iso_timestamp"],
                target_component=target_component,
                issues_found=len(issues) > 0,
                issues=issues,
                system_health=system_health,
                duration_seconds=(datetime.utcnow() - start_time).total_seconds()
            )

            # Store in history
            self.diagnostic_history.append(result)
            if len(self.diagnostic_history) > 50:  # Keep last 50 diagnostics
                self.diagnostic_history = self.diagnostic_history[-50:]

            logger.info("Diagnostics completed", extra={
                "correlation_id": diagnostic_id,
                "issues_found": len(issues),
                "duration": result.duration_seconds
            })

            return result

        except Exception as e:
            logger.error(f"Diagnostic run failed: {e}", extra={
                "correlation_id": diagnostic_id,
                "error": str(e)
            })
            return self._create_error_result(diagnostic_id, str(e))

    async def _check_dals_api(self) -> List[ComponentIssue]:
        """Check DALS API service health"""
        issues = []

        try:
            # Check if API is responding
            # This would integrate with existing DALS health checks
            # For now, simulate basic check
            api_health = await self._simulate_health_check("dals_api")

            if not api_health.get("healthy", True):
                issues.append(ComponentIssue(
                    component="dals_api",
                    issue_type="service_unavailable",
                    severity=DiagnosticSeverity.HIGH,
                    description="DALS API service is not responding",
                    recommended_action="restart_api_service",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="dals_api",
                issue_type="diagnostic_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Failed to check DALS API: {e}",
                recommended_action="investigate_diagnostic_error",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_ucm_service(self) -> List[ComponentIssue]:
        """Check UCM cognitive service health"""
        issues = []

        try:
            # Check UCM connectivity
            if self.ucm_connector:
                health = await self.ucm_connector.health_check()
                if not health.get("healthy", False):
                    issues.append(ComponentIssue(
                        component="ucm_service",
                        issue_type="service_unavailable",
                        severity=DiagnosticSeverity.CRITICAL,
                        description="UCM cognitive service is not responding",
                        recommended_action="restart_ucm_service",
                        detected_at=current_timecodes()["iso_timestamp"]
                    ))
            else:
                issues.append(ComponentIssue(
                    component="ucm_service",
                    issue_type="connector_unavailable",
                    severity=DiagnosticSeverity.HIGH,
                    description="UCM connector not initialized",
                    recommended_action="initialize_ucm_connector",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="ucm_service",
                issue_type="diagnostic_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Failed to check UCM service: {e}",
                recommended_action="investigate_ucm_connection",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_caleon_security(self) -> List[ComponentIssue]:
        """Check Caleon security layer health"""
        issues = []

        try:
            # Test security layer responsiveness
            test_result = await self.security_layer.validate_reasoning_request(
                query="CSMM security layer health check",
                mode="sequential",
                ethical_check=True
            )

            if not test_result.get("authorized", False):
                issues.append(ComponentIssue(
                    component="caleon_security",
                    issue_type="security_validation_failed",
                    severity=DiagnosticSeverity.CRITICAL,
                    description="Caleon security layer validation failed",
                    recommended_action="investigate_security_layer",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="caleon_security",
                issue_type="diagnostic_error",
                severity=DiagnosticSeverity.HIGH,
                description=f"Failed to check Caleon security: {e}",
                recommended_action="restart_security_layer",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_database(self) -> List[ComponentIssue]:
        """Check database connectivity and health"""
        issues = []

        try:
            # This would check actual database connections
            # For now, simulate check
            db_health = await self._simulate_health_check("database")

            if not db_health.get("healthy", True):
                issues.append(ComponentIssue(
                    component="database",
                    issue_type="connection_failed",
                    severity=DiagnosticSeverity.HIGH,
                    description="Database connection is not available",
                    recommended_action="restart_database_connection",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="database",
                issue_type="diagnostic_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Failed to check database: {e}",
                recommended_action="investigate_database_connection",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_telemetry(self) -> List[ComponentIssue]:
        """Check telemetry system health"""
        issues = []

        try:
            # Check telemetry data flow
            telemetry_health = await self._simulate_health_check("telemetry")

            if not telemetry_health.get("healthy", True):
                issues.append(ComponentIssue(
                    component="telemetry",
                    issue_type="data_flow_blocked",
                    severity=DiagnosticSeverity.MEDIUM,
                    description="Telemetry data flow is interrupted",
                    recommended_action="restart_telemetry_service",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="telemetry",
                issue_type="diagnostic_error",
                severity=DiagnosticSeverity.LOW,
                description=f"Failed to check telemetry: {e}",
                recommended_action="investigate_telemetry_system",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_inventory(self) -> List[ComponentIssue]:
        """Check inventory management system health"""
        issues = []

        try:
            # Check inventory system
            inventory_health = await self._simulate_health_check("inventory")

            if not inventory_health.get("healthy", True):
                issues.append(ComponentIssue(
                    component="inventory",
                    issue_type="system_unavailable",
                    severity=DiagnosticSeverity.MEDIUM,
                    description="Inventory management system is not responding",
                    recommended_action="restart_inventory_service",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="inventory",
                issue_type="diagnostic_error",
                severity=DiagnosticSeverity.LOW,
                description=f"Failed to check inventory: {e}",
                recommended_action="investigate_inventory_system",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _assess_overall_health(self, issues: List[ComponentIssue]) -> SystemHealth:
        """
        Assess overall system health from detected issues

        Args:
            issues: List of detected component issues

        Returns:
            SystemHealth: Overall system health assessment
        """
        timecodes = current_timecodes()

        # Calculate overall health score (0-100)
        # Start with perfect health, deduct points for issues
        overall_score = 100

        # Count issues by severity
        critical_count = sum(1 for issue in issues if issue.severity.value == "critical")
        high_count = sum(1 for issue in issues if issue.severity.value == "high")
        medium_count = sum(1 for issue in issues if issue.severity.value == "medium")
        low_count = sum(1 for issue in issues if issue.severity.value == "low")

        # Deduct points based on severity
        overall_score -= critical_count * 25  # Critical issues: -25 each
        overall_score -= high_count * 15      # High issues: -15 each
        overall_score -= medium_count * 8     # Medium issues: -8 each
        overall_score -= low_count * 3        # Low issues: -3 each

        # Ensure score doesn't go below 0
        overall_score = max(0, overall_score)

        # Build component health data
        component_health = {}
        components_checked = set(self.component_checks.keys())

        for component in components_checked:
            component_issues = [issue for issue in issues if issue.component == component]
            component_health[component] = {
                "issues_count": len(component_issues),
                "critical_issues": sum(1 for issue in component_issues if issue.severity.value == "critical"),
                "status": "healthy" if len(component_issues) == 0 else "degraded" if any(issue.severity.value in ["high", "critical"] for issue in component_issues) else "warning"
            }

        return SystemHealth(
            timestamp=timecodes["iso_timestamp"],
            stardate=str(timecodes["stardate"]),  # Convert to string as required by model
            overall_score=overall_score,
            component_health=component_health,
            issues_detected=len(issues)
        )

    async def _simulate_health_check(self, component: str) -> Dict[str, Any]:
        """
        Simulate health check for development
        In production, this would check actual component health

        Args:
            component: Component name

        Returns:
            Dict with health status
        """
        # Simulate basic health checks
        # In real implementation, this would check actual services
        await asyncio.sleep(0.1)  # Simulate network delay

        # For demo purposes, assume components are healthy
        # Real implementation would check actual service endpoints
        return {
            "healthy": True,
            "response_time": 0.1,
            "component": component
        }

    async def _check_voice_routes(self) -> List[ComponentIssue]:
        """Check voice routes (TTS/STT)"""
        issues = []
        try:
            # Check TTS service
            # This would integrate with actual voice services
            # For now, simulate basic checks
            tts_healthy = True  # Would check actual TTS endpoint
            stt_healthy = True  # Would check actual STT endpoint

            if not tts_healthy:
                issues.append(ComponentIssue(
                    component="voice_routes",
                    issue_type="tts_failure",
                    severity=DiagnosticSeverity.HIGH,
                    description="Text-to-Speech service is not responding",
                    recommended_action="restart_tts_service",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

            if not stt_healthy:
                issues.append(ComponentIssue(
                    component="voice_routes",
                    issue_type="stt_failure",
                    severity=DiagnosticSeverity.HIGH,
                    description="Speech-to-Text service is not responding",
                    recommended_action="restart_stt_service",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="voice_routes",
                issue_type="voice_check_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Voice routes check failed: {e}",
                recommended_action="investigate_voice_routes",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_thinker_orchestrator(self) -> List[ComponentIssue]:
        """Check Thinker/Orchestrator service"""
        issues = []
        try:
            # Check if Thinker thread is running
            # This would check actual Thinker process status
            thinker_running = True  # Would check actual process

            if not thinker_running:
                issues.append(ComponentIssue(
                    component="thinker_orchestrator",
                    issue_type="thinker_hung",
                    severity=DiagnosticSeverity.CRITICAL,
                    description="Thinker/Orchestrator thread is not responding",
                    recommended_action="restart_thinker_thread",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="thinker_orchestrator",
                issue_type="thinker_check_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Thinker check failed: {e}",
                recommended_action="investigate_thinker_orchestrator",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_task_orchestrator(self) -> List[ComponentIssue]:
        """Check Task Orchestrator service"""
        issues = []
        try:
            # Check Task Orchestrator health
            # This would check the task-orchestrator service
            task_orchestrator_healthy = True  # Would check actual service

            if not task_orchestrator_healthy:
                issues.append(ComponentIssue(
                    component="task_orchestrator",
                    issue_type="task_orchestrator_failure",
                    severity=DiagnosticSeverity.HIGH,
                    description="Task Orchestrator service is not responding",
                    recommended_action="restart_task_orchestrator",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="task_orchestrator",
                issue_type="task_orchestrator_check_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Task Orchestrator check failed: {e}",
                recommended_action="investigate_task_orchestrator",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_reflection_vault(self) -> List[ComponentIssue]:
        """Check Reflection Vault system"""
        issues = []
        try:
            # Check vault write/read operations
            vault_accessible = True  # Would check actual vault operations

            if not vault_accessible:
                issues.append(ComponentIssue(
                    component="reflection_vault",
                    issue_type="vault_access_failure",
                    severity=DiagnosticSeverity.HIGH,
                    description="Reflection Vault is not accessible for read/write operations",
                    recommended_action="repair_vault_connection",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="reflection_vault",
                issue_type="vault_check_error",
                severity=DiagnosticSeverity.MEDIUM,
                description=f"Vault check failed: {e}",
                recommended_action="investigate_reflection_vault",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_voice_console(self) -> List[ComponentIssue]:
        """Check Voice Console interface"""
        issues = []
        try:
            # Check voice console connectivity
            voice_console_healthy = True  # Would check actual voice console

            if not voice_console_healthy:
                issues.append(ComponentIssue(
                    component="voice_console",
                    issue_type="voice_console_failure",
                    severity=DiagnosticSeverity.MEDIUM,
                    description="Voice Console interface is not responding",
                    recommended_action="restart_voice_console",
                    detected_at=current_timecodes()["iso_timestamp"]
                ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="voice_console",
                issue_type="voice_console_check_error",
                severity=DiagnosticSeverity.LOW,
                description=f"Voice console check failed: {e}",
                recommended_action="investigate_voice_console",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _check_dashboard(self) -> List[ComponentIssue]:
        """Check Dashboard service (port 8008)"""
        issues = []
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8008/health")
                if response.status_code != 200:
                    issues.append(ComponentIssue(
                        component="dashboard",
                        issue_type="dashboard_unhealthy",
                        severity=DiagnosticSeverity.HIGH,
                        description=f"Dashboard returned status {response.status_code}",
                        recommended_action="restart_dashboard_service",
                        detected_at=current_timecodes()["iso_timestamp"]
                    ))

        except Exception as e:
            issues.append(ComponentIssue(
                component="dashboard",
                issue_type="dashboard_connection_failure",
                severity=DiagnosticSeverity.HIGH,
                description=f"Cannot connect to Dashboard service: {e}",
                recommended_action="restart_dashboard_service",
                detected_at=current_timecodes()["iso_timestamp"]
            ))

        return issues

    async def _assess_overall_health(self, issues: List[ComponentIssue]) -> SystemHealth:
        """
        Assess overall system health from detected issues

        Args:
            issues: List of detected component issues

        Returns:
            SystemHealth: Overall system health assessment
        """
        timecodes = current_timecodes()

        # Calculate overall health score (0-100)
        # Start with perfect health, deduct points for issues
        overall_score = 100

        # Count issues by severity
        critical_count = sum(1 for issue in issues if issue.severity.value == "critical")
        high_count = sum(1 for issue in issues if issue.severity.value == "high")
        medium_count = sum(1 for issue in issues if issue.severity.value == "medium")
        low_count = sum(1 for issue in issues if issue.severity.value == "low")

        # Deduct points based on severity
        overall_score -= critical_count * 25  # Critical issues: -25 each
        overall_score -= high_count * 15      # High issues: -15 each
        overall_score -= medium_count * 8     # Medium issues: -8 each
        overall_score -= low_count * 3        # Low issues: -3 each

        # Ensure score doesn't go below 0
        overall_score = max(0, overall_score)

        # Build component health data
        component_health = {}
        components_checked = set(self.component_checks.keys())

        for component in components_checked:
            component_issues = [issue for issue in issues if issue.component == component]
            component_health[component] = {
                "issues_count": len(component_issues),
                "critical_issues": sum(1 for issue in component_issues if issue.severity.value == "critical"),
                "status": "healthy" if len(component_issues) == 0 else "degraded" if any(issue.severity.value in ["high", "critical"] for issue in component_issues) else "warning"
            }

        return SystemHealth(
            timestamp=timecodes["iso_timestamp"],
            stardate=str(timecodes["stardate"]),  # Convert to string as required by model
            overall_score=overall_score,
            component_health=component_health,
            issues_detected=len(issues)
        )

    def _create_error_result(self, diagnostic_id: str, error: str) -> DiagnosticResult:
        """Create error diagnostic result"""
        timecodes = current_timecodes()

        return DiagnosticResult(
            diagnostic_id=diagnostic_id,
            timestamp=timecodes["iso_timestamp"],
            target_component=None,
            issues_found=True,
            issues=[ComponentIssue(
                component="diagnostic_engine",
                issue_type="diagnostic_failure",
                severity=DiagnosticSeverity.CRITICAL,
                description=f"Diagnostic engine failed: {error}",
                recommended_action="investigate_diagnostic_engine",
                detected_at=timecodes["iso_timestamp"]
            )],
            system_health=SystemHealth(
                timestamp=timecodes["iso_timestamp"],
                stardate=str(timecodes["stardate"]),  # Convert to string as required by model
                overall_score=0,
                component_health={},
                issues_detected=1
            ),
            duration_seconds=0.0
        )

    async def get_diagnostic_history(self, limit: int = 10) -> List[DiagnosticResult]:
        """
        Get recent diagnostic history

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent diagnostic results
        """
        return self.diagnostic_history[-limit:] if self.diagnostic_history else []

    async def get_active_issues(self) -> List[ComponentIssue]:
        """
        Get currently active system issues

        Returns:
            List of active component issues
        """
        # Get the most recent diagnostic
        if not self.diagnostic_history:
            return []

        latest_diagnostic = self.diagnostic_history[-1]
        return latest_diagnostic.issues

    async def get_critical_issues(self) -> List[ComponentIssue]:
        """
        Get critical system issues requiring immediate attention

        Returns:
            List of critical component issues
        """
        active_issues = await self.get_active_issues()
        return [issue for issue in active_issues if issue.severity.value == "critical"]
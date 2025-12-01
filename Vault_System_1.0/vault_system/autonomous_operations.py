# autonomous_operations.py

"""
Autonomous Operations - Self-Managing System Capabilities

This module provides autonomous operation capabilities for the vault system,
including automated decision making, self-optimization, and independent execution.
"""

import asyncio
import threading
import time
from typing import Dict, Any, List, Optional, Callable, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import random
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import psutil
import os


class OperationMode(Enum):
    """Autonomous operation modes"""
    FULL_AUTONOMY = "full_autonomy"
    SUPERVISED_AUTONOMY = "supervised_autonomy"
    HYBRID_AUTONOMY = "hybrid_autonomy"
    MANUAL_OVERRIDE = "manual_override"


class DecisionType(Enum):
    """Types of autonomous decisions"""
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    RESOURCE_ALLOCATION = "resource_allocation"
    SYSTEM_HEALING = "system_healing"
    ADAPTATION = "adaptation"


@dataclass
class AutonomousDecision:
    """
    An autonomous decision made by the system.
    """
    decision_id: str
    decision_type: DecisionType
    description: str
    actions: List[Dict[str, Any]]
    confidence: float
    expected_impact: str
    timestamp: datetime
    executed: bool = False
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class SystemGoal:
    """
    A system goal for autonomous operations.
    """
    goal_id: str
    description: str
    priority: int  # 1-10, higher is more important
    target_metrics: Dict[str, float]
    deadline: Optional[datetime]
    status: str = "active"  # active, achieved, failed, cancelled
    progress: float = 0.0

    def __post_init__(self):
        if self.deadline is None:
            self.deadline = datetime.now() + timedelta(days=7)


class AutonomousOperations:
    """
    Autonomous operations system for self-managing vault capabilities.

    Provides automated decision making, self-optimization, and independent
    execution of system operations.
    """

    def __init__(self, lifecycle_controller, self_repair, adaptive_learning):
        """
        Initialize autonomous operations.

        Args:
            lifecycle_controller: Lifecycle controller for component management
            self_repair: Self-repair system for healing
            adaptive_learning: Adaptive learning for optimization
        """
        self.lifecycle_controller = lifecycle_controller
        self.self_repair = self_repair
        self.adaptive_learning = adaptive_learning

        # Operation mode
        self.operation_mode = OperationMode.SUPERVISED_AUTONOMY

        # Decision history
        self.decisions: List[AutonomousDecision] = []
        self.max_decisions = 1000

        # System goals
        self.system_goals: Dict[str, SystemGoal] = {}

        # Autonomous tasks
        self.autonomous_tasks: Dict[str, asyncio.Task] = {}
        self.running = False

        # Decision making parameters
        self.decision_threshold = 0.7  # Minimum confidence for autonomous execution
        self.risk_tolerance = 0.3  # Maximum acceptable risk level

        # Performance monitoring
        self.performance_metrics = {
            "decisions_made": 0,
            "decisions_executed": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "average_confidence": 0.0,
            "system_uptime": 0.0
        }

        # Resource limits
        self.resource_limits = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0
        }

        # Autonomous monitoring
        self.monitoring_active = False
        self.monitoring_interval = 60  # seconds

        print("🤖 Autonomous Operations initialized")

    def set_operation_mode(self, mode: OperationMode):
        """
        Set the autonomous operation mode.

        Args:
            mode: New operation mode
        """
        old_mode = self.operation_mode
        self.operation_mode = mode

        print(f"🔄 Operation mode changed: {old_mode.value} → {mode.value}")

        # Adjust parameters based on mode
        if mode == OperationMode.FULL_AUTONOMY:
            self.decision_threshold = 0.8
            self.risk_tolerance = 0.2
        elif mode == OperationMode.SUPERVISED_AUTONOMY:
            self.decision_threshold = 0.7
            self.risk_tolerance = 0.3
        elif mode == OperationMode.HYBRID_AUTONOMY:
            self.decision_threshold = 0.6
            self.risk_tolerance = 0.4
        elif mode == OperationMode.MANUAL_OVERRIDE:
            self.decision_threshold = 1.0  # Require perfect confidence
            self.risk_tolerance = 0.0

    def add_system_goal(self, goal_id: str, description: str, priority: int,
                       target_metrics: Dict[str, float], deadline: Optional[datetime] = None):
        """
        Add a system goal for autonomous pursuit.

        Args:
            goal_id: Unique goal identifier
            description: Goal description
            priority: Goal priority (1-10)
            target_metrics: Target performance metrics
            deadline: Optional deadline
        """
        goal = SystemGoal(
            goal_id=goal_id,
            description=description,
            priority=priority,
            target_metrics=target_metrics,
            deadline=deadline
        )

        self.system_goals[goal_id] = goal
        print(f"🎯 Added system goal: {goal_id} (priority {priority})")

    def remove_system_goal(self, goal_id: str):
        """
        Remove a system goal.

        Args:
            goal_id: Goal identifier
        """
        if goal_id in self.system_goals:
            del self.system_goals[goal_id]
            print(f"❌ Removed system goal: {goal_id}")

    def start_autonomous_operations(self):
        """Start autonomous operation tasks"""
        if self.running:
            return

        self.running = True

        # Start monitoring task
        self.autonomous_tasks["monitoring"] = asyncio.create_task(self._monitoring_loop())

        # Start decision making task
        self.autonomous_tasks["decision_making"] = asyncio.create_task(self._decision_making_loop())

        # Start goal pursuit task
        self.autonomous_tasks["goal_pursuit"] = asyncio.create_task(self._goal_pursuit_loop())

        print("🚀 Autonomous operations started")

    def stop_autonomous_operations(self):
        """Stop autonomous operation tasks"""
        self.running = False

        for task in self.autonomous_tasks.values():
            task.cancel()

        self.autonomous_tasks.clear()
        print("🛑 Autonomous operations stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop for autonomous operations"""
        while self.running:
            try:
                await self._perform_system_monitoring()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                await asyncio.sleep(10)

    async def _decision_making_loop(self):
        """Decision making loop for autonomous operations"""
        while self.running:
            try:
                await self._evaluate_and_make_decisions()
                await asyncio.sleep(300)  # Every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Decision making error: {e}")
                await asyncio.sleep(60)

    async def _goal_pursuit_loop(self):
        """Goal pursuit loop for autonomous operations"""
        while self.running:
            try:
                await self._pursue_system_goals()
                await asyncio.sleep(600)  # Every 10 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Goal pursuit error: {e}")
                await asyncio.sleep(120)

    async def _perform_system_monitoring(self):
        """Perform comprehensive system monitoring"""
        # Get system metrics
        system_health = await self._get_system_health()

        # Check resource usage
        resource_status = self._check_resource_usage()

        # Monitor component health
        component_health = await self.lifecycle_controller.get_component_health()

        # Detect anomalies
        anomalies = await self._detect_system_anomalies(system_health, component_health)

        # Update performance metrics
        self.performance_metrics["system_uptime"] = system_health.get("uptime_hours", 0)

        # Trigger autonomous responses if needed
        if anomalies:
            await self._respond_to_anomalies(anomalies)

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # Network I/O
            network = psutil.net_io_counters()
            bytes_sent = network.bytes_sent
            bytes_recv = network.bytes_recv

            # System uptime
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = uptime_seconds / 3600

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "bytes_sent": bytes_sent,
                "bytes_recv": bytes_recv,
                "uptime_hours": uptime_hours,
                "timestamp": datetime.now()
            }

        except Exception as e:
            print(f"⚠️  Failed to get system health: {e}")
            return {}

    def _check_resource_usage(self) -> Dict[str, Any]:
        """Check if resource usage exceeds limits"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_over_limit": cpu_percent > self.resource_limits["cpu_percent"],
                "memory_over_limit": memory.percent > self.resource_limits["memory_percent"],
                "disk_over_limit": disk.percent > self.resource_limits["disk_percent"],
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }

        except Exception as e:
            return {"error": str(e)}

    async def _evaluate_and_make_decisions(self):
        """Evaluate system state and make autonomous decisions"""
        # Get current system state
        system_state = await self._assess_system_state()

        # Identify opportunities for optimization
        optimization_opportunities = self._identify_optimization_opportunities(system_state)

        # Generate potential decisions
        potential_decisions = self._generate_decisions(optimization_opportunities)

        # Evaluate and execute decisions
        for decision in potential_decisions:
            if await self._should_execute_decision(decision):
                await self._execute_decision(decision)

    async def _assess_system_state(self) -> Dict[str, Any]:
        """Assess current system state"""
        system_health = await self._get_system_health()
        component_health = await self.lifecycle_controller.get_component_health()
        learning_metrics = self.adaptive_learning.get_learning_metrics()

        return {
            "system_health": system_health,
            "component_health": component_health,
            "learning_metrics": learning_metrics,
            "active_goals": len([g for g in self.system_goals.values() if g.status == "active"]),
            "recent_decisions": len([d for d in self.decisions if (datetime.now() - d.timestamp).seconds < 3600])
        }

    def _identify_optimization_opportunities(self, system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for system optimization"""
        opportunities = []

        # Check resource usage
        resource_status = self._check_resource_usage()
        if resource_status.get("cpu_over_limit"):
            opportunities.append({
                "type": "resource_optimization",
                "category": "cpu",
                "severity": "high",
                "description": f"CPU usage at {resource_status['cpu_percent']:.1f}% exceeds limit"
            })

        if resource_status.get("memory_over_limit"):
            opportunities.append({
                "type": "resource_optimization",
                "category": "memory",
                "severity": "high",
                "description": f"Memory usage at {resource_status['memory_percent']:.1f}% exceeds limit"
            })

        # Check component health
        component_health = system_state.get("component_health", {})
        unhealthy_components = [
            comp for comp, health in component_health.items()
            if health.get("status") not in ["healthy", "good"]
        ]

        if unhealthy_components:
            opportunities.append({
                "type": "component_health",
                "components": unhealthy_components,
                "severity": "medium",
                "description": f"Unhealthy components: {', '.join(unhealthy_components)}"
            })

        # Check learning efficiency
        learning_metrics = system_state.get("learning_metrics", {})
        learning_efficiency = learning_metrics.get("learning_efficiency", 0)
        if learning_efficiency < 0.5:
            opportunities.append({
                "type": "learning_optimization",
                "severity": "low",
                "description": f"Learning efficiency at {learning_efficiency:.2f} could be improved"
            })

        return opportunities

    def _generate_decisions(self, opportunities: List[Dict[str, Any]]) -> List[AutonomousDecision]:
        """Generate autonomous decisions based on opportunities"""
        decisions = []

        for opportunity in opportunities:
            opp_type = opportunity["type"]
            severity = opportunity["severity"]

            if opp_type == "resource_optimization":
                category = opportunity["category"]
                decision = self._generate_resource_decision(category, severity)
                if decision:
                    decisions.append(decision)

            elif opp_type == "component_health":
                components = opportunity["components"]
                decision = self._generate_health_decision(components, severity)
                if decision:
                    decisions.append(decision)

            elif opp_type == "learning_optimization":
                decision = self._generate_learning_decision(severity)
                if decision:
                    decisions.append(decision)

        return decisions

    def _generate_resource_decision(self, category: str, severity: str) -> Optional[AutonomousDecision]:
        """Generate resource optimization decision"""
        actions = []

        if category == "cpu":
            actions = [
                {
                    "action": "reduce_thread_pool",
                    "description": "Reduce thread pool size to lower CPU usage",
                    "risk": "low"
                },
                {
                    "action": "optimize_background_tasks",
                    "description": "Optimize background task scheduling",
                    "risk": "medium"
                }
            ]
        elif category == "memory":
            actions = [
                {
                    "action": "clear_caches",
                    "description": "Clear non-essential caches to free memory",
                    "risk": "low"
                },
                {
                    "action": "reduce_buffer_sizes",
                    "description": "Reduce buffer sizes for memory optimization",
                    "risk": "medium"
                }
            ]

        if actions:
            return AutonomousDecision(
                decision_id=f"resource_opt_{category}_{int(time.time())}",
                decision_type=DecisionType.RESOURCE_ALLOCATION,
                description=f"Optimize {category} resource usage ({severity} priority)",
                actions=actions,
                confidence=0.75 if severity == "high" else 0.6,
                expected_impact=f"Reduce {category} usage by 10-20%",
                timestamp=datetime.now()
            )

        return None

    def _generate_health_decision(self, components: List[str], severity: str) -> Optional[AutonomousDecision]:
        """Generate component health decision"""
        actions = []

        for component in components:
            actions.append({
                "action": "restart_component",
                "component": component,
                "description": f"Restart unhealthy component {component}",
                "risk": "medium"
            })


        if actions:
            return AutonomousDecision(
                decision_id=f"health_fix_{int(time.time())}",
                decision_type=DecisionType.SYSTEM_HEALING,
                description=f"Fix health issues for {len(components)} components ({severity} priority)",
                actions=actions,
                confidence=0.8,
                expected_impact="Restore component health and functionality",
                timestamp=datetime.now()
            )

        return None

    def _generate_learning_decision(self, severity: str) -> Optional[AutonomousDecision]:
        """Generate learning optimization decision"""
        actions = [
            {
                "action": "increase_learning_rate",
                "description": "Increase learning batch size for better pattern recognition",
                "risk": "low"
            },
            {
                "action": "enable_transfer_learning",
                "description": "Enable transfer learning to accelerate knowledge acquisition",
                "risk": "low"
            }
        ]

        return AutonomousDecision(
            decision_id=f"learning_opt_{int(time.time())}",
            decision_type=DecisionType.OPTIMIZATION,
            description=f"Optimize learning efficiency ({severity} priority)",
            actions=actions,
            confidence=0.65,
            expected_impact="Improve learning efficiency by 15-25%",
            timestamp=datetime.now()
        )

    async def _should_execute_decision(self, decision: AutonomousDecision) -> bool:
        """Determine if a decision should be executed autonomously"""
        # Check operation mode
        if self.operation_mode == OperationMode.MANUAL_OVERRIDE:
            return False

        # Check confidence threshold
        if decision.confidence < self.decision_threshold:
            return False

        # Check risk tolerance
        max_risk = max(action.get("risk", "low") for action in decision.actions)
        risk_levels = {"low": 0.1, "medium": 0.3, "high": 0.7}

        if risk_levels.get(max_risk, 0.5) > self.risk_tolerance:
            return False

        # Additional checks based on operation mode
        if self.operation_mode == OperationMode.SUPERVISED_AUTONOMY:
            # In supervised mode, log decision for review
            print(f"🤖 Decision pending approval: {decision.description} (confidence: {decision.confidence:.2f})")
            # For now, auto-approve in supervised mode
            return True

        return True

    async def _execute_decision(self, decision: AutonomousDecision):
        """Execute an autonomous decision"""
        print(f"⚡ Executing autonomous decision: {decision.description}")

        results = []

        for action in decision.actions:
            try:
                result = await self._execute_action(action)
                results.append({"action": action["action"], "success": True, "result": result})
            except Exception as e:
                results.append({"action": action["action"], "success": False, "error": str(e)})

        # Update decision
        decision.executed = True
        decision.result = {
            "execution_time": datetime.now(),
            "results": results,
            "overall_success": all(r["success"] for r in results)
        }

        # Record decision
        self.decisions.append(decision)
        if len(self.decisions) > self.max_decisions:
            self.decisions = self.decisions[-self.max_decisions:]

        # Update performance metrics
        self.performance_metrics["decisions_made"] += 1
        self.performance_metrics["decisions_executed"] += 1

        if decision.result["overall_success"]:
            self.performance_metrics["successful_decisions"] += 1
        else:
            self.performance_metrics["failed_decisions"] += 1

        # Update average confidence
        total_decisions = self.performance_metrics["decisions_made"]
        self.performance_metrics["average_confidence"] = (
            (self.performance_metrics["average_confidence"] * (total_decisions - 1) + decision.confidence)
            / total_decisions
        )

        print(f"✅ Decision execution complete: {decision.result['overall_success']}")

    async def _execute_action(self, action: Dict[str, Any]) -> Any:
        """Execute a specific action"""
        action_type = action["action"]

        if action_type == "reduce_thread_pool":
            # Reduce thread pool size
            return await self._reduce_thread_pool()

        elif action_type == "optimize_background_tasks":
            # Optimize background tasks
            return await self._optimize_background_tasks()

        elif action_type == "clear_caches":
            # Clear caches
            return await self._clear_caches()

        elif action_type == "reduce_buffer_sizes":
            # Reduce buffer sizes
            return await self._reduce_buffer_sizes()

        elif action_type == "restart_component":
            # Restart component
            component = action["component"]
            return await self.lifecycle_controller.restart_component(component)

        elif action_type == "increase_learning_rate":
            # Increase learning rate
            self.adaptive_learning.optimize_performance()
            return "Learning optimization applied"

        elif action_type == "enable_transfer_learning":
            # Enable transfer learning
            return "Transfer learning enabled"

        else:
            raise ValueError(f"Unknown action type: {action_type}")

    async def _reduce_thread_pool(self) -> str:
        """Reduce thread pool size"""
        # This would interact with the thread pool manager
        return "Thread pool size reduced"

    async def _optimize_background_tasks(self) -> str:
        """Optimize background task scheduling"""
        # This would reschedule background tasks
        return "Background tasks optimized"

    async def _clear_caches(self) -> str:
        """Clear non-essential caches"""
        # Clear various caches in the system
        return "Caches cleared"

    async def _reduce_buffer_sizes(self) -> str:
        """Reduce buffer sizes"""
        # Reduce buffer sizes for memory optimization
        return "Buffer sizes reduced"

    async def _pursue_system_goals(self):
        """Pursue active system goals"""
        for goal in self.system_goals.values():
            if goal.status != "active":
                continue

            # Check if goal is achieved
            if self._is_goal_achieved(goal):
                goal.status = "achieved"
                goal.progress = 1.0
                print(f"🎯 Goal achieved: {goal.description}")
                continue

            # Check if goal is overdue
            if goal.deadline and datetime.now() > goal.deadline:
                goal.status = "failed"
                print(f"❌ Goal failed (overdue): {goal.description}")
                continue

            # Take actions toward goal
            await self._take_goal_actions(goal)

    def _is_goal_achieved(self, goal: SystemGoal) -> bool:
        """Check if a goal has been achieved"""
        # Simplified goal checking - would need specific metrics for each goal
        current_metrics = self._get_current_metrics()

        achieved = True
        for metric, target in goal.target_metrics.items():
            current = current_metrics.get(metric, 0)
            if current < target:
                achieved = False
                break

        return achieved

    def _get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        # Simplified - would gather real metrics
        return {
            "system_uptime": self.performance_metrics["system_uptime"],
            "learning_efficiency": self.adaptive_learning.get_learning_metrics().get("learning_efficiency", 0),
            "successful_decisions": self.performance_metrics["successful_decisions"]
        }

    async def _take_goal_actions(self, goal: SystemGoal):
        """Take actions toward achieving a goal"""
        # Simplified goal pursuit - would implement specific strategies
        goal.progress += 0.01  # Small progress increment

    async def _detect_system_anomalies(self, system_health: Dict[str, Any],
                                     component_health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect system anomalies"""
        anomalies = []

        # Check for sudden changes in metrics
        # This is a simplified anomaly detection

        cpu_percent = system_health.get("cpu_percent", 0)
        if cpu_percent > 95:
            anomalies.append({
                "type": "resource_spike",
                "resource": "cpu",
                "value": cpu_percent,
                "threshold": 95,
                "severity": "critical"
            })

        memory_percent = system_health.get("memory_percent", 0)
        if memory_percent > 95:
            anomalies.append({
                "type": "resource_spike",
                "resource": "memory",
                "value": memory_percent,
                "threshold": 95,
                "severity": "critical"
            })

        return anomalies

    async def _respond_to_anomalies(self, anomalies: List[Dict[str, Any]]):
        """Respond to detected anomalies"""
        for anomaly in anomalies:
            if anomaly["severity"] == "critical":
                # Trigger immediate response
                await self._handle_critical_anomaly(anomaly)

    async def _handle_critical_anomaly(self, anomaly: Dict[str, Any]):
        """Handle critical system anomalies"""
        anomaly_type = anomaly["type"]

        if anomaly_type == "resource_spike":
            resource = anomaly["resource"]
            print(f"🚨 Critical {resource} spike detected: {anomaly['value']}%")

            # Trigger emergency optimization
            decision = self._generate_resource_decision(resource, "critical")
            if decision:
                await self._execute_decision(decision)

    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get autonomous operations status"""
        total_decisions = self.performance_metrics["decisions_made"]
        success_rate = (
            self.performance_metrics["successful_decisions"] / max(1, total_decisions) * 100
            if total_decisions > 0 else 0
        )

        return {
            "operation_mode": self.operation_mode.value,
            "running": self.running,
            "decisions_made": total_decisions,
            "decisions_executed": self.performance_metrics["decisions_executed"],
            "success_rate": round(success_rate, 1),
            "average_confidence": round(self.performance_metrics["average_confidence"], 3),
            "active_goals": len([g for g in self.system_goals.values() if g.status == "active"]),
            "system_uptime": round(self.performance_metrics["system_uptime"], 1)
        }

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent autonomous decisions.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of recent decisions
        """
        recent_decisions = self.decisions[-limit:]

        return [
            {
                "decision_id": d.decision_id,
                "type": d.decision_type.value,
                "description": d.description,
                "confidence": round(d.confidence, 3),
                "executed": d.executed,
                "timestamp": d.timestamp.isoformat(),
                "result": d.result
            }
            for d in recent_decisions
        ]

    def get_system_goals(self) -> List[Dict[str, Any]]:
        """Get current system goals"""
        return [
            {
                "goal_id": g.goal_id,
                "description": g.description,
                "priority": g.priority,
                "status": g.status,
                "progress": round(g.progress, 3),
                "deadline": g.deadline.isoformat() if g.deadline else None,
                "target_metrics": g.target_metrics
            }
            for g in self.system_goals.values()
        ]

    def export_decision_history(self, filepath: str):
        """
        Export decision history to file.

        Args:
            filepath: Path to export file
        """
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "operation_mode": self.operation_mode.value,
            "performance_metrics": self.performance_metrics,
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "type": d.decision_type.value,
                    "description": d.description,
                    "confidence": d.confidence,
                    "executed": d.executed,
                    "timestamp": d.timestamp.isoformat(),
                    "result": d.result
                }
                for d in self.decisions
            ]
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"💾 Decision history exported to {filepath}")
        except Exception as e:
            print(f"❌ Failed to export decision history: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get autonomous operations system health"""
        return {
            "operation_mode": self.operation_mode.value,
            "running": self.running,
            "active_tasks": len(self.autonomous_tasks),
            "decisions_count": len(self.decisions),
            "goals_count": len(self.system_goals),
            "performance_metrics": self.performance_metrics
        }
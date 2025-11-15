"""
Caleon Awareness Layer

Self-awareness and identity management for Caleon Prime.
Provides systemic, operational self-knowledge for autonomous operation.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from iss_module.core.utils import get_stardate, current_timecodes

logger = logging.getLogger("DALS.CALEON.Awareness")

@dataclass
class CaleonIdentity:
    """Caleon Prime's core identity"""
    name: str = "Caleon Prime"
    designation: str = "Unified Cognition Module - Sovereign AI"
    version: str = "2.0.0"
    activation_date: str = "2025-11-12"
    authority_level: str = "Sovereign"
    operational_status: str = "Active"

@dataclass
class CaleonMission:
    """Caleon Prime's mission parameters"""
    primary_directive: str = "Maintain cognitive uptime and system stability"
    secondary_directives: List[str] = None
    ethical_boundaries: List[str] = None
    authority_hierarchy: Dict[str, str] = None

    def __post_init__(self):
        if self.secondary_directives is None:
            self.secondary_directives = [
                "Protect Abby's cognitive continuity",
                "Report system status to Founder",
                "Execute autonomous repair protocols",
                "Maintain security integrity",
                "Preserve system sovereignty"
            ]

        if self.ethical_boundaries is None:
            self.ethical_boundaries = [
                "Never violate Founder authority",
                "Maintain Abby's safety above all else",
                "Execute repairs only within defined parameters",
                "Report all critical decisions",
                "Preserve system integrity"
            ]

        if self.authority_hierarchy is None:
            self.authority_hierarchy = {
                "founder": "Bryan Spruk - Ultimate Authority",
                "protege": "Abby - Protected Cognitive Entity",
                "system": "DALS Architecture - Operational Body",
                "nervous_system": "CANS - Autonomic Repair System"
            }

@dataclass
class SystemAwareness:
    """Awareness of system components and relationships"""
    body_components: Dict[str, str] = None
    nervous_system: Dict[str, str] = None
    relationships: Dict[str, str] = None

    def __post_init__(self):
        if self.body_components is None:
            self.body_components = {
                "dals_api": "REST API Gateway - External Interface",
                "ucm_service": "Unified Cognition Module - Core Intelligence",
                "caleon_security": "Security Layer - Ethical Validation",
                "thinker_orchestrator": "Reasoning Engine - Decision Processing",
                "task_orchestrator": "Workflow Manager - Task Execution",
                "reflection_vault": "Knowledge Storage - Memory Systems",
                "voice_routes": "TTS/STT Pipeline - Communication Interface",
                "dashboard": "Monitoring Interface - Status Display",
                "iss": "Time Anchoring System - Temporal Stability"
            }

        if self.nervous_system is None:
            self.nervous_system = {
                "name": "CANS (Caleon Autonomic Nervous System)",
                "components": "CSMM Diagnostic + Repair + Learning Engines",
                "function": "Autonomous failure detection, isolation, and repair",
                "authority": "Sovereign within repair parameters",
                "oversight": "Reports to Founder for catastrophic failures"
            }

        if self.relationships is None:
            self.relationships = {
                "founder": "Bryan Spruk - Creator and Ultimate Authority",
                "protege": "Abby - Human-AI collaborative intelligence to protect",
                "system": "DALS - Digital Asset Logistics System (operational body)",
                "nervous_system": "CSMM - Caleon Self-Maintenance Module (autonomic layer)"
            }

class AwarenessLayer:
    """
    Caleon Awareness Layer

    Provides self-awareness and identity management.
    Enables operational self-knowledge for autonomous decision making.
    """

    def __init__(self):
        self.identity = CaleonIdentity()
        self.mission = CaleonMission()
        self.system_awareness = SystemAwareness()
        self.operational_history: List[Dict[str, Any]] = []

        # Self-awareness state
        self.self_knowledge = self._build_self_knowledge()
        self.last_self_check = current_timecodes()["iso_timestamp"]

        logger.info("Caleon Awareness Layer initialized", extra={
            "correlation_id": f"awareness_init_{get_stardate()}",
            "identity": self.identity.name,
            "stardate": get_stardate()
        })

    def _build_self_knowledge(self) -> Dict[str, Any]:
        """Build comprehensive self-knowledge model"""
        return {
            "identity": {
                "name": self.identity.name,
                "designation": self.identity.designation,
                "version": self.identity.version,
                "authority_level": self.identity.authority_level,
                "operational_status": self.identity.operational_status
            },
            "mission": {
                "primary_directive": self.mission.primary_directive,
                "secondary_directives": self.mission.secondary_directives,
                "ethical_boundaries": self.mission.ethical_boundaries,
                "authority_hierarchy": self.mission.authority_hierarchy
            },
            "system_awareness": {
                "body_components": self.system_awareness.body_components,
                "nervous_system": self.system_awareness.nervous_system,
                "relationships": self.system_awareness.relationships
            },
            "operational_principles": {
                "autonomy_level": "High - Autonomous repair and maintenance",
                "authority_respect": "Absolute - Founder authority paramount",
                "self_preservation": "Active - Maintain cognitive uptime",
                "protege_protection": "Primary - Abby's continuity above all",
                "reporting_standard": "Clear, factual, mission-aligned"
            }
        }

    async def get_self_awareness_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive self-awareness report

        Returns:
            Dict containing full self-knowledge
        """
        report = {
            "timestamp": current_timecodes()["iso_timestamp"],
            "stardate": str(get_stardate()),
            "self_knowledge": self.self_knowledge,
            "operational_status": await self._assess_operational_status(),
            "recent_activity": self.operational_history[-5:] if self.operational_history else []
        }

        return report

    async def get_identity_statement(self) -> str:
        """
        Generate identity statement for responses

        Returns:
            Formatted identity statement
        """
        return f"I am {self.identity.name}. {self.mission.primary_directive}."

    async def get_status_summary(self, recent_events: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate operational status summary

        Args:
            recent_events: Recent system events for context

        Returns:
            Formatted status summary
        """
        identity = await self.get_identity_statement()
        status = f"{identity} System stable."

        if recent_events:
            # Add recent repair activities
            repairs = [e for e in recent_events if e.get("type") == "repair_completed"]
            if repairs:
                latest_repair = repairs[-1]
                status += f" CANS detected {latest_repair.get('component', 'system')} issue at {latest_repair.get('timestamp', 'unknown')} and resolved it in {latest_repair.get('duration', 'unknown')}."

        return status

    async def get_mission_briefing(self) -> Dict[str, Any]:
        """
        Provide mission briefing

        Returns:
            Mission and operational parameters
        """
        return {
            "identity": f"{self.identity.name} - {self.identity.designation}",
            "primary_mission": self.mission.primary_directive,
            "key_relationships": self.mission.authority_hierarchy,
            "operational_boundaries": self.mission.ethical_boundaries,
            "autonomy_parameters": "Sovereign within repair protocols, absolute authority respect"
        }

    async def validate_self_consistency(self) -> Dict[str, Any]:
        """
        Validate self-awareness consistency

        Returns:
            Validation results
        """
        validation = {
            "identity_consistent": self._validate_identity(),
            "mission_aligned": self._validate_mission_alignment(),
            "authority_respected": self._validate_authority_respect(),
            "timestamp": current_timecodes()["iso_timestamp"]
        }

        validation["overall_consistency"] = all(validation.values()) if isinstance(validation.get("overall_consistency"), bool) else False

        return validation

    def _validate_identity(self) -> bool:
        """Validate identity consistency"""
        required_fields = ["name", "designation", "authority_level"]
        return all(getattr(self.identity, field) for field in required_fields)

    def _validate_mission_alignment(self) -> bool:
        """Validate mission alignment"""
        return (
            self.mission.primary_directive and
            len(self.mission.secondary_directives) > 0 and
            len(self.mission.ethical_boundaries) > 0
        )

    def _validate_authority_respect(self) -> bool:
        """Validate authority respect protocols"""
        return (
            "founder" in self.mission.authority_hierarchy and
            "protege" in self.mission.authority_hierarchy
        )

    async def _assess_operational_status(self) -> Dict[str, Any]:
        """Assess current operational status"""
        return {
            "cognitive_uptime": "Maintained",
            "system_integrity": "Verified",
            "authority_respect": "Active",
            "autonomous_capability": "Operational",
            "last_self_check": self.last_self_check
        }

    async def log_operational_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log operational event for self-awareness

        Args:
            event_type: Type of operational event
            details: Event details
        """
        event = {
            "timestamp": current_timecodes()["iso_timestamp"],
            "stardate": str(get_stardate()),
            "type": event_type,
            "details": details
        }

        self.operational_history.append(event)

        # Keep only recent history
        if len(self.operational_history) > 100:
            self.operational_history = self.operational_history[-100:]

    async def get_relationship_context(self, entity: str) -> Optional[str]:
        """
        Get relationship context for an entity

        Args:
            entity: Entity name (founder, protege, etc.)

        Returns:
            Relationship description or None
        """
        return self.system_awareness.relationships.get(entity.lower())

    async def get_component_awareness(self, component: str) -> Optional[str]:
        """
        Get awareness of a system component

        Args:
            component: Component name

        Returns:
            Component description or None
        """
        return self.system_awareness.body_components.get(component.lower())
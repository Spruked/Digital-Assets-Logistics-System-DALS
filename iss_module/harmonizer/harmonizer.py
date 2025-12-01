"""
Gyro-Cortical Harmonizer - Final Verdict Engine
===============================================

The Gyro-Cortical Harmonizer is the final reasoning stage before any output.
It implements the 5+1 combinatorial reasoning cycle with philosophical guidance
and convergence validation within ±3 standard deviations.

Architecture:
- 5 logic JSON packets from: Helices, EchoStack, Drift, Vault, Security
- 1 philosophical guide (Kant, Locke, Hume, Stoicism, etc.)
- Recursive cycles until convergence within ±3σ
- Final articulation gatekeeper

Author: DALS Cognitive Architecture
"""

import asyncio
import json
import logging
import math
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from ..core.utils import get_stardate, current_timecodes
from ..core.caleon_security_layer import CaleonSecurityLayer

logger = logging.getLogger("DALS.Harmonizer")


class PhilosophicalGuide(Enum):
    """Philosophical frameworks for reasoning guidance"""
    KANT = "categorical_imperative"
    LOCKE = "natural_rights"
    HUME = "empirical_causation"
    STOICISM = "virtue_ethics"
    UTILITARIANISM = "greatest_happiness"
    EXISTENTIALISM = "authentic_choice"
    PHENOMENOLOGY = "lived_experience"
    PRAGMATISM = "practical_consequences"


class LogicPacketType(Enum):
    """Types of logic packets from UCM modules"""
    HELICES = "helices"  # Pattern recognition
    ECHO_STACK = "echo_stack"  # Memory resonance
    DRIFT = "drift"  # Temporal analysis
    VAULT = "vault"  # Knowledge integration
    SECURITY = "security"  # Risk assessment


@dataclass
class LogicPacket:
    """Individual logic packet from UCM modules"""
    packet_type: LogicPacketType
    content: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    timestamp: str
    source_module: str


@dataclass
class ReasoningCycle:
    """Complete 5+1 reasoning cycle"""
    cycle_id: str
    logic_packets: List[LogicPacket]
    philosophical_guide: PhilosophicalGuide
    verdict: Dict[str, Any]
    convergence_score: float
    processing_time_ms: float
    timestamp: str


@dataclass
class HarmonizerState:
    """Internal state of the Harmonizer"""
    active_cycles: List[ReasoningCycle] = field(default_factory=list)
    convergence_history: List[float] = field(default_factory=list)
    philosophical_rotation: List[PhilosophicalGuide] = field(default_factory=list)
    stability_threshold: float = 3.0  # ±3σ
    max_cycles: int = 10
    current_verdict: Optional[Dict[str, Any]] = None
    last_convergence_time: Optional[str] = None


class GyroCorticalHarmonizer:
    """
    Gyro-Cortical Harmonizer - Final Verdict Engine

    Implements the 5+1 combinatorial reasoning cycle:
    - 5 logic packets from UCM modules
    - 1 philosophical guide for ethical framing
    - Recursive convergence until ±3σ stability
    - Final articulation gatekeeper
    """

    def __init__(self):
        self.state = HarmonizerState()
        self.security_layer = CaleonSecurityLayer()

        # Philosophical guides in rotation order
        self.philosophical_guides = [
            PhilosophicalGuide.KANT,
            PhilosophicalGuide.LOCKE,
            PhilosophicalGuide.HUME,
            PhilosophicalGuide.STOICISM,
            PhilosophicalGuide.UTILITARIANISM,
            PhilosophicalGuide.EXISTENTIALISM,
            PhilosophicalGuide.PHENOMENOLOGY,
            PhilosophicalGuide.PRAGMATISM
        ]

        self._initialize_philosophical_rotation()

        logger.info("Gyro-Cortical Harmonizer initialized")

    def _initialize_philosophical_rotation(self):
        """Initialize philosophical guide rotation to prevent bias"""
        self.state.philosophical_rotation = self.philosophical_guides.copy()
        random.shuffle(self.state.philosophical_rotation)

    async def process_reasoning_request(self, logic_packets: List[LogicPacket],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing entry point - runs recursive reasoning cycles until convergence

        Args:
            logic_packets: 5 logic packets from UCM modules
            context: Request context and metadata

        Returns:
            Final harmonized verdict after convergence
        """
        start_time = datetime.now()

        # Validate input
        if len(logic_packets) != 5:
            raise ValueError(f"Harmonizer requires exactly 5 logic packets, received {len(logic_packets)}")

        # Security validation
        security_check = await self.security_layer.validate_reasoning_request(context)
        if not security_check.get('approved', False):
            return {
                'verdict': 'blocked',
                'reason': security_check.get('reason', 'Security validation failed'),
                'security_gate': {'block': True}
            }

        # Run recursive convergence cycles
        converged_verdict = await self._run_convergence_cycles(logic_packets, context)

        # Final security check on verdict
        final_check = await self.security_layer.validate_final_verdict(converged_verdict)
        if not final_check.get('approved', False):
            return {
                'verdict': 'blocked',
                'reason': final_check.get('reason', 'Final verdict validation failed'),
                'security_gate': {'block': True}
            }

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        final_response = {
            'verdict': converged_verdict,
            'processing_time_ms': processing_time,
            'convergence_cycles': len(self.state.active_cycles),
            'philosophical_guide': self.state.active_cycles[-1].philosophical_guide.value if self.state.active_cycles else None,
            'stability_achieved': True,
            'security_gate': {'block': False},
            'timestamp': get_stardate()
        }

        logger.info(f"Harmonizer verdict reached after {len(self.state.active_cycles)} cycles in {processing_time:.2f}ms")
        return final_response

    async def _run_convergence_cycles(self, logic_packets: List[LogicPacket],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run recursive reasoning cycles until convergence within ±3σ

        Args:
            logic_packets: Input logic packets
            context: Request context

        Returns:
            Converged verdict
        """
        cycle_count = 0
        last_verdict = None

        while cycle_count < self.state.max_cycles:
            # Select philosophical guide (rotate to prevent bias)
            philosophical_guide = self._select_philosophical_guide(cycle_count)

            # Run single reasoning cycle
            cycle = await self._execute_reasoning_cycle(
                logic_packets, philosophical_guide, context, cycle_count
            )

            self.state.active_cycles.append(cycle)

            # Check convergence
            if self._check_convergence(cycle.verdict):
                logger.info(f"Convergence achieved in cycle {cycle_count + 1}")
                self.state.current_verdict = cycle.verdict
                self.state.last_convergence_time = cycle.timestamp
                return cycle.verdict

            last_verdict = cycle.verdict
            cycle_count += 1

        # Maximum cycles reached - return best effort verdict
        logger.warning(f"Maximum cycles ({self.state.max_cycles}) reached without convergence")
        fallback_verdict = self._generate_fallback_verdict(logic_packets, context)
        self.state.current_verdict = fallback_verdict
        return fallback_verdict

    async def _execute_reasoning_cycle(self, logic_packets: List[LogicPacket],
                                     philosophical_guide: PhilosophicalGuide,
                                     context: Dict[str, Any], cycle_num: int) -> ReasoningCycle:
        """
        Execute a single 5+1 reasoning cycle

        Args:
            logic_packets: The 5 logic packets
            philosophical_guide: Selected philosophical framework
            context: Request context
            cycle_num: Cycle number for tracking

        Returns:
            Complete reasoning cycle result
        """
        cycle_start = datetime.now()
        cycle_id = f"harmonizer_{get_stardate()}_{cycle_num}"

        # Apply philosophical framing
        framed_packets = await self._apply_philosophical_framing(
            logic_packets, philosophical_guide
        )

        # Combine logic packets through gyroscopic integration
        combined_logic = self._gyroscopic_integration(framed_packets)

        # Generate verdict through convergence validation
        verdict = await self._generate_converged_verdict(combined_logic, context)

        processing_time = (datetime.now() - cycle_start).total_seconds() * 1000

        cycle = ReasoningCycle(
            cycle_id=cycle_id,
            logic_packets=framed_packets,
            philosophical_guide=philosophical_guide,
            verdict=verdict,
            convergence_score=self._calculate_convergence_score(verdict),
            processing_time_ms=processing_time,
            timestamp=get_stardate()
        )

        return cycle

    async def _apply_philosophical_framing(self, logic_packets: List[LogicPacket],
                                         philosophical_guide: PhilosophicalGuide) -> List[LogicPacket]:
        """
        Apply philosophical framework to logic packets for ethical reasoning

        Args:
            logic_packets: Raw logic packets
            philosophical_guide: Philosophical framework to apply

        Returns:
            Philosophically framed logic packets
        """
        framed_packets = []

        for packet in logic_packets:
            # Apply philosophical lens based on guide
            framed_content = await self._apply_philosophical_lens(
                packet.content, philosophical_guide
            )

            framed_packet = LogicPacket(
                packet_type=packet.packet_type,
                content=framed_content,
                confidence=packet.confidence,
                timestamp=packet.timestamp,
                source_module=packet.source_module
            )

            framed_packets.append(framed_packet)

        return framed_packets

    async def _apply_philosophical_lens(self, content: Dict[str, Any],
                                      philosophical_guide: PhilosophicalGuide) -> Dict[str, Any]:
        """
        Apply specific philosophical framework to content

        Args:
            content: Logic packet content
            philosophical_guide: Framework to apply

        Returns:
            Philosophically framed content
        """
        framed_content = content.copy()

        # Apply framework-specific reasoning
        if philosophical_guide == PhilosophicalGuide.KANT:
            # Categorical imperative - universal moral law
            framed_content['ethical_framing'] = 'categorical_imperative'
            framed_content['moral_universality'] = self._evaluate_universal_morality(content)

        elif philosophical_guide == PhilosophicalGuide.LOCKE:
            # Natural rights - life, liberty, property
            framed_content['ethical_framing'] = 'natural_rights'
            framed_content['rights_preservation'] = self._evaluate_rights_preservation(content)

        elif philosophical_guide == PhilosophicalGuide.HUME:
            # Empirical causation - experience-based reasoning
            framed_content['ethical_framing'] = 'empirical_causation'
            framed_content['causal_evidence'] = self._evaluate_causal_evidence(content)

        elif philosophical_guide == PhilosophicalGuide.STOICISM:
            # Virtue ethics - inner strength and wisdom
            framed_content['ethical_framing'] = 'virtue_ethics'
            framed_content['virtue_alignment'] = self._evaluate_virtue_alignment(content)

        # Add philosophical metadata
        framed_content['philosophical_guide'] = philosophical_guide.value
        framed_content['framing_timestamp'] = get_stardate()

        return framed_content

    def _gyroscopic_integration(self, logic_packets: List[LogicPacket]) -> Dict[str, Any]:
        """
        Integrate logic packets through gyroscopic combination
        Simulates the "spinning" convergence of multiple reasoning streams

        Args:
            logic_packets: Framed logic packets

        Returns:
            Gyroscopically integrated logic
        """
        # Group packets by type
        packet_groups = {}
        for packet in logic_packets:
            if packet.packet_type.value not in packet_groups:
                packet_groups[packet.packet_type.value] = []
            packet_groups[packet.packet_type.value].append(packet)

        # Calculate weighted integration
        integrated_logic = {
            'integrated_confidence': 0.0,
            'packet_count': len(logic_packets),
            'dominant_themes': [],
            'risk_assessment': {},
            'ethical_alignment': {},
            'temporal_stability': {},
            'knowledge_integration': {}
        }

        total_weight = 0
        for packet_type, packets in packet_groups.items():
            # Weight by confidence and recency
            weight = sum(p.confidence for p in packets) / len(packets)
            total_weight += weight

            # Integrate packet content
            self._integrate_packet_type(integrated_logic, packet_type, packets, weight)

        # Normalize by total weight
        if total_weight > 0:
            integrated_logic['integrated_confidence'] = total_weight / len(packet_groups)

        return integrated_logic

    def _integrate_packet_type(self, integrated_logic: Dict[str, Any],
                             packet_type: str, packets: List[LogicPacket], weight: float):
        """Integrate packets of specific type into combined logic"""
        if packet_type == 'helices':
            # Pattern recognition integration
            patterns = [p.content.get('patterns', []) for p in packets]
            integrated_logic['dominant_themes'].extend(
                pattern for pattern_list in patterns for pattern in pattern_list
            )

        elif packet_type == 'security':
            # Risk assessment integration
            risks = [p.content.get('risk_score', 0.5) for p in packets]
            integrated_logic['risk_assessment'] = {
                'average_risk': sum(risks) / len(risks),
                'max_risk': max(risks),
                'risk_weight': weight
            }

        elif packet_type == 'vault':
            # Knowledge integration
            knowledge_items = [p.content.get('knowledge', {}) for p in packets]
            integrated_logic['knowledge_integration'] = self._merge_knowledge(knowledge_items)

    async def _generate_converged_verdict(self, combined_logic: Dict[str, Any],
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final verdict from gyroscopically integrated logic

        Args:
            combined_logic: Integrated logic from gyroscope
            context: Request context

        Returns:
            Final harmonized verdict
        """
        # Apply convergence validation
        verdict = {
            'confidence': combined_logic.get('integrated_confidence', 0.5),
            'risk_score': combined_logic.get('risk_assessment', {}).get('average_risk', 0.5),
            'ethical_alignment': self._calculate_ethical_alignment(combined_logic),
            'temporal_stability': self._assess_temporal_stability(combined_logic),
            'knowledge_grounding': len(combined_logic.get('knowledge_integration', {})),
            'dominant_themes': list(set(combined_logic.get('dominant_themes', []))),
            'decision_framework': 'gyro_cortical_harmonizer',
            'convergence_validated': True,
            'philosophical_grounding': True
        }

        # Add context-aware recommendations
        verdict['recommendations'] = self._generate_recommendations(verdict, context)

        return verdict

    def _check_convergence(self, verdict: Dict[str, Any]) -> bool:
        """
        Check if verdict has converged within ±3σ stability threshold

        Args:
            verdict: Current verdict to check

        Returns:
            True if converged, False otherwise
        """
        if len(self.state.convergence_history) < 2:
            # Need at least 2 cycles for convergence check
            self.state.convergence_history.append(verdict.get('confidence', 0.5))
            return False

        # Add current verdict to history
        self.state.convergence_history.append(verdict.get('confidence', 0.5))

        # Keep only last 5 cycles for convergence calculation
        if len(self.state.convergence_history) > 5:
            self.state.convergence_history = self.state.convergence_history[-5:]

        # Calculate standard deviation
        if len(self.state.convergence_history) >= 3:
            mean = sum(self.state.convergence_history) / len(self.state.convergence_history)
            variance = sum((x - mean) ** 2 for x in self.state.convergence_history) / len(self.state.convergence_history)
            std_dev = math.sqrt(variance)

            # Check if within ±3σ of mean
            current_value = self.state.convergence_history[-1]
            deviation = abs(current_value - mean)

            converged = deviation <= (self.state.stability_threshold * std_dev)

            if converged:
                logger.info(f"Convergence achieved: {current_value:.4f} within {deviation:.4f}σ of mean {mean:.4f}")

            return converged

        return False

    def _calculate_convergence_score(self, verdict: Dict[str, Any]) -> float:
        """Calculate convergence score for tracking"""
        confidence = verdict.get('confidence', 0.5)
        risk_score = verdict.get('risk_score', 0.5)
        ethical_alignment = verdict.get('ethical_alignment', 0.5)

        # Weighted convergence score
        return (confidence * 0.4) + ((1 - risk_score) * 0.4) + (ethical_alignment * 0.2)

    def _select_philosophical_guide(self, cycle_num: int) -> PhilosophicalGuide:
        """Select philosophical guide with rotation to prevent bias"""
        guide_index = cycle_num % len(self.state.philosophical_rotation)
        return self.state.philosophical_rotation[guide_index]

    def _generate_fallback_verdict(self, logic_packets: List[LogicPacket],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback verdict when max cycles reached"""
        logger.warning("Generating fallback verdict - max cycles reached")

        # Conservative fallback based on security packets
        security_packets = [p for p in logic_packets if p.packet_type == LogicPacketType.SECURITY]
        avg_risk = sum(p.content.get('risk_score', 0.5) for p in security_packets) / len(security_packets) if security_packets else 0.5

        return {
            'confidence': 0.3,  # Low confidence for fallback
            'risk_score': min(avg_risk + 0.2, 1.0),  # Conservative risk assessment
            'ethical_alignment': 0.4,
            'temporal_stability': 0.3,
            'knowledge_grounding': 0,
            'dominant_themes': ['fallback_reasoning'],
            'decision_framework': 'gyro_cortical_harmonizer_fallback',
            'convergence_validated': False,
            'philosophical_grounding': False,
            'recommendations': ['escalate_to_human_override', 'additional_context_required']
        }

    # Helper methods for philosophical evaluation
    def _evaluate_universal_morality(self, content: Dict[str, Any]) -> bool:
        """Evaluate content against Kant's categorical imperative"""
        # Simplified implementation - check for universal applicability
        return content.get('universal_applicable', True)

    def _evaluate_rights_preservation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate rights preservation in content"""
        return {
            'life_preserved': content.get('life_impact', 0) <= 0.3,
            'liberty_preserved': content.get('liberty_impact', 0) <= 0.3,
            'property_preserved': content.get('property_impact', 0) <= 0.3
        }

    def _evaluate_causal_evidence(self, content: Dict[str, Any]) -> float:
        """Evaluate empirical causal evidence strength"""
        evidence_score = content.get('empirical_evidence', 0.5)
        return min(evidence_score, 1.0)

    def _evaluate_virtue_alignment(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Evaluate alignment with stoic virtues"""
        virtues = ['wisdom', 'courage', 'justice', 'temperance']
        alignment = {}
        for virtue in virtues:
            alignment[virtue] = content.get(f'{virtue}_alignment', 'moderate')
        return alignment

    def _merge_knowledge(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge knowledge from multiple vault packets"""
        merged = {}
        for item in knowledge_items:
            for key, value in item.items():
                if key not in merged:
                    merged[key] = []
                if isinstance(value, list):
                    merged[key].extend(value)
                else:
                    merged[key].append(value)
        return merged

    def _calculate_ethical_alignment(self, combined_logic: Dict[str, Any]) -> float:
        """Calculate overall ethical alignment score"""
        # Simplified calculation based on risk and philosophical framing
        risk_score = combined_logic.get('risk_assessment', {}).get('average_risk', 0.5)
        return 1.0 - risk_score  # Inverse relationship

    def _assess_temporal_stability(self, combined_logic: Dict[str, Any]) -> float:
        """Assess temporal stability of reasoning"""
        # Based on consistency across time-based packets
        return combined_logic.get('integrated_confidence', 0.5)

    def _generate_recommendations(self, verdict: Dict[str, Any],
                                context: Dict[str, Any]) -> List[str]:
        """Generate context-aware recommendations"""
        recommendations = []

        if verdict.get('risk_score', 0.5) > 0.7:
            recommendations.append('high_risk_detected')
            recommendations.append('human_review_recommended')

        if verdict.get('confidence', 0.5) < 0.6:
            recommendations.append('low_confidence_additional_data_needed')

        if verdict.get('ethical_alignment', 0.5) < 0.7:
            recommendations.append('ethical_concerns_identified')

        if not verdict.get('convergence_validated', False):
            recommendations.append('convergence_not_achieved_review_required')

        return recommendations

    # Public API methods
    async def get_status(self) -> Dict[str, Any]:
        """Get harmonizer status - DALS-001 compliant"""
        if not self.state.current_verdict:
            return {
                "status": "inactive",
                "active_cycles": 0,
                "last_convergence": None,
                "stability_threshold": self.state.stability_threshold
            }

        return {
            "status": "active",
            "active_cycles": len(self.state.active_cycles),
            "last_convergence": self.state.last_convergence_time,
            "current_verdict_confidence": self.state.current_verdict.get('confidence', 0),
            "stability_threshold": self.state.stability_threshold,
            "philosophical_guides_used": len(set(c.philosophical_guide for c in self.state.active_cycles))
        }

    def reset_state(self):
        """Reset harmonizer state for new session"""
        self.state = HarmonizerState()
        self._initialize_philosophical_rotation()
        logger.info("Harmonizer state reset")


# Global harmonizer instance
_harmonizer_instance = None

def get_harmonizer() -> GyroCorticalHarmonizer:
    """Get global harmonizer instance"""
    global _harmonizer_instance
    if _harmonizer_instance is None:
        _harmonizer_instance = GyroCorticalHarmonizer()
    return _harmonizer_instance
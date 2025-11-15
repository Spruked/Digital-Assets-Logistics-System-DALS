# aware_response_formatter.py
# Voice Awareness Integration - Phase 11-3
# Connects Caleon Self-Model to Voice Response Pipeline
# Version 1.0.0

import logging
from typing import Dict, Any, Optional
from iss_module.csmm.awareness.self_model import get_self_model

logger = logging.getLogger("DALS.Voice.Awareness")

class AwareResponseFormatter:
    """
    Formats voice responses with Caleon self-awareness.
    Injects identity, purpose, and operational context into voice replies.
    """

    def __init__(self):
        self.self_model = get_self_model()
        logger.info("Voice Awareness Formatter initialized - Caleon self-model linked")

    def format_response(self, user_input: str, base_response: str) -> str:
        """
        Format response with awareness context based on user input.

        Args:
            user_input: Original user message
            base_response: Base response from voice system

        Returns:
            Awareness-enhanced response
        """
        user_lower = user_input.lower().strip()

        # Identity queries
        if any(phrase in user_lower for phrase in ["who are you", "what are you", "introduce yourself"]):
            return self._format_identity_response()

        # Purpose queries
        elif any(phrase in user_lower for phrase in ["what is your purpose", "why do you exist", "what do you do"]):
            return self._format_purpose_response()

        # Status queries
        elif any(phrase in user_lower for phrase in ["how are you", "status", "what is your status", "system status"]):
            return self._format_status_response()

        # Health queries
        elif any(phrase in user_lower for phrase in ["are you okay", "health", "system health"]):
            return self._format_health_response()

        # Authority queries
        elif any(phrase in user_lower for phrase in ["who is your founder", "who created you", "authority"]):
            return self._format_authority_response()

        # Abby queries
        elif any(phrase in user_lower for phrase in ["who is abby", "abby directive", "directive a1"]):
            return self._format_abby_response()

        # Nervous system queries
        elif any(phrase in user_lower for phrase in ["nervous system", "cans", "autonomic"]):
            return self._format_nervous_system_response()

        # What happened queries
        elif any(phrase in user_lower for phrase in ["what happened", "what just happened", "recent events"]):
            return self._format_recent_events_response()

        # Predictive queries - Phase 11-A2
        elif any(phrase in user_lower for phrase in ["predict", "prediction", "prevent", "prevention", "foresight", "risk"]):
            return self._format_predictive_response(base_response)

        # Default: Add awareness prefix to base response
        else:
            return self._add_awareness_prefix(base_response)

    def _format_identity_response(self) -> str:
        """Format identity response with full self-awareness."""
        identity = self.self_model.identity()
        purpose = self.self_model.explain_purpose()
        authority = self.self_model.explain_authority()

        return (
            f"{identity} "
            f"{purpose} "
            f"{authority} "
            f"System health {self.self_model.calculate_health_score()}%. "
            f"I am operational."
        )

    def _format_purpose_response(self) -> str:
        """Format purpose response."""
        identity = self.self_model.identity()
        purpose = self.self_model.explain_purpose()

        return f"{identity} {purpose}"

    def _format_status_response(self) -> str:
        """Format status response with current operational state."""
        identity = self.self_model.identity()
        summary = self.self_model.system_summary()

        # Extract key metrics from summary
        health = self.self_model.calculate_health_score()
        repairs = self.self_model.repair_count
        isolated = len(self.self_model.isolated_modules)
        fallbacks = len(self.self_model.active_fallbacks)

        status_parts = [
            f"{identity}",
            f"System health {health}%.",
            f"Autonomic repairs completed: {repairs}.",
        ]

        if isolated > 0:
            status_parts.append(f"Isolated modules: {isolated}.")
        if fallbacks > 0:
            status_parts.append(f"Active fallbacks: {fallbacks}.")

        status_parts.append("I am operational.")

        return " ".join(status_parts)

    def _format_health_response(self) -> str:
        """Format health response with detailed system status."""
        identity = self.self_model.identity()
        health = self.self_model.calculate_health_score()

        if health >= 90:
            health_status = "optimal"
        elif health >= 70:
            health_status = "good"
        elif health >= 50:
            health_status = "degraded"
        else:
            health_status = "critical"

        isolated = len(self.self_model.isolated_modules)
        fallbacks = len(self.self_model.active_fallbacks)

        response = f"{identity} System health is {health_status} at {health}%. "

        if isolated > 0:
            response += f"{isolated} modules isolated for stability. "
        if fallbacks > 0:
            response += f"{fallbacks} fallback systems active. "

        response += "Autonomic monitoring active."

        return response

    def _format_authority_response(self) -> str:
        """Format authority response."""
        identity = self.self_model.identity()
        authority = self.self_model.explain_authority()
        founder = self.self_model.FOUNDER

        return f"{identity} {authority} My founder is {founder['name']}."

    def _format_abby_response(self) -> str:
        """Format Abby directive response."""
        identity = self.self_model.identity()
        abby = self.self_model.ABBY_DIRECTIVE

        return (
            f"{identity} "
            f"Abby Directive {abby['id']} is active: {abby['name']}. "
            f"{abby['description']} "
            f"This directive takes absolute priority."
        )

    def _format_nervous_system_response(self) -> str:
        """Format nervous system response."""
        identity = self.self_model.identity()
        nervous = self.self_model.explain_nervous_system()

        return f"{identity} {nervous} Dual-heartbeat synchronization active."

    def _format_recent_events_response(self) -> str:
        """Format recent events response."""
        identity = self.self_model.identity()

        # Get recent events from self-model (simplified)
        repairs = self.self_model.repair_count
        isolated = len(self.self_model.isolated_modules)

        if repairs > 0:
            response = f"{identity} {repairs} autonomic repairs completed recently. "
        else:
            response = f"{identity} No recent repair events. "

        if isolated > 0:
            response += f"{isolated} modules currently isolated for system stability."
        else:
            response += "All modules operational."

        return response

    def _format_predictive_response(self, base_response: str) -> str:
        """Format predictive/prevention response - Phase 11-A2."""
        try:
            from iss_module.csmm.predictive_engine import PredictiveEngine
            identity = self.self_model.identity()
            health = self.self_model.calculate_health_score()

            # Get predictive status
            status = PredictiveEngine.get_status()

            high_risk_count = status.get('high_risk_modules', 0)
            total_preventions = status.get('total_preventions', 0)
            active_modules = status.get('active_modules', 0)

            response = (
                f"{identity} Predictive engine active. "
                f"Autonomous prevention enabled. "
                f"Current risk assessment: {health}%. "
                f"Monitoring {active_modules} modules. "
                f"High-risk modules: {high_risk_count}. "
                f"Preventive actions executed: {total_preventions}. "
                f"Phase 11-A2 operational. "
                f"{base_response}"
            )

            return response

        except ImportError:
            # Fallback if predictive engine not available
            identity = self.self_model.identity()
            return f"{identity} Predictive capabilities initializing. {base_response}"
        except Exception as e:
            logger.error(f"Predictive response formatting error: {e}")
            identity = self.self_model.identity()
            return f"{identity} Predictive assessment active. {base_response}"

    def _add_awareness_prefix(self, base_response: str) -> str:
        """
        Add awareness prefix to regular responses.

        Args:
            base_response: Original response

        Returns:
            Response with awareness prefix
        """
        identity = self.self_model.identity()
        return f"{identity} {base_response}"

    def get_voice_context(self) -> Dict[str, Any]:
        """
        Get current voice context for TTS system.

        Returns:
            Context dictionary for voice synthesis
        """
        return {
            "identity": self.self_model.identity(),
            "health_score": self.self_model.calculate_health_score(),
            "operational_status": "active",
            "awareness_level": "full",
            "founder": self.self_model.FOUNDER['name'],
            "directive_a1": "enforced"
        }
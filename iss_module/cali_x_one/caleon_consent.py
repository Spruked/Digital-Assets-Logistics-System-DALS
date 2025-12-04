"""
Caleon Consent Manager - Voice-Activated Consent System
Integrates with Cali ethics gate for voice override capabilities.
"""

import asyncio
import logging
import requests
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

from .ethics_gate import CALI_ETHICS_URL

logger = logging.getLogger("caleon-consent")

class ConsentMode(Enum):
    """Consent acquisition modes"""
    ALWAYS_YES = "always_yes"  # For testing/development
    MANUAL = "manual"  # Requires explicit user approval
    VOICE = "voice"  # Voice-activated consent
    RANDOM = "random"  # Random approval (for testing)
    CONSENSUS = "consensus"  # Requires consensus from multiple sources

@dataclass
class ConsentRequest:
    """Represents a consent request"""
    action: str
    context: Dict[str, Any]
    risk_level: str  # "low", "medium", "high", "critical"
    timeout_seconds: int = 30

@dataclass
class ConsentResult:
    """Result of a consent request"""
    approved: bool
    method: str
    confidence: float
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = None

class CaleonConsentManager:
    """
    Manages consent acquisition with multiple modes including voice override.
    Integrates with Cali ethics gate for voice-activated approvals.
    """

    def __init__(self, mode: ConsentMode = ConsentMode.MANUAL):
        self.mode = mode
        self.voice_active = False
        self.ethics_gate_available = self._check_ethics_gate()

    def _check_ethics_gate(self) -> bool:
        """Check if Cali ethics gate is available."""
        try:
            response = requests.get(f"{CALI_ETHICS_URL}/health", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    async def get_consent(self, request: ConsentRequest) -> ConsentResult:
        """
        Get consent for an action using the configured mode.
        """
        if self.mode == ConsentMode.ALWAYS_YES:
            return await self._always_yes_consent(request)
        elif self.mode == ConsentMode.MANUAL:
            return await self._manual_consent(request)
        elif self.mode == ConsentMode.VOICE:
            return await self._voice_consent(request)
        elif self.mode == ConsentMode.RANDOM:
            return await self._random_consent(request)
        elif self.mode == ConsentMode.CONSENSUS:
            return await self._consensus_consent(request)
        else:
            raise ValueError(f"Unknown consent mode: {self.mode}")

    async def _always_yes_consent(self, request: ConsentRequest) -> ConsentResult:
        """Always approve (for testing/development)."""
        logger.warning(f"ALWAYS_YES mode: Auto-approving {request.action}")
        return ConsentResult(
            approved=True,
            method="always_yes",
            confidence=1.0,
            reasoning="Always approve mode enabled",
            metadata={"mode": "always_yes"}
        )

    async def _manual_consent(self, request: ConsentRequest) -> ConsentResult:
        """Require explicit manual approval."""
        # In a real implementation, this would show a UI prompt
        # For now, we'll simulate with a timeout
        logger.info(f"Manual consent required for: {request.action}")

        # Simulate waiting for user input
        await asyncio.sleep(min(request.timeout_seconds, 5))  # Shorter for demo

        return ConsentResult(
            approved=False,  # Default to no for safety
            method="manual",
            confidence=0.5,
            reasoning="Manual approval required (simulated denial)",
            metadata={"timeout": request.timeout_seconds}
        )

    async def _voice_consent(self, request: ConsentRequest) -> ConsentResult:
        """Voice-activated consent with Cali ethics integration."""
        logger.info(f"Voice consent for: {request.action}")

        try:
            # Wait for voice keyword
            keyword = await self._voice_callback()

            if keyword in {"approve", "yes", "confirmed", "caleon approve"}:
                # Inject high-ethics token into ethics gate
                if self.ethics_gate_available:
                    try:
                        requests.post(
                            f"{CALI_ETHICS_URL}/inject",
                            json={
                                "token": " [APPROVED] ",
                                "ethics": 1.0,
                                "priority": 10  # High priority
                            },
                            timeout=0.5
                        )
                        logger.info("Injected approval token into ethics gate")
                    except Exception as e:
                        logger.warning(f"Failed to inject approval token: {e}")

                return ConsentResult(
                    approved=True,
                    method="voice",
                    confidence=0.95,
                    reasoning=f"Voice approval detected: '{keyword}'",
                    metadata={"keyword": keyword, "ethics_injected": self.ethics_gate_available}
                )
            else:
                return ConsentResult(
                    approved=False,
                    method="voice",
                    confidence=0.8,
                    reasoning=f"Voice denial or unclear: '{keyword}'",
                    metadata={"keyword": keyword}
                )

        except Exception as e:
            logger.error(f"Voice consent failed: {e}")
            return ConsentResult(
                approved=False,
                method="voice",
                confidence=0.0,
                reasoning=f"Voice consent error: {str(e)}",
                metadata={"error": str(e)}
            )

    async def _random_consent(self, request: ConsentRequest) -> ConsentResult:
        """Random approval (for testing)."""
        import random
        approved = random.choice([True, False])
        confidence = random.uniform(0.5, 1.0)

        return ConsentResult(
            approved=approved,
            method="random",
            confidence=confidence,
            reasoning=f"Random decision: {'approved' if approved else 'denied'}",
            metadata={"random_seed": random.random()}
        )

    async def _consensus_consent(self, request: ConsentRequest) -> ConsentResult:
        """Require consensus from multiple sources."""
        # This would implement consensus logic
        # For now, simulate with majority vote
        votes = []
        for i in range(3):  # Simulate 3 consensus sources
            vote = await self._random_consent(request)  # Simplified
            votes.append(vote.approved)

        approved = sum(votes) >= 2  # Majority wins
        confidence = sum(votes) / len(votes)

        return ConsentResult(
            approved=approved,
            method="consensus",
            confidence=confidence,
            reasoning=f"Consensus vote: {sum(votes)}/{len(votes)} approved",
            metadata={"votes": votes}
        )

    async def _voice_callback(self) -> str:
        """
        Listen for voice keywords.
        In a real implementation, this would integrate with speech recognition.
        """
        # Simulate voice recognition delay
        await asyncio.sleep(1.0)

        # Simulate voice recognition (in real implementation, this would use Web Speech API or similar)
        # For demo purposes, we'll randomly return keywords
        import random
        keywords = ["approve", "yes", "no", "deny", "unclear", "caleon approve"]
        weights = [0.3, 0.2, 0.2, 0.15, 0.1, 0.05]  # Bias toward approval for demo

        keyword = random.choices(keywords, weights=weights, k=1)[0]
        logger.info(f"Voice recognition result: '{keyword}'")

        return keyword

    def set_mode(self, mode: ConsentMode):
        """Change the consent mode."""
        logger.info(f"Changing consent mode from {self.mode} to {mode}")
        self.mode = mode

    def get_status(self) -> Dict[str, Any]:
        """Get current status of consent manager."""
        return {
            "mode": self.mode.value,
            "ethics_gate_available": self.ethics_gate_available,
            "voice_active": self.voice_active
        }

# Global instance for easy access
_consent_manager: Optional[CaleonConsentManager] = None

def get_consent_manager(mode: ConsentMode = ConsentMode.MANUAL) -> CaleonConsentManager:
    """Get or create the global consent manager instance."""
    global _consent_manager
    if _consent_manager is None:
        _consent_manager = CaleonConsentManager(mode)
    return _consent_manager

async def request_consent(action: str, context: Dict[str, Any] = None,
                         risk_level: str = "medium") -> ConsentResult:
    """
    Convenience function to request consent.
    """
    if context is None:
        context = {}

    request = ConsentRequest(
        action=action,
        context=context,
        risk_level=risk_level
    )

    manager = get_consent_manager()
    return await manager.get_consent(request)
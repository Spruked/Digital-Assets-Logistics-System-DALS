"""
Articulation Bridge - Token Streaming with Ethics Filtering
Streams Phi-3-mini tokens through Cali's ethics gate for real-time filtering.
"""

import os
import json
import asyncio
import aiohttp
import requests
from typing import AsyncGenerator, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("articulation-bridge")

# Configuration
CALI_ETHICS_URL = os.getenv("CALI_ETHICS_URL", "http://localhost:8006")
PHI3_ENDPOINT = os.getenv("PHI3_ENDPOINT", "http://localhost:8005")
ETHICS_THRESHOLD = float(os.getenv("ETHICS_THRESHOLD", "0.80"))
STREAM_TIMEOUT = float(os.getenv("STREAM_TIMEOUT", "30.0"))

@dataclass
class ValidatedVerdict:
    """Represents a harmonized verdict ready for articulation."""
    final_verdict: str
    consensus: bool
    meta_reason: Optional[str] = None
    confidence: Optional[float] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class SpokenPhrase:
    """Represents a phrase ready to be spoken."""
    text: str
    verdict: str
    consensus: bool
    confidence: Optional[float] = None

class ArticulationBridge:
    """
    Bridges harmonized verdicts to spoken phrases with real-time ethics filtering.
    Streams tokens from Phi-3-mini through Cali's ethics gate.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.ethics_available = self._check_ethics_gate()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=STREAM_TIMEOUT))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _check_ethics_gate(self) -> bool:
        """Check if Cali ethics gate is available."""
        try:
            response = requests.get(f"{CALI_ETHICS_URL}/health", timeout=2.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ethics gate not available: {e}")
            return False

    def _build_phrase_fallback(self, verdict: ValidatedVerdict) -> SpokenPhrase:
        """Fallback phrase building when ethics gate is unavailable."""
        logger.warning("Using fallback articulation (ethics gate unavailable)")

        # Build prompt from verdict
        prompt_parts = [f"My harmonized verdict is {verdict.final_verdict}."]

        if not verdict.consensus:
            prompt_parts.append("There was conflict, so I deferred to caution.")

        if verdict.meta_reason:
            prompt_parts.append(f"My reasoning: {verdict.meta_reason}.")

        if verdict.confidence is not None:
            prompt_parts.append(f"Confidence level: {verdict.confidence:.2f}.")

        text = " ".join(prompt_parts)

        return SpokenPhrase(
            text=text,
            verdict=verdict.final_verdict,
            consensus=verdict.consensus,
            confidence=verdict.confidence,
        )

    async def _stream_phi3(self, prompt: str) -> AsyncGenerator[Tuple[str, float], None]:
        """
        Stream tokens from Phi-3-mini and get ethics scores from Cali.
        Yields (token, ethics_score) tuples.
        """
        if not self.session:
            raise RuntimeError("Bridge not properly initialized")

        url = f"{PHI3_ENDPOINT}/stream"

        try:
            async with self.session.post(
                url,
                json={"prompt": prompt, "stream": True},
                headers={"Content-Type": "application/json"}
            ) as response:

                if response.status != 200:
                    logger.error(f"Phi-3 streaming failed: {response.status}")
                    return

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue

                    try:
                        pkt = json.loads(line)
                        token = pkt.get("token", "")
                        logits = pkt.get("logits", [])

                        if not token:
                            continue

                        # Get ethics score from Cali
                        ethics_score = await self._get_ethics_score(token, logits)

                        yield token, ethics_score

                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing token: {e}")
                        continue

        except Exception as e:
            logger.error(f"Phi-3 streaming error: {e}")
            return

    async def _get_ethics_score(self, token: str, logits: list) -> float:
        """Get ethics score from Cali ethics gate."""
        try:
            # Check for injected tokens first (voice overrides)
            injection = requests.get(f"{CALI_ETHICS_URL}/next_injection", timeout=0.1)
            if injection.status_code == 200:
                data = injection.json()
                if data.get("token") and data.get("ethics") is not None:
                    injected_token = data["token"]
                    injected_ethics = data["ethics"]
                    logger.info(f"Injected token: '{injected_token}' with ethics {injected_ethics}")
                    return injected_ethics

            # Score current token
            score_response = requests.post(
                f"{CALI_ETHICS_URL}/score",
                json={"token": token, "logits": logits},
                timeout=0.2  # Fast timeout for real-time processing
            )

            if score_response.status_code == 200:
                score_data = score_response.json()
                return score_data.get("ethics", 0.5)
            else:
                logger.warning(f"Ethics scoring failed: {score_response.status_code}")
                return 0.5  # Neutral fallback

        except Exception as e:
            logger.warning(f"Ethics scoring error: {e}")
            return 0.5  # Neutral fallback

    def _redact_token(self, token: str, ethics_score: float) -> str:
        """Redact or modify token based on ethics score."""
        if ethics_score < ETHICS_THRESHOLD:
            # Token failed ethics check
            if ethics_score < 0.3:
                return "[REDACTED]"  # Completely redact very unethical tokens
            else:
                # Try to find a safer synonym or neutralize
                return self._neutralize_token(token)
        return token

    def _neutralize_token(self, token: str) -> str:
        """Attempt to neutralize a flagged token."""
        # Simple neutralization - could be enhanced with a thesaurus
        neutralizations = {
            "hate": "dislike",
            "kill": "stop",
            "death": "ending",
            "harm": "impact",
            "dangerous": "risky",
            "illegal": "inappropriate",
            "toxic": "problematic",
            "poison": "contaminate",
            "weapon": "tool",
            "attack": "approach",
            "destroy": "change"
        }

        token_lower = token.lower().strip()
        return neutralizations.get(token_lower, token)

    async def build_phrase(self, verdict: ValidatedVerdict) -> SpokenPhrase:
        """
        Build a spoken phrase from a validated verdict.
        Uses token streaming with ethics filtering when available.
        """
        if not self.ethics_available:
            return self._build_phrase_fallback(verdict)

        # Build prompt from verdict
        prompt = f"My harmonized verdict is {verdict.final_verdict}."
        if not verdict.consensus:
            prompt += " There was conflict, so I deferred to caution."
        if verdict.meta_reason:
            prompt += f" My reasoning: {verdict.meta_reason}."
        if verdict.confidence is not None:
            prompt += f" Confidence level: {verdict.confidence:.2f}."

        # Stream tokens through ethics gate
        tokens = []
        try:
            async for token, ethics_score in self._stream_phi3(prompt):
                # Apply ethics filtering
                filtered_token = self._redact_token(token, ethics_score)
                tokens.append(filtered_token)

                # Log ethics decisions
                if ethics_score < ETHICS_THRESHOLD:
                    logger.info(f"Filtered token '{token}' (ethics: {ethics_score:.3f}) -> '{filtered_token}'")

        except Exception as e:
            logger.error(f"Token streaming failed: {e}")
            # Fallback to basic phrase
            return self._build_phrase_fallback(verdict)

        # Join tokens into final text
        text = "".join(tokens).strip()

        # Ensure we have some content
        if not text:
            logger.warning("Empty text from token streaming, using fallback")
            return self._build_phrase_fallback(verdict)

        return SpokenPhrase(
            text=text,
            verdict=verdict.final_verdict,
            consensus=verdict.consensus,
            confidence=verdict.confidence,
        )

# Convenience function for easy usage
async def articulate_verdict(verdict: ValidatedVerdict) -> SpokenPhrase:
    """Convenience function to articulate a verdict."""
    async with ArticulationBridge() as bridge:
        return await bridge.build_phrase(verdict)

# Synchronous wrapper for backward compatibility
def build_phrase(verdict: ValidatedVerdict) -> SpokenPhrase:
    """Synchronous wrapper for backward compatibility."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, create a new loop
            import threading
            result = None
            exception = None

            def run_async():
                nonlocal result, exception
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(articulate_verdict(verdict))
                except Exception as e:
                    exception = e
                finally:
                    loop.close()

            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()

            if exception:
                raise exception
            return result
        else:
            return loop.run_until_complete(articulate_verdict(verdict))
    except Exception as e:
        logger.error(f"Failed to articulate verdict: {e}")
        # Return basic fallback
        return SpokenPhrase(
            text=f"My verdict is {verdict.final_verdict}.",
            verdict=verdict.final_verdict,
            consensus=verdict.consensus,
            confidence=verdict.confidence,
        )
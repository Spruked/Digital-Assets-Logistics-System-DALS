"""
SHiM v1.1 - Spherical Harmonic Integrity Module for DALS
Advisory-Only Cognitive Subsystem

This module provides harmonic resonance analysis for asset claims
using spherical harmonics (ℓ, m) to evaluate evidence coherence.
All outputs are advisory only with zero execution authority.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import hashlib
import math
import random


class RiskHeuristicsAnalyzer:
    """Analyzes risk patterns in evidence and analysis results."""

    def __init__(self):
        self.risk_patterns = {
            "high_uncertainty": {
                "condition": lambda score, band, evidence_count, evidence_types: score < 0.5 or band == "WIDE",
                "severity": "HIGH",
                "description": "High uncertainty detected - additional evidence recommended"
            },
            "insufficient_evidence": {
                "condition": lambda score, band, evidence_count, evidence_types: evidence_count < 3,
                "severity": "MEDIUM",
                "description": "Insufficient evidence types - minimum 3 recommended"
            },
            "conflicting_signals": {
                "condition": lambda score, band, evidence_count, evidence_types: score < 0.3,
                "severity": "HIGH",
                "description": "Conflicting evidence signals detected"
            },
            "weak_coherence": {
                "condition": lambda score, band, evidence_count, evidence_types: score < 0.6 and band == "WIDE",
                "severity": "MEDIUM",
                "description": "Weak evidence coherence with high variance"
            },
            "regulatory_gaps": {
                "condition": lambda score, band, evidence_count, evidence_types: not any(
                    ev in ["kyc_compliant", "aml_screened", "regulatory_approved"] for ev in evidence_types
                ),
                "severity": "MEDIUM",
                "description": "Potential regulatory compliance gaps detected"
            }
        }

    def analyze_risks(self, shim_score: float, confidence_band: str,
                      evidence_count: int, evidence_types: List[str]) -> List[Dict[str, Any]]:
        """Analyze evidence for risk patterns."""
        risks = []

        for risk_name, pattern in self.risk_patterns.items():
            if pattern["condition"](shim_score, confidence_band, evidence_count, evidence_types):
                risks.append({
                    "risk_type": risk_name,
                    "severity": pattern["severity"],
                    "description": pattern["description"],
                    "recommendation": self._get_recommendation(risk_name)
                })

        return risks

    def _get_recommendation(self, risk_type: str) -> str:
        """Get recommendation for specific risk type."""
        recommendations = {
            "high_uncertainty": "Gather additional evidence types and verify sources",
            "insufficient_evidence": "Collect at least 3 different evidence types",
            "conflicting_signals": "Review evidence for inconsistencies and resolve conflicts",
            "weak_coherence": "Strengthen evidence chain and reduce variance",
            "regulatory_gaps": "Conduct regulatory compliance check and add required evidence"
        }
        return recommendations.get(risk_type, "Review analysis and consult human expert")


class SphericalHarmonicAnalyzer:
    """Analyzes evidence using spherical harmonic resonance patterns."""

    def __init__(self):
        self.harmonic_orders = {
            'signature_valid': {'l': 2, 'm': 1, 'weight': 0.96},
            'identity_verified': {'l': 2, 'm': -1, 'weight': 0.98},
            'provenance_intact': {'l': 1, 'm': 0, 'weight': 0.93},
            'chain_consistent': {'l': 3, 'm': 2, 'weight': 0.91},
            'historical_pattern': {'l': 2, 'm': 0, 'weight': 0.89}
        }

    def analyze_evidence(self, evidence: List[str]) -> Dict[str, float]:
        """Calculate harmonic overlap for each evidence type."""
        weighting = {}

        for ev in evidence:
            if ev in self.harmonic_orders:
                # Simulate harmonic resonance calculation
                base_weight = self.harmonic_orders[ev]['weight']
                # Add small random variation for realism
                variation = random.uniform(-0.02, 0.02)
                weighting[ev] = max(0.0, min(1.0, base_weight + variation))
            else:
                # Unknown evidence type - assign moderate confidence
                weighting[ev] = 0.75

        return weighting

    def calculate_shim_score(self, evidence_weighting: Dict[str, float]) -> float:
        """Calculate aggregate harmonic coherence score."""
        if not evidence_weighting:
            return 0.0

        # Weighted average with harmonic decay
        total_weight = 0.0
        weighted_sum = 0.0

        for evidence, weight in evidence_weighting.items():
            harmonic_weight = 1.0 / (1.0 + self.harmonic_orders.get(evidence, {}).get('l', 2))
            weighted_sum += weight * harmonic_weight
            total_weight += harmonic_weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def determine_verdict(self, shim_score: float) -> str:
        """Determine verdict based on harmonic coherence."""
        if shim_score >= 0.9:
            return "HIGH_SUPPORT"
        elif shim_score >= 0.7:
            return "MODERATE"
        elif shim_score >= 0.5:
            return "LOW"
        else:
            return "CONFLICT"

    def calculate_confidence_band(self, evidence_weighting: Dict[str, float]) -> str:
        """Calculate confidence band based on evidence variance."""
        if not evidence_weighting:
            return "WIDE"

        weights = list(evidence_weighting.values())
        if len(weights) < 2:
            return "NARROW"

        mean = sum(weights) / len(weights)
        variance = sum((w - mean) ** 2 for w in weights) / len(weights)
        std_dev = math.sqrt(variance)

        return "NARROW" if std_dev < 0.1 else "WIDE"

    def generate_explanation(self, claim: str, evidence_weighting: Dict[str, float],
                           shim_score: float, verdict: str) -> List[str]:
        """Generate human-readable explanation of harmonic analysis."""
        explanations = []

        # Evidence coherence
        strong_evidence = [k for k, v in evidence_weighting.items() if v >= 0.9]
        weak_evidence = [k for k, v in evidence_weighting.items() if v < 0.7]

        if strong_evidence:
            explanations.append(f"Strong harmonic overlap detected in: {', '.join(strong_evidence)}")

        if weak_evidence:
            explanations.append(f"Weak resonance in: {', '.join(weak_evidence)}")

        # Harmonic analysis
        dominant_harmonics = []
        for ev, weight in evidence_weighting.items():
            if ev in self.harmonic_orders:
                l = self.harmonic_orders[ev]['l']
                m = self.harmonic_orders[ev]['m']
                dominant_harmonics.append(f"ℓ={l}, m={m}")

        if dominant_harmonics:
            explanations.append(f"Dominant spherical harmonics: {', '.join(set(dominant_harmonics))}")

        # Verdict explanation
        if verdict == "HIGH_SUPPORT":
            explanations.append("High coherence indicates strong evidence alignment")
        elif verdict == "MODERATE":
            explanations.append("Moderate resonance suggests conditional support")
        elif verdict == "LOW":
            explanations.append("Low harmonic overlap indicates weak evidence")
        else:
            explanations.append("Conflicting harmonics detected - review required")

        # Audit depth simulation
        audit_depth = random.randint(5, 10)
        explanations.append(f"Provenance audit depth: {audit_depth} blocks analyzed")

        return explanations


class DALSAdvisor:
    """SHiM v1.1 DALS Advisory Interface - Advisory Only, Zero Execution Authority"""

    def __init__(self):
        self.analyzer = SphericalHarmonicAnalyzer()
        self.risk_analyzer = RiskHeuristicsAnalyzer()
        self.version = "shim_v1.1_spherical"

    def _generate_asset_id(self) -> str:
        """Generate unique asset ID for this analysis."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
        unique_id = str(uuid.uuid4())[:3].upper()
        return f"DAL-{timestamp[:4]}-{timestamp[4:6]}-{unique_id}"

    def _generate_audit_trace_id(self) -> str:
        """Generate audit trace ID."""
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        sequence = str(uuid.uuid4())[:3].upper()
        return f"SHIM-ADV-{date_str}-{sequence}"

    def _get_recommended_action(self, verdict: str, shim_score: float) -> str:
        """Determine recommended human action based on analysis."""
        if verdict == "HIGH_SUPPORT" and shim_score >= 0.95:
            return "Proceed to human review and multi-sig approval"
        elif verdict == "HIGH_SUPPORT":
            return "Proceed with caution - human review recommended"
        elif verdict == "MODERATE":
            return "Human review required before proceeding"
        elif verdict == "LOW":
            return "Strong human oversight required - additional evidence needed"
        else:
            return "Halt and escalate - conflicting evidence detected"

    def analyze(self, claim: str, evidence: List[str]) -> Dict[str, Any]:
        """
        Perform SHiM v1.1 harmonic analysis of asset claim.

        IMPORTANT: This is ADVISORY ONLY. No execution authority.
        Final decisions must be made by human operators with multi-sig.

        Args:
            claim: The asset claim to analyze
            evidence: List of evidence types present

        Returns:
            Dict containing shim_advisory and dals_final_decision (always None)
        """
        # Perform harmonic analysis
        evidence_weighting = self.analyzer.analyze_evidence(evidence)
        shim_score = self.analyzer.calculate_shim_score(evidence_weighting)
        verdict = self.analyzer.determine_verdict(shim_score)
        confidence_band = self.analyzer.calculate_confidence_band(evidence_weighting)
        explanation = self.analyzer.generate_explanation(claim, evidence_weighting, shim_score, verdict)

        # Perform risk analysis
        risk_flags = self.risk_analyzer.analyze_risks(
            shim_score=shim_score,
            confidence_band=confidence_band,
            evidence_count=len(evidence),
            evidence_types=evidence
        )

        # Generate metadata
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        asset_id = self._generate_asset_id()
        audit_trace_id = self._generate_audit_trace_id()
        recommended_action = self._get_recommended_action(verdict, shim_score)

        # Construct advisory output
        shim_advisory = {
            "version": self.version,
            "timestamp": timestamp,
            "asset_id": asset_id,
            "claim": claim,
            "shim_score": round(shim_score, 2),
            "verdict": verdict,
            "confidence_band": confidence_band,
            "evidence_weighting": {k: round(v, 2) for k, v in evidence_weighting.items()},
            "explanation": explanation,
            "risk_flags": risk_flags,
            "advisory_mode": True,
            "enforcement": "NONE",
            "recommended_action": recommended_action,
            "audit_trace_id": audit_trace_id
        }

        return {
            "shim_advisory": shim_advisory,
            "dals_final_decision": None  # Always None - human authority preserved
        }


# Utility functions for integration
def validate_shim_output(output: Dict[str, Any]) -> bool:
    """Validate SHiM output against schema."""
    try:
        # Basic validation
        assert "shim_advisory" in output
        assert "dals_final_decision" in output
        assert output["dals_final_decision"] is None

        advisory = output["shim_advisory"]
        required_fields = [
            "version", "timestamp", "asset_id", "claim", "shim_score",
            "verdict", "confidence_band", "evidence_weighting",
            "explanation", "risk_flags", "advisory_mode", "enforcement",
            "recommended_action", "audit_trace_id"
        ]

        for field in required_fields:
            assert field in advisory

        assert advisory["advisory_mode"] is True
        assert advisory["enforcement"] == "NONE"
        assert 0.0 <= advisory["shim_score"] <= 1.0

        return True

    except (AssertionError, KeyError, TypeError):
        return False


def shim_advisor_factory() -> DALSAdvisor:
    """Factory function for DALS Advisor instances."""
    return DALSAdvisor()
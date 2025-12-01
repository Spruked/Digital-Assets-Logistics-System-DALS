"""
Gyro-Cortical Harmonizer Package
================================

The Gyro-Cortical Harmonizer is the final reasoning stage before any output.
It implements 5+1 combinatorial reasoning cycles with philosophical guidance
and convergence validation within ±3 standard deviations.

Key Components:
- harmonizer.py: Main GyroCorticalHarmonizer class
- Implements recursive reasoning cycles with philosophical framing
- Validates convergence within stability thresholds
- Serves as final articulation gatekeeper

Integration:
- Requires 5 logic packets from UCM modules (Helices, EchoStack, Drift, Vault, Security)
- Applies 1 philosophical guide per cycle (rotates to prevent bias)
- Runs until convergence or max cycles reached
- Returns harmonized verdict for final decision making

DALS-001 Compliance:
- Returns real data only (zeros when inactive)
- No mock verdicts or simulated reasoning
- Transparent convergence tracking
"""

from .harmonizer import GyroCorticalHarmonizer, get_harmonizer

__all__ = [
    'GyroCorticalHarmonizer',
    'get_harmonizer'
]
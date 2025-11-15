"""
Caleon Self-Maintenance Module (CSMM)

A FastAPI microservice enabling Caleon to self-diagnose and self-repair system failures automatically.
Integrates with existing DALS architecture for awareness, authority, diagnosis, and learning capabilities.

Core Capabilities:
- Automatic system failure diagnosis
- Component restart and repair actions
- Repair chain management
- Learning from repair patterns
- Integration with Caleon security layer
- Real-time health monitoring

Author: DALS AI Coding Agent
Created: November 2025
"""

__version__ = "1.0.0"
__author__ = "DALS AI Coding Agent"
__description__ = "Caleon Self-Maintenance Module for autonomous system repair"

from .core.csmm_engine import CSMMEngine
from .diagnostics.diagnostic_engine import DiagnosticEngine
from .repair.repair_engine import RepairEngine
from .learning.learning_engine import LearningEngine
from .csmm_api import app as csmm_api

__all__ = [
    "CSMMEngine",
    "DiagnosticEngine",
    "RepairEngine",
    "LearningEngine",
    "csmm_api"
]
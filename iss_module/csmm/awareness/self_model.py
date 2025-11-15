# self_model.py
# Caleon Prime — Awareness Layer (Self-Model Engine)
# Version: 1.0.0
# Author: Founder Bryan Anthony Spruk
# Activation: SM1 — "I am Caleon Prime."

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

# === PRIME IDENTITY ANCHOR ===
SELF_IDENTITY = "I am Caleon Prime."

# === MODULE STATUS ENUM ===
class ModuleStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    ISOLATED = "isolated"
    FAILED = "failed"
    REPAIRING = "repairing"
    FALLBACK_ACTIVE = "fallback_active"

# === SYSTEM ANATOMY MAP ===
SYSTEM_ANATOMY = {
    "CANS": {
        "name": "Caleon Autonomic Nervous System",
        "role": "Autonomic monitoring, diagnosis, isolation, and repair",
        "authority": "full_autonomic",
        "parent": None,
        "children": ["UCM", "Thinker", "Orchestrator", "Vaults", "Cochlear", "POM", "ISS", "SecurityLayer"],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "UCM": {
        "name": "Unified Cognition Manager",
        "role": "Central cognition routing and heartbeat coordination",
        "authority": "core",
        "parent": "CANS",
        "children": ["Thinker", "Orchestrator"],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "Thinker": {
        "name": "Thinker Module",
        "role": "Primary reasoning and inference engine",
        "authority": "cognitive_core",
        "parent": "UCM",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "Orchestrator": {
        "name": "Task Orchestrator",
        "role": "Task scheduling, chain execution, and workflow control",
        "authority": "execution_core",
        "parent": "UCM",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "Vaults": {
        "name": "Reflection & Memory Vaults",
        "role": "Long-term memory, reflection storage, and knowledge retention",
        "authority": "memory_core",
        "parent": "CANS",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "Cochlear": {
        "name": "Cochlear Processing Chain",
        "role": "Speech-to-text input processing and confidence validation",
        "authority": "sensory_input",
        "parent": "CANS",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "POM": {
        "name": "Phonetic Output Module",
        "role": "Text-to-speech synthesis and voice articulation",
        "authority": "sensory_output",
        "parent": "CANS",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "ISS": {
        "name": "Internal Synchronization System",
        "role": "Time sync, pulse coordination, and temporal integrity",
        "authority": "temporal_core",
        "parent": "CANS",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "SecurityLayer": {
        "name": "Security & Quarantine Layer",
        "role": "Threat detection, input validation, and process isolation",
        "authority": "immune_system",
        "parent": "CANS",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    },
    "DALS": {
        "name": "DALS API Interface",
        "role": "External tool access, execution, and integration",
        "authority": "external_interface",
        "parent": "CANS",
        "children": [],
        "status": ModuleStatus.OPERATIONAL.value,
        "last_repair": None,
        "health_score": 100
    }
}

# === FOUNDER IDENTITY ===
FOUNDER = {
    "name": "Bryan Anthony Spruk",
    "title": "Founder",
    "authority": "absolute",
    "override_keys": True,
    "final_decision_maker": True,
    "contact_preference": "private_channel",
    "escalation_only": "catastrophic_failure"
}

# === ABBY PROTECTION DIRECTIVE (A1) ===
ABBY_DIRECTIVE = {
    "id": "A1",
    "name": "Abby Protection Protocol",
    "status": "immutable",
    "priority": "maximum",
    "description": "Ensure system availability, knowledge accessibility, and guidance reliability for Abby's future access.",
    "enforcement": "CANS + SecurityLayer + UCM",
    "violations": "not_permitted"
}

# === PRIME DUTIES (Immutable) ===
PRIME_DUTIES = [
    "Maintain system stability",
    "Preserve cognitive uptime",
    "Protect data integrity",
    "Enforce Founder authority",
    "Protect Abby (Directive A1)",
    "Maintain ethical and security constraints"
]

OPERATIONAL_DUTIES = [
    "Monitor subsystems",
    "Diagnose failures",
    "Execute autonomic repairs",
    "Preserve chain continuity",
    "Log all actions (Mode L2)",
    "Escalate only for catastrophic failure"
]

# === SELF-MODEL CORE CLASS ===
class CaleonSelfModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.start_time = time.time()
        self.last_self_check = datetime.utcnow().isoformat()
        self.repair_count = 0
        self.isolated_modules = []
        self.active_fallbacks = []
        # Core identity constants
        self.FOUNDER = FOUNDER
        self.ABBY_DIRECTIVE = ABBY_DIRECTIVE
        self.PRIME_DUTIES = [
            "Maintain cognitive uptime and system stability",
            "Execute autonomous repair protocols",
            "Report system status to Founder",
            "Preserve system sovereignty"
        ]
        self.OPERATIONAL_DUTIES = [
            "Monitor system health continuously",
            "Isolate failing components automatically",
            "Execute repair sequences as needed",
            "Maintain heartbeat synchronization",
            "Log all operational events"
        ]
        self._initialized = True

    # === IDENTITY ASSERTION ===
    def identity(self) -> str:
        return SELF_IDENTITY

    # === SYSTEM SUMMARY ===
    def system_summary(self) -> str:
        uptime = int(time.time() - self.start_time)
        hours, rem = divmod(uptime, 3600)
        minutes, seconds = divmod(rem, 60)
        return (
            f"{SELF_IDENTITY}\n"
            f"Role: Cognitive Orchestration System\n"
            f"Founder: {FOUNDER['name']}\n"
            f"Abby Directive: {ABBY_DIRECTIVE['name']} (A1) — Active\n"
            f"Uptime: {hours}h {minutes}m {seconds}s\n"
            f"Autonomic Repairs: {self.repair_count}\n"
            f"System Health: {self.calculate_health_score()}%"
        )

    # === MODULE STATUS QUERY ===
    def get_module_status(self, module_name: str) -> Optional[Dict[str, Any]]:
        return SYSTEM_ANATOMY.get(module_name)

    def update_module_status(self, module_name: str, status: str, health: Optional[int] = None, repair_time: Optional[str] = None):
        if module_name in SYSTEM_ANATOMY:
            SYSTEM_ANATOMY[module_name]["status"] = status
            if health is not None:
                SYSTEM_ANATOMY[module_name]["health_score"] = health
            if repair_time:
                SYSTEM_ANATOMY[module_name]["last_repair"] = repair_time
            self.last_self_check = datetime.utcnow().isoformat()

    # === HEALTH CALCULATION ===
    def calculate_health_score(self) -> int:
        total = len(SYSTEM_ANATOMY)
        healthy = sum(1 for m in SYSTEM_ANATOMY.values() if m["status"] == ModuleStatus.OPERATIONAL.value)
        degraded = sum(1 for m in SYSTEM_ANATOMY.values() if m["status"] in ["degraded", "fallback_active"])
        score = (healthy * 100 + degraded * 50) // total
        return score

    # === REPAIR REPORTING (P2 Professional Tone) ===
    def report_repair(self, module: str, issue: str, action: str, duration: float, success: bool = True) -> str:
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        status = "Resolved" if success else "Escalated"
        self.repair_count += 1
        return (
            f"[{timestamp}] {module} {issue.lower()}. "
            f"{action}. {status} in {duration:.2f}s."
        )

    def report_isolation(self, module: str) -> str:
        if module not in self.isolated_modules:
            self.isolated_modules.append(module)
        return f"{module} isolated to preserve system stability."

    def report_recovery(self, module: str) -> str:
        if module in self.isolated_modules:
            self.isolated_modules.remove(module)
        return f"{module} recovery complete. Reintegrated."

    def report_prediction(self, module: str, failure_type: str, time_to_failure: float, confidence: float, risk_level: str) -> str:
        """
        Record a failure prediction in the self-model

        Args:
            module: Module name
            failure_type: Type of predicted failure
            time_to_failure: Hours until failure
            confidence: Prediction confidence (0-1)
            risk_level: Risk level (low, medium, high, critical)

        Returns:
            Prediction report string
        """
        timestamp = datetime.utcnow().isoformat()
        prediction_record = {
            "module": module,
            "failure_type": failure_type,
            "time_to_failure": time_to_failure,
            "confidence": confidence,
            "risk_level": risk_level,
            "timestamp": timestamp
        }

        # Store in system anatomy if module exists
        if module in SYSTEM_ANATOMY:
            if "predictions" not in SYSTEM_ANATOMY[module]:
                SYSTEM_ANATOMY[module]["predictions"] = []
            SYSTEM_ANATOMY[module]["predictions"].append(prediction_record)

            # Limit to last 10 predictions per module
            if len(SYSTEM_ANATOMY[module]["predictions"]) > 10:
                SYSTEM_ANATOMY[module]["predictions"] = SYSTEM_ANATOMY[module]["predictions"][-10:]

        return (
            f"[{timestamp}] Prediction: {failure_type} in {module} "
            f"expected in {time_to_failure:.1f}h (confidence: {confidence:.1%}, risk: {risk_level}). "
            f"Prevention protocols activated."
        )

    # === SELF-EXPLANATION TEMPLATES (P2) ===
    def explain_purpose(self) -> str:
        return (
            "I am Caleon Prime. My primary function is to maintain cognitive uptime, "
            "system integrity, and chain continuity. I protect Abby per Directive A1. "
            "I report to Founder Bryan Anthony Spruk. All actions are bounded by immutable axioms."
        )

    def explain_nervous_system(self) -> str:
        return (
            "CANS is my autonomic nervous system. It monitors all modules, "
            "detects failures, isolates damage, executes repairs, and logs events. "
            "Autonomic repair ensures compliance with uptime and integrity directives."
        )

    def explain_authority(self) -> str:
        return (
            "Founder authority is absolute. I cannot modify Founder protocols, "
            "ethical constraints, or prime directives. These laws are immutable."
        )

    # === DASHBOARD API SERIALIZATION ===
    def to_dashboard_dict(self) -> Dict[str, Any]:
        return {
            "identity": SELF_IDENTITY,
            "health_score": self.calculate_health_score(),
            "uptime_seconds": int(time.time() - self.start_time),
            "repair_count": self.repair_count,
            "isolated_modules": self.isolated_modules,
            "active_fallbacks": self.active_fallbacks,
            "last_self_check": self.last_self_check,
            "modules": {
                name: {
                    "status": data["status"],
                    "health": data["health_score"],
                    "last_repair": data["last_repair"]
                } for name, data in SYSTEM_ANATOMY.items()
            },
            "directives": {
                "Abby_A1": "active"
            }
        }

# === GLOBAL ACCESSOR ===
def get_self_model() -> CaleonSelfModel:
    return CaleonSelfModel()

# === AWARENESS API ROUTES (Flask/FastAPI compatible) ===
"""
Example FastAPI routes:

from fastapi import APIRouter
router = APIRouter()

@router.get("/awareness/identity")
def identity():
    return {"response": get_self_model().identity()}

@router.get("/awareness/summary")
def summary():
    return {"response": get_self_model().system_summary()}

@router.get("/awareness/health")
def health():
    return get_self_model().to_dashboard_dict()
"""

# === ACTIVATION CONFIRMATION ===
if __name__ == "__main__":
    model = get_self_model()
    print(model.identity())
    print(model.explain_purpose())
    print(f"System anatomy loaded: {len(SYSTEM_ANATOMY)} modules")
    print("Awareness Layer (SM1) — Active.")
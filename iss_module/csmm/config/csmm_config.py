"""
CSMM Configuration

Configuration settings for the Caleon Self-Maintenance Module.
"""

import os
from typing import Dict, Any

# CSMM Service Configuration
CSMM_CONFIG = {
    "service": {
        "name": "csmm-service",
        "host": os.getenv("CSMM_HOST", "0.0.0.0"),
        "port": int(os.getenv("CSMM_PORT", "8009")),
        "log_level": os.getenv("CSMM_LOG_LEVEL", "INFO"),
        "enable_cors": True,
        "cors_origins": ["*"],  # Configure for production
    },

    "engine": {
        "diagnostic_interval": int(os.getenv("CSMM_DIAGNOSTIC_INTERVAL", "300")),  # 5 minutes
        "repair_timeout": int(os.getenv("CSMM_REPAIR_TIMEOUT", "600")),  # 10 minutes
        "learning_enabled": os.getenv("CSMM_LEARNING_ENABLED", "true").lower() == "true",
        "max_concurrent_repairs": int(os.getenv("CSMM_MAX_CONCURRENT_REPAIRS", "3")),
        "autonomous_mode": os.getenv("CSMM_AUTONOMOUS_MODE", "aggressive"),  # conservative, standard, aggressive
        "founder_alert_threshold": os.getenv("CSMM_FOUNDER_ALERT_THRESHOLD", "catastrophic"),  # warning, critical, catastrophic
    },

    "diagnostics": {
        "deep_scan_interval": int(os.getenv("CSMM_DEEP_SCAN_INTERVAL", "3600")),  # 1 hour
        "component_timeout": int(os.getenv("CSMM_COMPONENT_TIMEOUT", "30")),  # 30 seconds
        "max_diagnostic_history": int(os.getenv("CSMM_MAX_DIAGNOSTIC_HISTORY", "100")),
        "health_check_grace_period": int(os.getenv("CSMM_HEALTH_CHECK_GRACE_PERIOD", "60")),  # 1 minute
    },

    "repair": {
        "auto_repair_enabled": os.getenv("CSMM_AUTO_REPAIR_ENABLED", "true").lower() == "true",
        "max_repair_attempts": int(os.getenv("CSMM_MAX_REPAIR_ATTEMPTS", "3")),
        "repair_retry_delay": int(os.getenv("CSMM_REPAIR_RETRY_DELAY", "60")),  # 1 minute
        "critical_repair_priority": "high",
        "repair_history_retention": int(os.getenv("CSMM_REPAIR_HISTORY_RETENTION", "100")),
    },

    "learning": {
        "min_samples_for_pattern": int(os.getenv("CSMM_MIN_SAMPLES_FOR_PATTERN", "3")),
        "confidence_threshold": float(os.getenv("CSMM_CONFIDENCE_THRESHOLD", "0.7")),
        "pattern_retention_days": int(os.getenv("CSMM_PATTERN_RETENTION_DAYS", "30")),
        "predictive_window_days": int(os.getenv("CSMM_PREDICTIVE_WINDOW_DAYS", "7")),
        "learning_data_backup_interval": int(os.getenv("CSMM_LEARNING_BACKUP_INTERVAL", "86400")),  # 24 hours
    },

    "security": {
        "caleon_integration_enabled": os.getenv("CSMM_CALEON_INTEGRATION", "true").lower() == "true",
        "security_check_timeout": int(os.getenv("CSMM_SECURITY_CHECK_TIMEOUT", "30")),
        "tamper_detection_enabled": os.getenv("CSMM_TAMPER_DETECTION", "true").lower() == "true",
        "drift_monitoring_enabled": os.getenv("CSMM_DRIFT_MONITORING", "true").lower() == "true",
    },

    "monitoring": {
        "telemetry_enabled": os.getenv("CSMM_TELEMETRY_ENABLED", "true").lower() == "true",
        "metrics_collection_interval": int(os.getenv("CSMM_METRICS_INTERVAL", "60")),  # 1 minute
        "alert_threshold_critical": float(os.getenv("CSMM_ALERT_THRESHOLD_CRITICAL", "0.8")),
        "alert_threshold_warning": float(os.getenv("CSMM_ALERT_THRESHOLD_WARNING", "0.6")),
    },

    "components": {
        "dals_api": {
            "name": "DALS API",
            "endpoint": os.getenv("DALS_API_ENDPOINT", "http://localhost:8003"),
            "health_endpoint": "/health",
            "timeout": 10,
            "critical": True,
        },
        "ucm_service": {
            "name": "UCM Service",
            "endpoint": os.getenv("UCM_ENDPOINT", "http://localhost:8080"),
            "health_endpoint": "/health",
            "timeout": 15,
            "critical": True,
        },
        "caleon_security": {
            "name": "Caleon Security Layer",
            "module": "iss_module.core.caleon_security_layer",
            "timeout": 5,
            "critical": True,
        },
        "database": {
            "name": "Database Connection",
            "connection_string": os.getenv("DATABASE_URL", ""),
            "timeout": 10,
            "critical": True,
        },
        "telemetry": {
            "name": "Telemetry Service",
            "endpoint": os.getenv("TELEMETRY_ENDPOINT", ""),
            "timeout": 10,
            "critical": False,
        },
        "inventory": {
            "name": "Inventory Service",
            "endpoint": os.getenv("INVENTORY_ENDPOINT", ""),
            "timeout": 10,
            "critical": False,
        },
        "voice_routes": {
            "name": "Voice Routes (TTS/STT)",
            "tts_endpoint": os.getenv("TTS_ENDPOINT", ""),
            "stt_endpoint": os.getenv("STT_ENDPOINT", ""),
            "timeout": 10,
            "critical": False,
        },
        "thinker_orchestrator": {
            "name": "Thinker/Orchestrator",
            "process_name": "thinker",
            "timeout": 30,
            "critical": True,
        },
        "task_orchestrator": {
            "name": "Task Orchestrator",
            "endpoint": os.getenv("TASK_ORCHESTRATOR_ENDPOINT", ""),
            "timeout": 15,
            "critical": True,
        },
        "reflection_vault": {
            "name": "Reflection Vault",
            "vault_path": "seeds/gpt_seed_vault/philosophical_vaults",
            "timeout": 10,
            "critical": True,
        },
        "voice_console": {
            "name": "Voice Console",
            "endpoint": os.getenv("VOICE_CONSOLE_ENDPOINT", ""),
            "timeout": 10,
            "critical": False,
        },
        "dashboard": {
            "name": "Dashboard Service",
            "endpoint": os.getenv("DASHBOARD_ENDPOINT", "http://localhost:8008"),
            "health_endpoint": "/health",
            "timeout": 10,
            "critical": False,
        },
    },

    "integrations": {
        "ucm_connector": {
            "enabled": os.getenv("UCM_CONNECTOR_ENABLED", "true").lower() == "true",
            "host": os.getenv("UCM_HOST", "localhost"),
            "port": int(os.getenv("UCM_PORT", "8081")),
            "timeout": 30,
            "retry_attempts": 3,
        },
        "reflection_vaults": {
            "enabled": os.getenv("REFLECTION_VAULTS_ENABLED", "true").lower() == "true",
            "a_priori_path": "seeds/gpt_seed_vault/philosophical_vaults/a_priori.json",
            "a_posteriori_path": "seeds/gpt_seed_vault/philosophical_vaults/a_posteriori.json",
            "synaptic_trace_path": "seeds/gpt_seed_vault/philosophical_vaults/synaptic_trace.json",
        },
    },
}

def get_config() -> Dict[str, Any]:
    """Get the complete CSMM configuration"""
    return CSMM_CONFIG

def get_service_config() -> Dict[str, Any]:
    """Get service-specific configuration"""
    return CSMM_CONFIG["service"]

def get_engine_config() -> Dict[str, Any]:
    """Get engine-specific configuration"""
    return CSMM_CONFIG["engine"]

def get_component_config(component_name: str) -> Dict[str, Any]:
    """Get configuration for a specific component"""
    return CSMM_CONFIG["components"].get(component_name, {})

def is_critical_component(component_name: str) -> bool:
    """Check if a component is marked as critical"""
    component = get_component_config(component_name)
    return component.get("critical", False)
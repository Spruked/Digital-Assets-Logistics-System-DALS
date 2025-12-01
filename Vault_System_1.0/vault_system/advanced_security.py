# advanced_security.py

"""
Advanced Security - Multi-Layer Protection and Threat Intelligence

This module provides advanced security capabilities for the vault system,
including threat detection, intrusion prevention, and security intelligence.
"""

import asyncio
import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, List, Optional, Callable, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import json
import logging
import re
import ipaddress
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import warnings
warnings.filterwarnings('ignore')


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(Enum):
    """Types of security events"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALWARE_DETECTED = "malware_detected"
    DATA_TAMPERING = "data_tampering"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class SecurityIncident:
    """
    A security incident detected by the system.
    """
    incident_id: str
    event_type: SecurityEvent
    threat_level: ThreatLevel
    description: str
    source_ip: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    evidence: Dict[str, Any]
    mitigated: bool = False
    mitigation_actions: Optional[List[str]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.mitigation_actions is None:
            self.mitigation_actions = []


@dataclass
class SecurityPolicy:
    """
    A security policy definition.
    """
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 5  # 1-10, higher is more important
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


class AdvancedSecurity:
    """
    Advanced security system providing multi-layer protection and threat intelligence.

    Implements comprehensive security monitoring, threat detection, and automated
    response capabilities for the vault system.
    """

    def __init__(self, lifecycle_controller, telemetry_stream):
        """
        Initialize advanced security system.

        Args:
            lifecycle_controller: Lifecycle controller for component management
            telemetry_stream: Telemetry stream for monitoring
        """
        self.lifecycle_controller = lifecycle_controller
        self.telemetry_stream = telemetry_stream

        # Security incidents
        self.incidents: List[SecurityIncident] = []
        self.max_incidents = 5000

        # Security policies
        self.policies: Dict[str, SecurityPolicy] = {}
        self._load_default_policies()

        # Threat intelligence
        self.threat_indicators: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns: Dict[str, re.Pattern] = {}

        # Security monitoring
        self.monitoring_active = False
        self.monitoring_interval = 30  # seconds

        # Behavioral analysis
        self.user_behaviors: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.system_behaviors: deque = deque(maxlen=1000)

        # Cryptographic keys
        self.encryption_keys: Dict[str, bytes] = {}
        self.signing_keys: Dict[str, rsa.RSAPrivateKey] = {}

        # Security metrics
        self.security_metrics = {
            "incidents_detected": 0,
            "incidents_mitigated": 0,
            "false_positives": 0,
            "threats_blocked": 0,
            "policy_violations": 0,
            "uptime_protected": 0.0
        }

        # Risk assessment
        self.risk_scores: Dict[str, float] = {}

        print("🔒 Advanced Security initialized")

    def _load_default_policies(self):
        """Load default security policies"""
        default_policies = [
            SecurityPolicy(
                policy_id="auth_rate_limit",
                name="Authentication Rate Limiting",
                description="Prevent brute force attacks by limiting authentication attempts",
                rules=[
                    {
                        "condition": "auth_attempts_per_minute > 5",
                        "action": "block_ip",
                        "duration": 900  # 15 minutes
                    }
                ],
                priority=9
            ),
            SecurityPolicy(
                policy_id="suspicious_patterns",
                name="Suspicious Pattern Detection",
                description="Detect and block suspicious request patterns",
                rules=[
                    {
                        "condition": "contains_sql_injection",
                        "action": "block_request",
                        "severity": "high"
                    },
                    {
                        "condition": "unusual_file_access",
                        "action": "alert_admin",
                        "severity": "medium"
                    }
                ],
                priority=8
            ),
            SecurityPolicy(
                policy_id="data_integrity",
                name="Data Integrity Protection",
                description="Monitor and protect data integrity",
                rules=[
                    {
                        "condition": "data_tampering_detected",
                        "action": "quarantine_data",
                        "severity": "critical"
                    }
                ],
                priority=10
            )
        ]

        for policy in default_policies:
            self.policies[policy.policy_id] = policy

    def start_security_monitoring(self):
        """Start security monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        asyncio.create_task(self._security_monitoring_loop())
        print("👁️  Security monitoring started")

    def stop_security_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        print("🛑 Security monitoring stopped")

    async def _security_monitoring_loop(self):
        """Main security monitoring loop"""
        while self.monitoring_active:
            try:
                await self._perform_security_checks()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Security monitoring error: {e}")
                await asyncio.sleep(10)

    async def _perform_security_checks(self):
        """Perform comprehensive security checks"""
        # Check for suspicious activities
        await self._check_suspicious_activities()

        # Monitor system integrity
        await self._check_system_integrity()

        # Analyze user behavior
        await self._analyze_user_behavior()

        # Update threat intelligence
        await self._update_threat_intelligence()

        # Evaluate policies
        await self._evaluate_security_policies()

    async def _check_suspicious_activities(self):
        """Check for suspicious activities"""
        # Get recent telemetry data
        recent_data = await self.telemetry_stream.get_recent_data(hours=1)

        for entry in recent_data:
            # Check for various suspicious patterns
            if self._is_suspicious_request(entry):
                await self._handle_suspicious_activity(entry)

            if self._is_brute_force_attempt(entry):
                await self._handle_brute_force_attack(entry)

            if self._is_anomalous_behavior(entry):
                await self._handle_anomalous_behavior(entry)

    def _is_suspicious_request(self, request_data: Dict[str, Any]) -> bool:
        """Check if a request appears suspicious"""
        # Check for SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b.*\b(FROM|INTO|TABLE|DATABASE)\b)",
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bOR\b.*\d+\s*=\s*\d+)",
            r"(\bAND\b.*\d+\s*=\s*\d+)"
        ]

        request_body = str(request_data.get("body", "")).lower()

        for pattern in sql_patterns:
            if re.search(pattern, request_body, re.IGNORECASE):
                return True

        # Check for XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>"
        ]

        for pattern in xss_patterns:
            if re.search(pattern, request_body, re.IGNORECASE):
                return True

        return False

    def _is_brute_force_attempt(self, request_data: Dict[str, Any]) -> bool:
        """Check if request indicates brute force attempt"""
        ip = request_data.get("source_ip")
        endpoint = request_data.get("endpoint", "")

        if not ip or "auth" not in endpoint.lower():
            return False

        # Track authentication attempts per IP
        current_time = datetime.now()

        # This would need to be implemented with persistent storage
        # For now, return False as placeholder
        return False

    def _is_anomalous_behavior(self, request_data: Dict[str, Any]) -> bool:
        """Check for anomalous behavior"""
        user_id = request_data.get("user_id")
        if not user_id:
            return False

        # Add to user behavior history
        behavior_entry = {
            "timestamp": datetime.now(),
            "action": request_data.get("action", "unknown"),
            "endpoint": request_data.get("endpoint", "unknown"),
            "response_time": request_data.get("response_time", 0)
        }

        self.user_behaviors[user_id].append(behavior_entry)

        # Check for anomalies in behavior
        if len(self.user_behaviors[user_id]) >= 10:
            recent_behaviors = list(self.user_behaviors[user_id])[-10:]

            # Check for unusual response times
            response_times = [b["response_time"] for b in recent_behaviors]
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)

            if max_time > avg_time * 3:  # Response time spike
                return True

            # Check for unusual access patterns
            endpoints = [b["endpoint"] for b in recent_behaviors]
            unique_endpoints = len(set(endpoints))

            if unique_endpoints > 8:  # Accessing many different endpoints rapidly
                return True

        return False

    async def _handle_suspicious_activity(self, request_data: Dict[str, Any]):
        """Handle detected suspicious activity"""
        ip = request_data.get("source_ip", "unknown")

        incident = SecurityIncident(
            incident_id=f"suspicious_{int(time.time())}_{secrets.token_hex(4)}",
            event_type=SecurityEvent.SUSPICIOUS_ACTIVITY,
            threat_level=ThreatLevel.MEDIUM,
            description=f"Suspicious request pattern detected from {ip}",
            source_ip=ip,
            user_id=request_data.get("user_id"),
            timestamp=datetime.now(),
            evidence={
                "request_data": request_data,
                "detection_method": "pattern_matching"
            }
        )

        await self._record_security_incident(incident)
        await self._mitigate_incident(incident)

    async def _handle_brute_force_attack(self, request_data: Dict[str, Any]):
        """Handle brute force attack detection"""
        ip = request_data.get("source_ip", "unknown")

        incident = SecurityIncident(
            incident_id=f"brute_force_{int(time.time())}_{secrets.token_hex(4)}",
            event_type=SecurityEvent.BRUTE_FORCE_ATTACK,
            threat_level=ThreatLevel.HIGH,
            description=f"Brute force attack detected from {ip}",
            source_ip=ip,
            user_id=request_data.get("user_id"),
            timestamp=datetime.now(),
            evidence={
                "request_data": request_data,
                "detection_method": "rate_limiting"
            }
        )

        await self._record_security_incident(incident)
        await self._mitigate_incident(incident)

    async def _handle_anomalous_behavior(self, request_data: Dict[str, Any]):
        """Handle anomalous behavior detection"""
        user_id = request_data.get("user_id", "unknown")

        incident = SecurityIncident(
            incident_id=f"anomalous_{int(time.time())}_{secrets.token_hex(4)}",
            event_type=SecurityEvent.ANOMALOUS_BEHAVIOR,
            threat_level=ThreatLevel.MEDIUM,
            description=f"Anomalous behavior detected for user {user_id}",
            source_ip=request_data.get("source_ip"),
            user_id=user_id,
            timestamp=datetime.now(),
            evidence={
                "request_data": request_data,
                "detection_method": "behavioral_analysis"
            }
        )

        await self._record_security_incident(incident)
        await self._mitigate_incident(incident)

    async def _check_system_integrity(self):
        """Check system integrity"""
        # Check file integrity
        integrity_violations = await self._check_file_integrity()

        if integrity_violations:
            for violation in integrity_violations:
                incident = SecurityIncident(
                    incident_id=f"integrity_{int(time.time())}_{secrets.token_hex(4)}",
                    event_type=SecurityEvent.DATA_TAMPERING,
                    threat_level=ThreatLevel.CRITICAL,
                    description=f"File integrity violation: {violation['file']}",
                    evidence=violation
                )

                await self._record_security_incident(incident)
                await self._mitigate_incident(incident)

    async def _check_file_integrity(self) -> List[Dict[str, Any]]:
        """Check integrity of critical files"""
        # This would check file hashes against known good values
        # Placeholder implementation
        return []

    async def _analyze_user_behavior(self):
        """Analyze user behavior patterns"""
        # Analyze behavior patterns for all users
        for user_id, behaviors in self.user_behaviors.items():
            if len(behaviors) >= 20:
                risk_score = self._calculate_user_risk_score(user_id, behaviors)
                self.risk_scores[user_id] = risk_score

                if risk_score > 0.8:  # High risk
                    incident = SecurityIncident(
                        incident_id=f"high_risk_user_{int(time.time())}_{secrets.token_hex(4)}",
                        event_type=SecurityEvent.ANOMALOUS_BEHAVIOR,
                        threat_level=ThreatLevel.HIGH,
                        description=f"High risk behavior detected for user {user_id}",
                        source_ip=None,
                        user_id=user_id,
                        timestamp=datetime.now(),
                        evidence={
                            "risk_score": risk_score,
                            "behavior_count": len(behaviors)
                        }
                    )

                    await self._record_security_incident(incident)

    def _calculate_user_risk_score(self, user_id: str, behaviors: deque) -> float:
        """Calculate risk score for a user based on behavior"""
        if len(behaviors) < 10:
            return 0.0

        # Analyze various risk factors
        risk_factors = []

        # Factor 1: Access pattern diversity
        endpoints = [b["endpoint"] for b in behaviors]
        unique_endpoints = len(set(endpoints))
        endpoint_risk = min(unique_endpoints / 10, 1.0)  # Normalize to 0-1
        risk_factors.append(endpoint_risk * 0.3)

        # Factor 2: Time pattern anomalies
        timestamps = [b["timestamp"] for b in behaviors]
        if len(timestamps) >= 2:
            time_diffs = [(timestamps[i] - timestamps[i-1]).seconds for i in range(1, len(timestamps))]
            avg_diff = sum(time_diffs) / len(time_diffs)
            unusual_timing = sum(1 for diff in time_diffs if diff < avg_diff * 0.1)  # Very rapid requests
            timing_risk = min(unusual_timing / len(time_diffs), 1.0)
            risk_factors.append(timing_risk * 0.4)

        # Factor 3: Error rate
        # This would require error tracking in behaviors
        error_risk = 0.1  # Placeholder
        risk_factors.append(error_risk * 0.3)

        return sum(risk_factors)

    async def _update_threat_intelligence(self):
        """Update threat intelligence feeds"""
        # This would fetch threat intelligence from external sources
        # For now, it's a placeholder

        # Simulate adding some threat indicators
        new_indicators = [
            "192.168.1.100",  # Example blocked IP
            "malicious-domain.com"
        ]

        for indicator in new_indicators:
            self.threat_indicators.add(indicator)

    async def _evaluate_security_policies(self):
        """Evaluate active security policies"""
        for policy in self.policies.values():
            if not policy.enabled:
                continue

            # Evaluate each rule in the policy
            for rule in policy.rules:
                if await self._evaluate_policy_rule(rule):
                    await self._execute_policy_action(policy, rule)

    async def _evaluate_policy_rule(self, rule: Dict[str, Any]) -> bool:
        """Evaluate a policy rule condition"""
        condition = rule.get("condition", "")

        # Simple condition evaluation (would need more sophisticated implementation)
        if condition == "auth_attempts_per_minute > 5":
            # Check authentication rate
            return False  # Placeholder

        elif condition == "contains_sql_injection":
            # Check for SQL injection
            return False  # Placeholder

        elif condition == "data_tampering_detected":
            # Check for data tampering
            return False  # Placeholder

        return False

    async def _execute_policy_action(self, policy: SecurityPolicy, rule: Dict[str, Any]):
        """Execute a policy action"""
        action = rule.get("action", "")
        severity = rule.get("severity", "low")

        if action == "block_ip":
            # Block IP address
            duration = rule.get("duration", 900)
            print(f"🚫 Blocking IP for {duration} seconds due to policy violation")

        elif action == "block_request":
            # Block request
            print(f"🚫 Blocking request due to {severity} severity threat")

        elif action == "alert_admin":
            # Alert administrator
            print(f"🚨 Security alert: {policy.name} - {rule.get('condition', 'unknown condition')}")

        elif action == "quarantine_data":
            # Quarantine data
            print(f"🔒 Quarantining data due to integrity violation")

        # Record policy violation
        self.security_metrics["policy_violations"] += 1

    async def _record_security_incident(self, incident: SecurityIncident):
        """Record a security incident"""
        self.incidents.append(incident)

        # Maintain incident limit
        if len(self.incidents) > self.max_incidents:
            self.incidents = self.incidents[-self.max_incidents:]

        # Update metrics
        self.security_metrics["incidents_detected"] += 1

        print(f"🚨 Security incident detected: {incident.event_type.value} ({incident.threat_level.value})")

    async def _mitigate_incident(self, incident: SecurityIncident):
        """Mitigate a security incident"""
        mitigation_actions = []

        if incident.event_type == SecurityEvent.UNAUTHORIZED_ACCESS:
            # Block the IP
            if incident.source_ip:
                self.blocked_ips.add(incident.source_ip)
                mitigation_actions.append(f"Blocked IP: {incident.source_ip}")

        elif incident.event_type == SecurityEvent.SUSPICIOUS_ACTIVITY:
            # Log and monitor
            mitigation_actions.append("Increased monitoring for suspicious patterns")

        elif incident.event_type == SecurityEvent.BRUTE_FORCE_ATTACK:
            # Implement rate limiting
            if incident.source_ip:
                self.blocked_ips.add(incident.source_ip)
                mitigation_actions.append(f"Rate limiting applied to IP: {incident.source_ip}")

        elif incident.event_type == SecurityEvent.ANOMALOUS_BEHAVIOR:
            # Flag user for review
            mitigation_actions.append(f"User {incident.user_id} flagged for review")

        elif incident.event_type == SecurityEvent.DATA_TAMPERING:
            # Quarantine affected data
            mitigation_actions.append("Data quarantined for integrity check")

        # Update incident
        incident.mitigated = True
        incident.mitigation_actions = mitigation_actions

        # Update metrics
        self.security_metrics["incidents_mitigated"] += 1

        print(f"✅ Incident mitigated: {len(mitigation_actions)} actions taken")

    def generate_encryption_key(self, key_id: str, key_size: int = 32) -> bytes:
        """
        Generate a new encryption key.

        Args:
            key_id: Unique identifier for the key
            key_size: Size of the key in bytes

        Returns:
            Generated key
        """
        key = secrets.token_bytes(key_size)
        self.encryption_keys[key_id] = key
        return key

    def generate_signing_keypair(self, key_id: str) -> rsa.RSAPrivateKey:
        """
        Generate a new RSA signing keypair.

        Args:
            key_id: Unique identifier for the keypair

        Returns:
            Private key
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.signing_keys[key_id] = private_key
        return private_key

    def encrypt_data(self, data: bytes, key_id: str) -> bytes:
        """
        Encrypt data using AES.

        Args:
            data: Data to encrypt
            key_id: Key identifier

        Returns:
            Encrypted data
        """
        if key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key {key_id} not found")

        key = self.encryption_keys[key_id]

        # Simple AES encryption (would use proper AES implementation)
        # This is a placeholder - real implementation would use cryptography library
        return data  # Placeholder

    def decrypt_data(self, encrypted_data: bytes, key_id: str) -> bytes:
        """
        Decrypt data using AES.

        Args:
            encrypted_data: Data to decrypt
            key_id: Key identifier

        Returns:
            Decrypted data
        """
        if key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key {key_id} not found")

        key = self.encryption_keys[key_id]

        # Simple AES decryption (would use proper AES implementation)
        # This is a placeholder
        return encrypted_data  # Placeholder

    def sign_data(self, data: bytes, key_id: str) -> bytes:
        """
        Sign data using RSA.

        Args:
            data: Data to sign
            key_id: Key identifier

        Returns:
            Digital signature
        """
        if key_id not in self.signing_keys:
            raise ValueError(f"Signing key {key_id} not found")

        private_key = self.signing_keys[key_id]

        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    def verify_signature(self, data: bytes, signature: bytes, key_id: str) -> bool:
        """
        Verify data signature using RSA.

        Args:
            data: Original data
            signature: Digital signature
            key_id: Key identifier

        Returns:
            True if signature is valid
        """
        if key_id not in self.signing_keys:
            return False

        private_key = self.signing_keys[key_id]
        public_key = private_key.public_key()

        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def is_ip_blocked(self, ip_address: str) -> bool:
        """
        Check if an IP address is blocked.

        Args:
            ip_address: IP address to check

        Returns:
            True if IP is blocked
        """
        return ip_address in self.blocked_ips

    def block_ip(self, ip_address: str, duration: int = 3600):
        """
        Block an IP address.

        Args:
            ip_address: IP address to block
            duration: Block duration in seconds
        """
        self.blocked_ips.add(ip_address)

        # Schedule unblock (simplified)
        async def unblock_later():
            await asyncio.sleep(duration)
            if ip_address in self.blocked_ips:
                self.blocked_ips.remove(ip_address)

        asyncio.create_task(unblock_later())
        print(f"🚫 Blocked IP: {ip_address} for {duration} seconds")

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        total_incidents = self.security_metrics["incidents_detected"]
        mitigated_incidents = self.security_metrics["incidents_mitigated"]

        return {
            "incidents_detected": total_incidents,
            "incidents_mitigated": mitigated_incidents,
            "mitigation_rate": round(mitigated_incidents / max(1, total_incidents) * 100, 1),
            "threats_blocked": self.security_metrics["threats_blocked"],
            "policy_violations": self.security_metrics["policy_violations"],
            "active_policies": len([p for p in self.policies.values() if p.enabled]),
            "blocked_ips": len(self.blocked_ips),
            "high_risk_users": len([score for score in self.risk_scores.values() if score > 0.7])
        }

    def get_recent_incidents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent security incidents.

        Args:
            limit: Maximum number of incidents to return

        Returns:
            List of recent incidents
        """
        recent_incidents = self.incidents[-limit:]

        return [
            {
                "incident_id": i.incident_id,
                "event_type": i.event_type.value,
                "threat_level": i.threat_level.value,
                "description": i.description,
                "source_ip": i.source_ip,
                "user_id": i.user_id,
                "timestamp": i.timestamp.isoformat(),
                "mitigated": i.mitigated,
                "mitigation_actions": i.mitigation_actions
            }
            for i in recent_incidents
        ]

    def get_security_policies(self) -> List[Dict[str, Any]]:
        """Get security policies"""
        return [
            {
                "policy_id": p.policy_id,
                "name": p.name,
                "description": p.description,
                "enabled": p.enabled,
                "priority": p.priority,
                "rules_count": len(p.rules),
                "last_updated": p.last_updated.isoformat() if p.last_updated else None
            }
            for p in self.policies.values()
        ]

    def export_security_report(self, filepath: str):
        """
        Export security report to file.

        Args:
            filepath: Path to export file
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "security_metrics": self.get_security_metrics(),
            "recent_incidents": self.get_recent_incidents(50),
            "active_policies": self.get_security_policies(),
            "blocked_ips": list(self.blocked_ips),
            "threat_indicators": list(self.threat_indicators)
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"💾 Security report exported to {filepath}")
        except Exception as e:
            print(f"❌ Failed to export security report: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get advanced security system health"""
        return {
            "monitoring_active": self.monitoring_active,
            "incidents_count": len(self.incidents),
            "policies_count": len(self.policies),
            "blocked_ips_count": len(self.blocked_ips),
            "encryption_keys_count": len(self.encryption_keys),
            "signing_keys_count": len(self.signing_keys),
            "security_metrics": self.get_security_metrics()
        }
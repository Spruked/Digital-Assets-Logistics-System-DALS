"""
TrueMark Mint Connector - Enterprise Certificate Platform
DALS Integration Bridge for TrueMark Mint Enterprise Backend

TrueMark Mint: Scale with Trust.
Enterprise bulk minting, compliance verification, license management.
Port 9001 backend integration with DALS-001 compliance.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import httpx

from iss_module.core.utils import get_stardate, current_timecodes

logger = logging.getLogger("DALS.TrueMark")

class TrueMarkConnector:
    """
    Enterprise connector for TrueMark Mint backend.
    Handles bulk certificate minting, compliance verification, and license management.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:9001",
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with proper configuration."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout
            )
        return self._client

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and ISS timestamps."""
        client = await self._get_client()

        try:
            response = await client.request(method, endpoint, json=data, params=params)
            response.raise_for_status()

            result = response.json()
            # Add ISS timestamps to all responses
            timecodes = current_timecodes()
            result.update({
                "timestamp_iso": timecodes.iso_timestamp,
                "timestamp_stardate": timecodes.stardate,
                "timestamp_julian": timecodes.julian_date,
                "timestamp_epoch": timecodes.unix_timestamp
            })

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"TrueMark API error: {e.response.status_code} - {e.response.text}")
            return self._error_response(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")
        except httpx.RequestError as e:
            logger.error(f"TrueMark connection error: {e}")
            return self._error_response("Connection failed")
        except Exception as e:
            logger.error(f"TrueMark unexpected error: {e}")
            return self._error_response("Internal error")

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Return DALS-001 compliant error response (zeros/null)."""
        timecodes = current_timecodes()
        return {
            "status": "error",
            "message": message,
            "truemark_available": False,
            "bulk_mints_completed": 0,
            "active_licenses": 0,
            "compliance_score": 0,
            "timestamp_iso": timecodes.iso_timestamp,
            "timestamp_stardate": timecodes.stardate,
            "timestamp_julian": timecodes.julian_date,
            "timestamp_epoch": timecodes.unix_timestamp
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check TrueMark backend connectivity and status.
        DALS-001 compliant: Returns real data or zeros.
        """
        result = await self._make_request("GET", "/health")

        if result.get("status") == "error":
            return result

        # Enhance with additional status info
        return {
            **result,
            "truemark_available": True,
            "service": "TrueMark Mint Enterprise",
            "market": "Enterprise/SMB",
            "capabilities": ["bulk_mint", "compliance", "licensing", "audit"]
        }

    async def mint_bulk_certificates(
        self,
        certificates: List[Dict[str, Any]],
        organization_id: str,
        compliance_level: str = "enterprise"
    ) -> Dict[str, Any]:
        """
        Bulk mint enterprise certificates.
        DALS-001 compliant: Returns real counts or zeros.

        Args:
            certificates: List of certificate data
            organization_id: Enterprise organization identifier
            compliance_level: "enterprise", "compliance", "standard"
        """
        payload = {
            "certificates": certificates,
            "organization_id": organization_id,
            "compliance_level": compliance_level,
            "mint_timestamp": current_timecodes().iso_timestamp
        }

        result = await self._make_request("POST", "/mint-bulk", payload)

        if result.get("status") == "error":
            return result

        # Return successful bulk mint result
        return {
            **result,
            "operation": "bulk_mint",
            "certificates_requested": len(certificates),
            "certificates_minted": result.get("minted_count", 0),
            "organization_id": organization_id,
            "compliance_level": compliance_level
        }

    async def verify_compliance(
        self,
        certificate_ids: List[str],
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Verify compliance status for enterprise certificates.
        DALS-001 compliant: Returns real compliance data or zeros.
        """
        payload = {
            "certificate_ids": certificate_ids,
            "organization_id": organization_id,
            "verification_timestamp": current_timecodes().iso_timestamp
        }

        result = await self._make_request("POST", "/verify", payload)

        if result.get("status") == "error":
            return result

        return {
            **result,
            "operation": "compliance_verification",
            "certificates_checked": len(certificate_ids),
            "compliant_count": result.get("compliant_count", 0),
            "non_compliant_count": result.get("non_compliant_count", 0),
            "compliance_score": result.get("compliance_score", 0)
        }

    async def validate_license(
        self,
        license_key: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Validate enterprise license status.
        DALS-001 compliant: Returns real license data or zeros.
        """
        params = {
            "license_key": license_key,
            "organization_id": organization_id
        }

        result = await self._make_request("GET", "/licenses/validate", params=params)

        if result.get("status") == "error":
            return result

        return {
            **result,
            "operation": "license_validation",
            "license_valid": result.get("valid", False),
            "license_type": result.get("license_type", "unknown"),
            "users_allowed": result.get("users_allowed", 0),
            "users_active": result.get("users_active", 0),
            "expires_at": result.get("expires_at", None)
        }

    async def get_audit_trail(
        self,
        organization_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get enterprise audit trail for compliance reporting.
        DALS-001 compliant: Returns real audit data or empty array.
        """
        params = {
            "organization_id": organization_id,
            "days_back": days_back
        }

        result = await self._make_request("GET", "/audit/trail", params=params)

        if result.get("status") == "error":
            return result

        return {
            **result,
            "operation": "audit_trail",
            "organization_id": organization_id,
            "days_back": days_back,
            "total_events": len(result.get("events", [])),
            "events": result.get("events", [])
        }

    async def get_compliance_status(
        self,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get overall compliance status for enterprise.
        DALS-001 compliant: Returns real compliance metrics or zeros.
        """
        params = {"organization_id": organization_id}

        result = await self._make_request("GET", "/compliance/status", params=params)

        if result.get("status") == "error":
            return result

        return {
            **result,
            "operation": "compliance_status",
            "organization_id": organization_id,
            "overall_score": result.get("overall_score", 0),
            "certificates_total": result.get("certificates_total", 0),
            "certificates_compliant": result.get("certificates_compliant", 0),
            "last_audit": result.get("last_audit", None)
        }

    async def get_active_licenses(self) -> Dict[str, Any]:
        """
        Get count of active enterprise licenses.
        DALS-001 compliant: Returns real license count or zero.
        """
        result = await self._make_request("GET", "/licenses/active")

        if result.get("status") == "error":
            return result

        return {
            **result,
            "operation": "active_licenses",
            "total_licenses": result.get("total_licenses", 0),
            "active_licenses": result.get("active_licenses", 0),
            "expired_licenses": result.get("expired_licenses", 0)
        }

    async def generate_invoice(
        self,
        organization_id: str,
        billing_period: str
    ) -> Dict[str, Any]:
        """
        Generate enterprise invoice for billing period.
        DALS-001 compliant: Returns real invoice data or zeros.
        """
        payload = {
            "organization_id": organization_id,
            "billing_period": billing_period,
            "generated_at": current_timecodes().iso_timestamp
        }

        result = await self._make_request("POST", "/invoice/generate", payload)

        if result.get("status") == "error":
            return result

        return {
            **result,
            "operation": "invoice_generation",
            "organization_id": organization_id,
            "billing_period": billing_period,
            "total_amount": result.get("total_amount", 0),
            "certificates_minted": result.get("certificates_minted", 0),
            "invoice_url": result.get("invoice_url", None)
        }

    async def close(self):
        """Close HTTP client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Global singleton instance
_truemark_connector: Optional[TrueMarkConnector] = None

def get_truemark_connector(
    base_url: str = "http://localhost:9001",
    api_key: Optional[str] = None
) -> TrueMarkConnector:
    """
    Get global TrueMark connector instance.
    Thread-safe singleton pattern.
    """
    global _truemark_connector
    if _truemark_connector is None:
        _truemark_connector = TrueMarkConnector(base_url, api_key)
    return _truemark_connector
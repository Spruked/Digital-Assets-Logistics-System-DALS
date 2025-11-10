"""
Alpha CertSig Elite Mint Connector
Integrates DALS with Alpha CertSig Elite NFT minting system
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.utils import current_timecodes

logger = logging.getLogger("DALS.AlphaCertSig")


class AlphaCertSigConnector:
    """
    Bridge between DALS and Alpha CertSig Elite Mint system
    Handles domain minting, verification, and vault integration
    """
    
    def __init__(self, base_url: str = "http://localhost:9000", api_key: Optional[str] = None):
        """
        Initialize Alpha CertSig connector
        
        Args:
            base_url: Alpha CertSig backend URL (default: localhost:9000)
            api_key: Optional API key for authenticated requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"Alpha CertSig connector initialized: {self.base_url}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Alpha CertSig backend health
        
        Returns:
            Health status with ISS timestamp
        """
        timecodes = current_timecodes()
        
        try:
            response = await self.client.get(f"{self.base_url}/")
            response.raise_for_status()
            
            return {
                "status": "connected",
                "alpha_certsig_available": True,
                "backend_response": response.json(),
                "timestamp_iso": timecodes.iso_timestamp,
                "timestamp_stardate": timecodes.stardate,
                "timestamp_julian": timecodes.julian_date,
                "timestamp_epoch": timecodes.unix_timestamp
            }
        except Exception as e:
            logger.error(f"Alpha CertSig health check failed: {e}")
            return {
                "status": "disconnected",
                "alpha_certsig_available": False,
                "error": str(e),
                "timestamp_iso": timecodes.iso_timestamp,
                "timestamp_stardate": timecodes.stardate
            }
    
    async def mint_certificate(
        self,
        certificate_type: str,
        recipient_address: str,
        metadata: Dict[str, Any],
        tld: str = "cert"
    ) -> Dict[str, Any]:
        """
        Mint an Alpha CertSig NFT certificate
        
        Args:
            certificate_type: K (Knowledge), H (Honor), E (Elite), L (Legacy)
            recipient_address: Wallet address receiving the NFT
            metadata: Certificate metadata (name, description, attributes)
            tld: Top-level domain (.cert, .vault, .heir, .leg, .sig)
        
        Returns:
            Mint operation result with ISS timestamps
        """
        timecodes = current_timecodes()
        
        payload = {
            "certificate_type": certificate_type,
            "recipient": recipient_address,
            "metadata": metadata,
            "tld": tld,
            "mint_timestamp_iso": timecodes.iso_timestamp,
            "mint_timestamp_stardate": timecodes.stardate,
            "mint_timestamp_julian": timecodes.julian_date,
            "mint_timestamp_epoch": timecodes.unix_timestamp,
            "anchor_hash": timecodes.anchor_hash
        }
        
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/mint",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Certificate minted: {certificate_type}.{tld} for {recipient_address}")
            
            return {
                "success": True,
                "mint_result": result,
                "certificate_type": certificate_type,
                "tld": tld,
                "recipient": recipient_address,
                "timestamp_iso": timecodes.iso_timestamp,
                "timestamp_stardate": timecodes.stardate,
                "timestamp_julian": timecodes.julian_date,
                "timestamp_epoch": timecodes.unix_timestamp
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Mint failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "timestamp_iso": timecodes.iso_timestamp
            }
        except Exception as e:
            logger.error(f"Mint exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp_iso": timecodes.iso_timestamp
            }
    
    async def verify_certificate(self, token_id: int) -> Dict[str, Any]:
        """
        Verify an Alpha CertSig certificate by token ID
        
        Args:
            token_id: NFT token identifier
        
        Returns:
            Certificate verification data
        """
        timecodes = current_timecodes()
        
        try:
            response = await self.client.get(f"{self.base_url}/api/nft/{token_id}")
            response.raise_for_status()
            
            return {
                "verified": True,
                "certificate_data": response.json(),
                "timestamp_iso": timecodes.iso_timestamp,
                "timestamp_stardate": timecodes.stardate
            }
        except Exception as e:
            logger.error(f"Verification failed for token {token_id}: {e}")
            return {
                "verified": False,
                "error": str(e),
                "timestamp_iso": timecodes.iso_timestamp
            }
    
    async def get_vault_status(self) -> Dict[str, Any]:
        """
        Get Alpha CertSig vault integration status
        
        Returns:
            Vault status with IPFS sync state
        """
        timecodes = current_timecodes()
        
        # TODO: Wire to actual vault endpoint when available
        return {
            "vault_active": False,  # DALS-001 compliant: real data or zero
            "ipfs_queue_length": 0,
            "sync_status": "offline",
            "timestamp_iso": timecodes.iso_timestamp,
            "timestamp_stardate": timecodes.stardate
        }
    
    async def close(self):
        """Close HTTP client connection"""
        await self.client.aclose()
        logger.info("Alpha CertSig connector closed")


# Global connector instance (lazy-loaded)
_connector: Optional[AlphaCertSigConnector] = None


def get_alpha_certsig_connector(
    base_url: str = "http://localhost:9000",
    api_key: Optional[str] = None
) -> AlphaCertSigConnector:
    """
    Get or create Alpha CertSig connector instance
    
    Args:
        base_url: Alpha CertSig backend URL
        api_key: Optional API key
    
    Returns:
        AlphaCertSigConnector instance
    """
    global _connector
    if _connector is None:
        _connector = AlphaCertSigConnector(base_url=base_url, api_key=api_key)
    return _connector

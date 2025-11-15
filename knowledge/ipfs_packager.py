# knowledge/ipfs_packager.py
import hashlib
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class IPFSPackager:
    """
    IPFS Packaging + Hashing Engine
    Stores knowledge payloads on IPFS with cryptographic integrity
    Phase 11-A2: Knowledge Preservation Pipeline
    """

    def __init__(self, ipfs_host: str = "localhost", ipfs_port: int = 5001):
        self.ipfs_host = ipfs_host
        self.ipfs_port = ipfs_port
        self.ipfs_client = None
        self._connect_ipfs()

    def _connect_ipfs(self):
        """Connect to IPFS node"""
        try:
            import ipfshttpclient
            self.ipfs_client = ipfshttpclient.connect(f'/ip4/{self.ipfs_host}/tcp/{self.ipfs_port}/http')
            logger.info(f"Connected to IPFS at {self.ipfs_host}:{self.ipfs_port}")
        except ImportError:
            logger.warning("ipfshttpclient not available - IPFS operations will be simulated")
            self.ipfs_client = None
        except Exception as e:
            logger.warning(f"Could not connect to IPFS: {e} - operations will be simulated")
            self.ipfs_client = None

    def _calculate_content_hash(self, content: Union[str, bytes]) -> str:
        """Calculate SHA-256 hash of content"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()

    def _calculate_merkle_root(self, data: Dict[str, Any]) -> str:
        """Calculate BLAKE2b Merkle root of structured data"""
        # Create deterministic JSON representation
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        return hashlib.blake2b(json_str.encode('utf-8'), digest_size=32).hexdigest()

    def _create_content_bundle(self, payload: Dict[str, Any], assets: List[Path] = None) -> Dict[str, Any]:
        """Create the complete content bundle for IPFS"""
        bundle = {
            "knowledge_payload": payload,
            "packaging_metadata": {
                "packaged_at": datetime.utcnow().isoformat() + "Z",
                "packager_version": "IPFSPackager v1.0",
                "content_type": "knowledge_nft",
                "protocol_version": "1.0"
            },
            "assets": [],
            "integrity_checks": {}
        }

        # Add assets if provided
        if assets:
            for asset_path in assets:
                if asset_path.exists():
                    asset_info = self._process_asset(asset_path)
                    bundle["assets"].append(asset_info)

        # Calculate integrity hashes
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        bundle["integrity_checks"] = {
            "payload_sha256": self._calculate_content_hash(payload_str),
            "bundle_blake2b": self._calculate_merkle_root(bundle),
            "timestamp_hash": self._calculate_content_hash(datetime.utcnow().isoformat())
        }

        return bundle

    def _process_asset(self, asset_path: Path) -> Dict[str, Any]:
        """Process an asset file for inclusion"""
        asset_info = {
            "filename": asset_path.name,
            "path": str(asset_path),
            "size_bytes": asset_path.stat().st_size,
            "modified_at": datetime.fromtimestamp(asset_path.stat().st_mtime).isoformat() + "Z"
        }

        # Calculate file hash
        with open(asset_path, 'rb') as f:
            file_content = f.read()
            asset_info["sha256_hash"] = self._calculate_content_hash(file_content)

        # Determine content type
        suffix = asset_path.suffix.lower()
        if suffix in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            asset_info["content_type"] = "image"
        elif suffix in ['.mp4', '.avi', '.mov', '.webm']:
            asset_info["content_type"] = "video"
        elif suffix in ['.mp3', '.wav', '.flac']:
            asset_info["content_type"] = "audio"
        elif suffix in ['.pdf']:
            asset_info["content_type"] = "document"
        else:
            asset_info["content_type"] = "file"

        # Add IPFS CID if client available
        if self.ipfs_client:
            try:
                cid = self.ipfs_client.add_bytes(file_content)
                asset_info["ipfs_cid"] = cid
                asset_info["ipfs_url"] = f"ipfs://{cid}"
                asset_info["gateway_url"] = f"https://ipfs.io/ipfs/{cid}"
            except Exception as e:
                logger.warning(f"Failed to add asset {asset_path} to IPFS: {e}")

        return asset_info

    def package(self, payload: Dict[str, Any], assets: List[Path] = None) -> Dict[str, Any]:
        """
        Package knowledge payload and assets for IPFS storage
        Returns IPFS packaging results
        """
        logger.info(f"Packaging knowledge payload for IPFS: {payload.get('expertise_level', 'Unknown')}")

        # Create content bundle
        bundle = self._create_content_bundle(payload, assets)

        # Convert bundle to bytes for IPFS
        bundle_json = json.dumps(bundle, sort_keys=True, ensure_ascii=True, indent=2)
        bundle_bytes = bundle_json.encode('utf-8')

        packaging_result = {
            "bundle_size_bytes": len(bundle_bytes),
            "content_hash": bundle["integrity_checks"]["payload_sha256"],
            "merkle_root": bundle["integrity_checks"]["bundle_blake2b"],
            "packaging_timestamp": bundle["packaging_metadata"]["packaged_at"],
            "asset_count": len(bundle["assets"]),
            "simulated": self.ipfs_client is None
        }

        # Add to IPFS if available
        if self.ipfs_client:
            try:
                main_cid = self.ipfs_client.add_bytes(bundle_bytes)
                packaging_result.update({
                    "cid": main_cid,
                    "ipfs_url": f"ipfs://{main_cid}",
                    "gateway_url": f"https://ipfs.io/ipfs/{main_cid}",
                    "filecoin_ready": True
                })

                # Pin the content for persistence
                try:
                    self.ipfs_client.pin.add(main_cid)
                    packaging_result["pinned"] = True
                except Exception as e:
                    logger.warning(f"Failed to pin CID {main_cid}: {e}")
                    packaging_result["pinned"] = False

                logger.info(f"Successfully stored on IPFS: {main_cid}")

            except Exception as e:
                logger.error(f"Failed to store on IPFS: {e}")
                packaging_result.update({
                    "cid": None,
                    "error": str(e),
                    "filecoin_ready": False
                })
        else:
            # Generate simulated CID for testing
            simulated_cid = base64.b32encode(hashlib.sha256(bundle_bytes).digest()[:20]).decode().lower() + '000000000000000000000000000'
            packaging_result.update({
                "cid": simulated_cid,
                "ipfs_url": f"ipfs://{simulated_cid}",
                "gateway_url": f"https://ipfs.io/ipfs/{simulated_cid}",
                "filecoin_ready": False,
                "note": "IPFS not available - using simulated CID for testing"
            })
            logger.info("IPFS not available - generated simulated CID for testing")

        # Add bundle metadata
        packaging_result["bundle_metadata"] = {
            "knowledge_items": len(payload.get("specialties", [])) + len(payload.get("procedures_mastered", [])),
            "teaching_points": len(payload.get("teaching_notes", [])),
            "years_experience": payload.get("years_experience", 0),
            "profession": payload.get("profession", "Unknown")
        }

        return packaging_result

    def verify_integrity(self, cid: str, expected_hash: str) -> Dict[str, Any]:
        """Verify integrity of stored content"""
        verification = {
            "verified": False,
            "cid": cid,
            "expected_hash": expected_hash,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if not self.ipfs_client:
            verification["error"] = "IPFS client not available"
            return verification

        try:
            # Retrieve content from IPFS
            content_bytes = self.ipfs_client.cat(cid)
            actual_hash = self._calculate_content_hash(content_bytes)

            verification.update({
                "verified": actual_hash == expected_hash,
                "actual_hash": actual_hash,
                "content_size": len(content_bytes)
            })

            if verification["verified"]:
                logger.info(f"Integrity verified for CID {cid}")
            else:
                logger.error(f"Integrity check FAILED for CID {cid}")

        except Exception as e:
            verification["error"] = str(e)
            logger.error(f"Failed to verify integrity for CID {cid}: {e}")

        return verification

    def get_storage_info(self, cid: str) -> Dict[str, Any]:
        """Get storage information for a CID"""
        info = {
            "cid": cid,
            "available": False,
            "size_bytes": 0,
            "pinned": False
        }

        if not self.ipfs_client:
            info["error"] = "IPFS client not available"
            return info

        try:
            # Check if CID exists
            stat = self.ipfs_client.files.stat(f"/ipfs/{cid}")
            info.update({
                "available": True,
                "size_bytes": stat.get("Size", 0),
                "cumulative_size": stat.get("CumulativeSize", 0)
            })

            # Check if pinned
            pins = self.ipfs_client.pin.ls()
            info["pinned"] = cid in pins

        except Exception as e:
            info["error"] = str(e)

        return info

    def create_backup_bundle(self, primary_cid: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup bundle for additional redundancy"""
        backup_bundle = {
            "primary_cid": primary_cid,
            "backup_created": datetime.utcnow().isoformat() + "Z",
            "payload_summary": {
                "expertise_level": payload.get("expertise_level"),
                "profession": payload.get("profession"),
                "years_experience": payload.get("years_experience"),
                "specialties_count": len(payload.get("specialties", []))
            },
            "backup_type": "knowledge_nft_redundancy"
        }

        # Store backup bundle
        backup_json = json.dumps(backup_bundle, sort_keys=True, ensure_ascii=True)
        backup_bytes = backup_json.encode('utf-8')

        backup_result = {
            "backup_hash": self._calculate_content_hash(backup_bytes),
            "backup_size": len(backup_bytes)
        }

        if self.ipfs_client:
            try:
                backup_cid = self.ipfs_client.add_bytes(backup_bytes)
                backup_result.update({
                    "backup_cid": backup_cid,
                    "backup_url": f"ipfs://{backup_cid}"
                })
            except Exception as e:
                logger.warning(f"Failed to create backup bundle: {e}")

        return backup_result
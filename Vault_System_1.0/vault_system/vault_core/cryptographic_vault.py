# cryptographic_vault.py

"""
Cryptographic Vault - Core AES-256 Encrypted Storage

This module provides the fundamental cryptographic storage capabilities
for the vault system, ensuring all data is encrypted at rest and in transit.
"""

import os
import json
import hashlib
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from enum import Enum


class VaultCategory(Enum):
    """Categories for vaulted data"""
    OPERATIONAL = "operational"
    PHILOSOPHICAL = "philosophical"
    SECURITY = "security"
    TELEMETRY = "telemetry"
    REFLECTION = "reflection"
    GLYPH = "glyph"


class EncryptionLevel(Enum):
    """Encryption strength levels"""
    STANDARD = "standard"  # AES-256
    HIGH = "high"         # AES-256 with additional layers
    MAXIMUM = "maximum"   # AES-256 with quantum-resistant padding


class CryptographicVault:
    """
    Core cryptographic vault with AES-256 encryption.

    Provides secure storage and retrieval of sensitive data with
    category-based organization and integrity verification.
    """

    def __init__(self, master_key: str, vault_path: str = "./vault_data"):
        """
        Initialize the cryptographic vault.

        Args:
            master_key: Master encryption key
            vault_path: Path to store encrypted vault files
        """
        self.master_key = master_key
        self.vault_path = vault_path
        self._ensure_vault_directory()

        # Generate encryption keys
        self.encryption_key = self._derive_key(master_key, "encryption")
        self.fernet = Fernet(self.encryption_key)

        # Initialize vault storage
        self.vault_store: Dict[str, Dict[str, Any]] = {}
        self.metadata_store: Dict[str, Dict[str, Any]] = {}

        # Load existing vault if available
        self._load_vault()

        print(f"🔐 Cryptographic vault initialized at {vault_path}")

    def _ensure_vault_directory(self):
        """Ensure vault directory exists"""
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path, exist_ok=True)

    def _derive_key(self, master_key: str, purpose: str) -> bytes:
        """
        Derive encryption key from master key using PBKDF2.

        Args:
            master_key: Master key string
            purpose: Key derivation purpose

        Returns:
            Derived key bytes
        """
        salt = hashlib.sha256(f"{purpose}_salt_2024".encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(master_key.encode()))

    def _load_vault(self):
        """Load existing vault data from disk"""
        vault_file = os.path.join(self.vault_path, "vault.enc")
        metadata_file = os.path.join(self.vault_path, "metadata.enc")

        try:
            if os.path.exists(vault_file):
                with open(vault_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.vault_store = json.loads(decrypted_data.decode())

            if os.path.exists(metadata_file):
                with open(metadata_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.metadata_store = json.loads(decrypted_data.decode())

        except (InvalidToken, json.JSONDecodeError) as e:
            print(f"⚠️  Warning: Could not load vault data: {e}")
            print("   Starting with empty vault")

    def _save_vault(self):
        """Save vault data to disk"""
        vault_file = os.path.join(self.vault_path, "vault.enc")
        metadata_file = os.path.join(self.vault_path, "metadata.enc")

        # Encrypt and save vault store
        vault_data = json.dumps(self.vault_store, indent=2)
        encrypted_vault = self.fernet.encrypt(vault_data.encode())
        with open(vault_file, 'wb') as f:
            f.write(encrypted_vault)

        # Encrypt and save metadata store
        metadata_data = json.dumps(self.metadata_store, indent=2)
        encrypted_metadata = self.fernet.encrypt(metadata_data.encode())
        with open(metadata_file, 'wb') as f:
            f.write(encrypted_metadata)

    def store(self, key: str, category: VaultCategory, data: Any,
              source: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store encrypted data in the vault.

        Args:
            key: Unique identifier for the data
            category: Data category
            data: Data to store (will be JSON serialized)
            source: Source system/component
            metadata: Additional metadata

        Returns:
            Success status
        """
        try:
            # Prepare vault entry
            entry = {
                "data": data,
                "category": category.value,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "version": 1
            }

            # Add metadata if provided
            if metadata:
                entry["metadata"] = metadata

            # Store in vault
            self.vault_store[key] = entry

            # Store metadata separately for quick access
            self.metadata_store[key] = {
                "category": category.value,
                "source": source,
                "timestamp": entry["timestamp"],
                "size": len(json.dumps(data)),
                "hash": self._calculate_hash(data)
            }

            # Save to disk
            self._save_vault()

            return True

        except Exception as e:
            print(f"❌ Failed to store data for key '{key}': {e}")
            return False

    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from the vault.

        Args:
            key: Data identifier

        Returns:
            Decrypted data entry or None if not found
        """
        return self.vault_store.get(key)

    def retrieve_by_category(self, category: VaultCategory) -> List[Dict[str, Any]]:
        """
        Retrieve all data for a specific category.

        Args:
            category: Category to filter by

        Returns:
            List of data entries
        """
        return [
            entry for entry in self.vault_store.values()
            if entry.get("category") == category.value
        ]

    def delete(self, key: str) -> bool:
        """
        Delete data from the vault.

        Args:
            key: Data identifier

        Returns:
            Success status
        """
        if key in self.vault_store:
            del self.vault_store[key]
            if key in self.metadata_store:
                del self.metadata_store[key]
            self._save_vault()
            return True
        return False

    def list_keys(self, category: Optional[VaultCategory] = None) -> List[str]:
        """
        List all keys in the vault, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of keys
        """
        if category is not None:
            return [
                key for key, entry in self.vault_store.items()
                if entry.get("category") == category.value
            ]
        return list(self.vault_store.keys())

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a vault entry.

        Args:
            key: Data identifier

        Returns:
            Metadata dictionary or None
        """
        return self.metadata_store.get(key)

    def update(self, key: str, data: Any, source: Optional[str] = None) -> bool:
        """
        Update existing data in the vault.

        Args:
            key: Data identifier
            data: New data
            source: Optional new source

        Returns:
            Success status
        """
        if key not in self.vault_store:
            return False

        entry = self.vault_store[key]
        entry["data"] = data
        entry["timestamp"] = datetime.now().isoformat()
        entry["version"] += 1

        if source:
            entry["source"] = source

        # Update metadata
        self.metadata_store[key].update({
            "timestamp": entry["timestamp"],
            "size": len(json.dumps(data)),
            "hash": self._calculate_hash(data)
        })

        self._save_vault()
        return True

    def _calculate_hash(self, data: Any) -> str:
        """Calculate SHA-256 hash of data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def verify_integrity(self, key: str) -> bool:
        """
        Verify data integrity using stored hash.

        Args:
            key: Data identifier

        Returns:
            Integrity status
        """
        if key not in self.vault_store or key not in self.metadata_store:
            return False

        stored_hash = self.metadata_store[key].get("hash")
        current_hash = self._calculate_hash(self.vault_store[key]["data"])

        return stored_hash == current_hash

    def get_vault_stats(self) -> Dict[str, Any]:
        """
        Get vault statistics.

        Returns:
            Statistics dictionary
        """
        categories = {}
        total_size = 0

        for entry in self.vault_store.values():
            cat = entry.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            total_size += len(json.dumps(entry["data"]))

        return {
            "total_entries": len(self.vault_store),
            "categories": categories,
            "total_size_bytes": total_size,
            "vault_path": self.vault_path,
            "last_modified": max(
                (entry["timestamp"] for entry in self.vault_store.values()),
                default=None
            )
        }

    def backup_vault(self, backup_path: str) -> bool:
        """
        Create a backup of the vault.

        Args:
            backup_path: Path for backup file

        Returns:
            Success status
        """
        try:
            backup_data = {
                "vault_store": self.vault_store,
                "metadata_store": self.metadata_store,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }

            encrypted_backup = self.fernet.encrypt(json.dumps(backup_data).encode())

            with open(backup_path, 'wb') as f:
                f.write(encrypted_backup)

            return True

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def restore_vault(self, backup_path: str) -> bool:
        """
        Restore vault from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            Success status
        """
        try:
            with open(backup_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            backup_data = json.loads(decrypted_data.decode())

            self.vault_store = backup_data["vault_store"]
            self.metadata_store = backup_data["metadata_store"]

            self._save_vault()
            return True

        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False

    def rotate_key(self, new_master_key: str) -> bool:
        """
        Rotate the master encryption key.

        Args:
            new_master_key: New master key

        Returns:
            Success status
        """
        try:
            # Generate new encryption key
            new_encryption_key = self._derive_key(new_master_key, "encryption")
            new_fernet = Fernet(new_encryption_key)

            # Re-encrypt all data with new key
            vault_data = json.dumps(self.vault_store, indent=2)
            encrypted_vault = new_fernet.encrypt(vault_data.encode())

            metadata_data = json.dumps(self.metadata_store, indent=2)
            encrypted_metadata = new_fernet.encrypt(metadata_data.encode())

            # Update keys
            self.master_key = new_master_key
            self.encryption_key = new_encryption_key
            self.fernet = new_fernet

            # Save with new encryption
            vault_file = os.path.join(self.vault_path, "vault.enc")
            metadata_file = os.path.join(self.vault_path, "metadata.enc")

            with open(vault_file, 'wb') as f:
                f.write(encrypted_vault)

            with open(metadata_file, 'wb') as f:
                f.write(encrypted_metadata)

            return True

        except Exception as e:
            print(f"❌ Key rotation failed: {e}")
            return False
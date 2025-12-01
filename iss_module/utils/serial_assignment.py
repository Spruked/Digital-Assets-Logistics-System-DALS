import uuid
import hashlib
import json
from datetime import datetime
from typing import Literal, Dict, Any, Optional
import os

# --- CONFIGURATION ---
VAULT_PATH = "vault/sig_serial_vault.jsonl"
HASH_LENGTH = 8  # Total length of the entropy hash part
GLYPH_CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # Custom set to avoid confusing characters

# --- ISS-Compatible Timestamp Placeholder ---
def get_iss_timestamp() -> str:
    """Returns a precise, time-anchored timestamp."""
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S.%fZ")

# --- Vault & Glyph Logic ---

def get_last_vault_hash() -> str:
    """Reads the last line of the .jsonl vault and returns its 'vault_self_hash'."""
    if not os.path.exists(VAULT_PATH) or os.path.getsize(VAULT_PATH) == 0:
        return "0" * 64  # Genesis hash for the very first record

    try:
        with open(VAULT_PATH, 'rb') as f:
            # Seek to the end of the file and read backwards to find the last line
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode('utf-8')
        
        last_record = json.loads(last_line)
        return last_record.get("vault_self_hash", "0" * 64)
    except Exception:
        # Fallback for corrupted file or single-line file
        with open(VAULT_PATH, 'r') as f:
            lines = f.readlines()
            if not lines:
                return "0" * 64
            last_record = json.loads(lines[-1])
            return last_record.get("vault_self_hash", "0" * 64)

def create_vault_record_hash(record_data: Dict[str, Any], previous_hash: str) -> str:
    """Generates the integrity hash for the new record."""
    # Convert data to a consistent string format, prepend previous hash, and hash the result
    data_string = f"{previous_hash}|{json.dumps(record_data, sort_keys=True)}"
    return hashlib.sha256(data_string.encode()).hexdigest()

def generate_glyph(serial_components: str) -> str:
    """Generates a 3-character verification glyph based on the input string."""
    ascii_sum = sum(ord(c) for c in serial_components)
    glyph = ""
    for i in range(3):
        index = (ascii_sum + i) % len(GLYPH_CHARACTERS)
        glyph += GLYPH_CHARACTERS[index]
        ascii_sum = (ascii_sum * 7) + 1 
    return glyph

# --- Core Logic Functions ---

def generate_entropy_hash() -> str:
    """Generates a short, unique hash for the serial."""
    raw_hash = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    entropy = raw_hash[:HASH_LENGTH]
    return f"{entropy[:4]}-{entropy[4:]}".upper()

def write_to_vault(data: Dict[str, Any]) -> None:
    """Appends a new record to the sig_serial_vault.jsonl file."""
    try:
        # 1. Get the hash of the last entry
        previous_hash = get_last_vault_hash()
        
        # 2. Add the previous hash to the record before hashing
        data["vault_prev_hash"] = previous_hash
        
        # 3. Create the new integrity hash for this record
        self_hash = create_vault_record_hash(data, previous_hash)
        data["vault_self_hash"] = self_hash
        
        # 4. Write the completed record to the file
        with open(VAULT_PATH, 'a') as f:
            json_line = json.dumps(data)
            f.write(json_line + '\n')
    except Exception as e:
        print(f"ERROR: Could not write to vault: {e}")
        raise

def assign_digital_asset_id(
    asset_type: Literal["FEATURE", "EPIC", "BUILD", "SERVICE", "ARTIFACT"],
    project_id: str,
    source_reference: str,
    parent_asset_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a Digital Asset ID with a verification glyph, an audit hash, 
    and logs it to the chained vault.
    """
    
    # 1. Generate core components
    entropy_hash = generate_entropy_hash()
    timestamp = get_iss_timestamp()
    
    # 2. Generate the verification glyph from the core components
    components_for_glyph = f"{asset_type.upper()}-{project_id.upper()}-{source_reference.upper()}"
    glyph = generate_glyph(components_for_glyph)

    # 3. Assemble the main asset ID string, now including the glyph
    asset_id_string = (
        f"{asset_type.upper()}-{project_id.upper()}-{source_reference.upper()}-"
        f"{entropy_hash}-{glyph}"
    )
    
    # 4. Create a comprehensive audit hash (distinct from the vault chain hash)
    audit_data = f"{asset_id_string}|{timestamp}|{asset_type}|{project_id}|{source_reference}|{parent_asset_id or ''}"
    audit_hash = hashlib.sha256(audit_data.encode()).hexdigest()
    
    # 5. Prepare the vault record
    vault_record = {
        "asset_id": asset_id_string,
        "type": asset_type.upper(),
        "project_id": project_id.upper(),
        "source_reference": source_reference.upper(),
        "parent_asset_id": parent_asset_id,
        "timestamp": timestamp,
        "audit_hash": audit_hash,
        "entropy": entropy_hash.replace('-', ''),
        "glyph": glyph,
    }
    
    # 6. Write to the append-only, chained vault
    write_to_vault(vault_record)
    
    # 7. Return the key data for the API response
    return {
        "asset_id": asset_id_string,
        "iss_timestamp": timestamp,
        "audit_hash": audit_hash,
        "status": "ASSIGNED_AND_LOGGED",
        "parent_asset_id": parent_asset_id,
        "glyph": glyph
    }

# Example of how to call the function directly (for testing)
if __name__ == "__main__":
    print("--- Digital Asset Logistics System (DALS) Test ---")
    
    # Example 1: Standard Feature Asset
    result_feature = assign_digital_asset_id(
        asset_type="FEATURE", 
        project_id="CORE-API", 
        source_reference="v1.2.0"
    )
    print("\nFEATURE Asset Assigned:")
    print(json.dumps(result_feature, indent=2))
    
    # Example 2: Build Artifact with a parent Epic
    result_build = assign_digital_asset_id(
        asset_type="BUILD", 
        project_id="WEB-APP", 
        source_reference="a4b2c8d9",
        parent_asset_id="EPIC-WEB-APP-LOGIN-FLOW-B2A1-C3D4"
    )
    print("\nBUILD Asset Assigned:")
    print(json.dumps(result_build, indent=2))
    
    print(f"\nCheck the vault file: {VAULT_PATH}")

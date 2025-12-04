"""
DALS Registration Script for Josephine TrueMark Worker
=======================================================
Assigns a DALS serial number and registers Josephine in the inventory system.

Model ID: WORKER-TRUEMARK-MINT-V1
Type: AI Worker (Host Bubble)
Purpose: NFT Minting Specialist
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from serial_assignment import assign_digital_asset_id
from iss_module.inventory.inventory_manager import UnitInventoryManager
from iss_module.core.utils import get_stardate


async def register_josephine_worker():
    """
    Register Josephine in DALS with proper serial assignment and inventory tracking.
    
    Model Taxonomy:
    - DMN-TM-01 = DALS Model Number for TrueMark Worker Generation 1
    - DSN = DALS Serial Number with embedded timestamp and UUID
    """
    
    print("=" * 70)
    print("DALS Worker Registration System")
    print("Registering: Josephine - TrueMark NFT Mint Specialist")
    print("=" * 70)
    
    # Step 1: Assign Digital Asset ID using DALS serial assignment
    print("\n[1/4] Assigning DALS Serial Number...")
    
    asset_data = assign_digital_asset_id(
        asset_type="SERVICE",
        project_id="WORKER-TRUEMARK-MINT",
        source_reference="V1",
        parent_asset_id="SERVICE-DALS-TRUEMARK-MINT-API-V1" if Path("vault/sig_serial_vault.jsonl").exists() else None
    )
    
    serial_number = asset_data["asset_id"]
    audit_hash = asset_data["audit_hash"]
    glyph = asset_data["glyph"]
    
    print(f"   ✓ Serial Number: {serial_number}")
    print(f"   ✓ Audit Hash: {audit_hash[:16]}...")
    print(f"   ✓ Verification Glyph: {glyph}")
    
    # Step 2: Create inventory record
    print("\n[2/4] Creating Inventory Record...")
    
    inventory_mgr = UnitInventoryManager()
    await inventory_mgr.initialize()
    
    unit_record = await inventory_mgr.create_unit_record(
        unit_serial=serial_number,
        model_id="WORKER-TRUEMARK-MINT-V1",
        deployment_location="DALS-Controller/Worker-Pool",
        initial_audit_hash=audit_hash,
        source_unit_serial=None,
        audited_by="DALS-Founder-Bryan-Spruk"
    )
    
    print(f"   ✓ Inventory Record Created")
    print(f"   ✓ Status: {unit_record.status}")
    print(f"   ✓ Deployment: {unit_record.deployment_environment}")
    
    # Step 3: Update status to DEPLOYED
    print("\n[3/4] Updating Deployment Status...")
    
    await inventory_mgr.update_unit_status(
        unit_serial=serial_number,
        new_status="DEPLOYED",
        update_details="Josephine TrueMark Worker deployed and operational. Endpoints: /predicate, /health, /mint/callback. Capabilities: NFT minting guidance, wallet connection, IPFS storage, blockchain certificates.",
        components_update=None,
        audited_by="DALS-Founder-Bryan-Spruk"
    )
    
    print(f"   ✓ Status Updated: DEPLOYED")
    
    # Step 4: Create deployment manifest
    print("\n[4/4] Generating Deployment Manifest...")
    
    stardate = get_stardate()
    
    manifest = {
        "worker_name": "Josephine",
        "worker_type": "Host Bubble Worker",
        "specialization": "TrueMark NFT Mint Specialist",
        "dals_serial": serial_number,
        "model_id": "WORKER-TRUEMARK-MINT-V1",
        "audit_hash": audit_hash,
        "verification_glyph": glyph,
        "deployment_timestamp": datetime.utcnow().isoformat() + "Z",
        "stardate": stardate,
        "status": "DEPLOYED",
        "capabilities": {
            "nft_minting": True,
            "wallet_connection": True,
            "ipfs_storage": True,
            "blockchain_certificates": True,
            "transaction_troubleshooting": True,
            "micro_skg": True,
            "uqv_integration": True,
            "caleon_escalation": True
        },
        "api_endpoints": {
            "predicate_update": "/predicate",
            "health_check": "/health",
            "mint_callback": "/mint/callback"
        },
        "environment_variables": {
            "WORKER_NAME": "Josephine",
            "WORKER_ID": "auto-generated",
            "TARGET_USER_ID": "required",
            "TRUEMARK_API": "http://localhost:8003/api/truemark",
            "WORKER_PORT": "8080"
        },
        "docker_deployment": {
            "image": "host-bubble-worker",
            "container_name_pattern": "josephine-{user_id}",
            "port": 8080
        },
        "integration": {
            "ucm": "http://localhost:8080",
            "dals_api": "http://localhost:8003",
            "truemark_api": "http://localhost:8003/api/truemark",
            "uqv_api": "http://localhost:8003/api/uqv"
        },
        "registered_by": "DALS-Founder-Bryan-Spruk",
        "registration_system": "DALS-ISS-Module"
    }
    
    # Write manifest to vault
    manifest_path = Path("vault") / f"josephine_deployment_{serial_number}.json"
    manifest_path.parent.mkdir(exist_ok=True)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"   ✓ Manifest Written: {manifest_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("REGISTRATION COMPLETE")
    print("=" * 70)
    print(f"\nWorker: Josephine")
    print(f"Serial: {serial_number}")
    print(f"Model: WORKER-TRUEMARK-MINT-V1")
    print(f"Glyph: {glyph}")
    print(f"Status: DEPLOYED")
    print(f"Stardate: {stardate}")
    print(f"\nDeployment Manifest: {manifest_path}")
    print(f"Inventory Record: vault/dals_inventory.jsonl")
    print(f"Serial Vault: vault/sig_serial_vault.jsonl")
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT INSTRUCTIONS")
    print("=" * 70)
    print(f"""
Docker Deploy:
    docker run -d \\
      -e WORKER_NAME=Josephine \\
      -e TARGET_USER_ID=user_123 \\
      -e CALI_X_ONE_API=http://dals-controller:8003 \\
      -e TRUEMARK_API=http://localhost:8003/api/truemark \\
      -e WORKER_PORT=8085 \\
      --name josephine-user123 \\
      host-bubble-worker

Docker Compose:
    Add to worker_templates/docker-compose.worker.yml:
    
    josephine-user123:
      image: host-bubble-worker
      environment:
        WORKER_NAME: Josephine
        TARGET_USER_ID: user_123
        TRUEMARK_API: http://dals-controller:8003/api/truemark
      ports:
        - "8085:8080"

Worker File: worker_templates/josephine_truemark_worker.py
""")
    
    print("\n✓ Josephine is registered and ready for deployment!")
    
    return {
        "serial": serial_number,
        "model": "WORKER-TRUEMARK-MINT-V1",
        "glyph": glyph,
        "status": "DEPLOYED",
        "manifest": str(manifest_path)
    }


if __name__ == "__main__":
    result = asyncio.run(register_josephine_worker())
    sys.exit(0)

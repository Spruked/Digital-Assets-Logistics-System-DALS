#!/usr/bin/env python3
"""
forged.py
DALS FORGE — One command to birth any specialist forever

Usage:
    python forged.py nft_mint       # Birth NFT mint specialist
    python forged.py greeting       # Birth greeting specialist
    python forged.py podcast_cohost # Birth podcast specialist
    
The worker will:
- Auto-register with DALS
- Get eternal DSN (DMN-GN-02-XXXXXXXX-XXXXX)
- Begin heartbeat cycle
- Join cognitive flywheel
"""

import subprocess
import sys
import uuid

def forge_worker(role: str):
    """Forge a new specialist worker with one command"""
    
    worker_id = uuid.uuid4().hex[:8].upper()
    container_name = f"worker-{role.lower()}-{worker_id}"
    
    print(f"🔥 Forging {role} specialist...")
    print(f"   Container: {container_name}")
    
    # Build and run worker container
    result = subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "-e", f"JOB_ROLE={role}",
        "-e", "WORKER_TYPE=unified_specialist",
        "-e", "REGISTRY_URL=http://dals:8003",
        "-e", "UCM_URL=http://cali-x-one:8000",
        "-e", "CALEON_URL=http://dals:8003",
        "--network", "dals_internal",
        "-p", "8080",  # Random host port
        "dals-worker:v5"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Worker forged: {role} specialist is now alive.")
        print(f"   Container ID: {result.stdout.strip()[:12]}")
        print(f"   Check status: docker logs {container_name}")
    else:
        print(f"❌ Forge failed: {result.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python forged.py <role>")
        print()
        print("Available roles:")
        print("  nft_mint       - NFT minting specialist")
        print("  greeting       - Greeting specialist")
        print("  timeline       - Timeline building specialist")
        print("  podcast_cohost - Podcast co-host specialist")
        print("  custom_role    - Any custom role name")
        sys.exit(1)
    
    role = sys.argv[1]
    forge_worker(role)

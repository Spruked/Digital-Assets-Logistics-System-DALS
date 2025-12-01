# DALS Worker-Cloning Engine (FORGE-01) v2.0

The heart of the DALS system - creates every worker for the rest of your life.

## Overview

This module provides a complete worker cloning and deployment system that:

- Generates unique serial numbers, model numbers, and ledger codes
- Creates cryptographic keypairs for each worker
- Injects identity and configuration data
- Registers workers in the DALS database
- Builds and launches Docker containers
- Uses staging for atomic operations
- Includes manifest hashing and versioning
- Supports dry-run mode
- Collision-proof port allocation
- Idempotent worker creation

## Architecture

- `forge_engine.py`: Main orchestration engine
- `allocators/`: Serial, model, ledger, and port allocation
- `injectors/`: JSON configuration injection (identity, config, manifest)
- `docker/`: Docker container building and launching
- `registry/`: DALS database registration
- `keygen/`: Cryptographic key generation
- `blueprints/`: Template blueprints for workers
- `utils/`: Hashing, idempotency, and logging utilities

## Usage

```python
from worker_forge.forge_engine import forge_worker

# Create a new worker
entry = forge_worker(
    worker_name="Nora",
    worker_type="ledger",
    class_code="300.100.000",
    template_name="Worker_Template",
    dals_db={"workers": []}
)

print(f"Worker created: {entry}")
```

## Dry Run

```python
manifest = forge_worker(
    worker_name="TestWorker",
    worker_type="ledger",
    class_code="300.100.000",
    dry_run=True
)
print(f"Would create: {manifest}")
```

## Template Structure

The Worker_Template contains:
- `identity.json`: Worker identity information
- `config.json`: Runtime configuration
- `worker.py`: Main worker application
- `Dockerfile`: Container build instructions
- `requirements.txt`: Python dependencies
- `certs/`: Directory for cryptographic keys
- `worker_manifest.json`: Generated manifest with hashes and metadata

## Security

Each worker gets its own Ed25519 keypair for secure communication and authentication.

## Versioning

Current version: 2.0 (see version.txt)
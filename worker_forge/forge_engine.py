import os
import shutil
import uuid
import tempfile
import datetime
import json

from workers.templates.worker_template import WorkerTemplate
from workers.registry import get_worker_template, REGISTERED_WORKER_TYPES

from worker_forge.allocators.serials import generate_serial
from worker_forge.allocators.ports import allocate_port
from worker_forge.allocators.model_numbers import generate_model
from worker_forge.allocators.ledger_codes import assign_ledger_code

from worker_forge.injectors.identity_injector import inject_identity
from worker_forge.injectors.config_injector import inject_config
from worker_forge.injectors.personality_injector import inject_personality

from worker_forge.keygen.keygen import generate_worker_keys
from worker_forge.registry.registrar import register_worker

from worker_forge.docker.docker_builder import build_and_launch_worker
from worker_forge.utils.hashing import hash_directory
from worker_forge.utils.idempotency import ensure_unique_worker
from worker_forge.utils.logging import logger


def _select_personality_template(worker_type: str) -> str:
    """
    Select appropriate personality template based on worker type.
    Maps worker types to their corresponding personality templates.
    """
    personality_map = {
        "ledger": "Ledger_Mind_v1",
        "archival": "Archival_Mind_v1",
        "mechanist": "Mechanist_Mind_v1",
        "nora": "Ledger_Mind_v1",
        "elara": "Archival_Mind_v1",
        "vektor": "Mechanist_Mind_v1"
    }

    # Default to base template if no specific mapping
    return personality_map.get(worker_type.lower(), "Worker_Template_v1")


def forge_worker(
    worker_name: str,
    worker_type: str,
    class_code: str,
    template_name="Worker_Template",
    dals_db=None,
    dry_run=False
):
    logger.info(f"forge.start: worker_name={worker_name}, worker_type={worker_type}")

    # Validate worker type is registered
    if worker_type not in REGISTERED_WORKER_TYPES:
        raise ValueError(f"Worker type '{worker_type}' is not registered. Available types: {list(REGISTERED_WORKER_TYPES.keys())}")

    # 1: Generate Worker Identity Values -------------------------------------
    serial = generate_serial(worker_type)
    model = generate_model(class_code)
    ledger = assign_ledger_code(class_code)
    port = allocate_port(dals_db)

    # 2: Generate Vault Integration Values ----------------------------------
    glyph_trace = f"{worker_type.upper()}-{serial}-{uuid.uuid4().hex[:8]}"
    accountability_vault = {}
    reflection_vault = {}
    ap_helix_ref = f"AP-{serial}-{datetime.datetime.utcnow().strftime('%Y%m%d')}"

    # 3: Create Worker Configuration ----------------------------------------
    worker_config = {
        "worker_serial": serial,
        "model_id": model,
        "glyph_trace": glyph_trace,
        "accountability_vault": accountability_vault,
        "reflection_vault": reflection_vault,
        "ap_helix_ref": ap_helix_ref,
        "ucm_plugin_pipe": f"ucm-pipe-{serial}",
        "worker_name": worker_name,
        "worker_type": worker_type,
        "class_code": class_code,
        "ledger_code": ledger,
        "port": port,
        "wedg_home": worker_type.upper(),
        "dals_registry_endpoint": "http://dals.local:9000/api/v1/registry/heartbeat",
        "ucm_host": "http://ucm.local:8000",
        "heartbeat_interval": 30
    }

    # 4: Instantiate Worker Template ----------------------------------------
    worker_template_class = get_worker_template(worker_type)
    worker_template = worker_template_class(worker_config)

    # 5: Generate Keys for Envelope Verification ----------------------------
    private_key, public_key = generate_worker_keys()

    # 6: Create Worker Directory Structure ----------------------------------
    final_path = os.path.join(os.path.dirname(__file__), f"../workers/{worker_name}")
    ensure_unique_worker(final_path)

    if not dry_run:
        os.makedirs(final_path, exist_ok=True)
        os.makedirs(f"{final_path}/certs", exist_ok=True)
        os.makedirs(f"{final_path}/vault", exist_ok=True)

        # Save keys
        with open(f"{final_path}/certs/worker_private.key", "wb") as f:
            f.write(private_key)
        with open(f"{final_path}/certs/worker_public.pem", "wb") as f:
            f.write(public_key)

        # Save configuration
        with open(f"{final_path}/config.json", "w") as f:
            json.dump(worker_config, f, indent=4)

        # Save identity
        identity_data = {
            "worker_name": worker_name,
            "worker_type": worker_type,
            "class_code": class_code,
            "ledger_code": ledger,
            "model_number": model,
            "serial_number": serial,
            "glyph_trace": glyph_trace,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
        with open(f"{final_path}/identity.json", "w") as f:
            json.dump(identity_data, f, indent=4)

    # 7: Inject Personality System -----------------------------------------
    personality_template = _select_personality_template(worker_type)

    # 8: Create Worker Manifest ---------------------------------------------
    manifest = {
        "forge_version": "2.0.0",  # Updated for template-based forging
        "forged_at": datetime.datetime.utcnow().isoformat(),
        "template_used": worker_template_class.__name__,
        "template_class": f"{worker_template_class.__module__}.{worker_template_class.__name__}",
        "personality_template": personality_template,
        "worker_serial": serial,
        "worker_model": model,
        "ledger_code": ledger,
        "class_code": class_code,
        "port": port,
        "glyph_trace": glyph_trace,
        "vault_integrity": worker_template._check_vault_integrity()
    }

    if not dry_run:
        with open(f"{final_path}/worker_manifest.json", "w") as f:
            json.dump(manifest, f, indent=4)

    if dry_run:
        logger.info(f"forge.dry_run: serial={serial}, model={model}, port={port}")
        return manifest

    # 9: Register Worker ---------------------------------------------------
    if dals_db is not None:
        entry = register_worker(
            dals_db, serial, model, ledger, class_code, port
        )
    else:
        # Create entry for return when no database is provided
        entry = {
            "serial": serial,
            "model": model,
            "ledger_code": ledger,
            "class_code": class_code,
            "port": port
        }

    # 10: Launch Worker Process -------------------------------------------
    # Note: In production, this would start the FastAPI server
    # For now, we'll just log the successful creation
    logger.info(f"forge.complete: serial={serial}, port={port}, template=WorkerTemplate")

    return entry
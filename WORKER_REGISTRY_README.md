# DALS Worker Registry System

The DALS Worker Registry system provides a unified way to manage and instantiate different types of DALS workers using template-based architecture.

## Overview

The worker registry maps worker types to their corresponding template classes, enabling DALS to:

- **Recognize worker types**: DALS can now identify and manage different worker categories
- **Unified instantiation**: All workers use the same WorkerTemplate base with type-specific configuration
- **Vault integration**: Every worker gets proper vault injection (accountability, reflection, glyph trace)
- **Registry management**: Easy addition of new worker types without code changes

## Architecture

```
Worker Registry
├── workers/registry.py - Type-to-class mapping
├── workers/templates/worker_template.py - Base template class
├── worker_forge/forge_engine.py - Registry-integrated forging
└── forge_worker_cli.py - Command-line interface
```

## Available Worker Types

The following worker types are currently registered:

- **template**: Base WorkerTemplate (for testing/development)
- **goat**: GOAT (Generative Operational AI Template) workers
- **mint**: Asset minting and certification workers
- **finance**: Financial transaction and ledger workers
- **ucm_relay**: UCM (Unified Cognition Module) relay workers
- **obs**: OBS (Open Broadcasting Software) control workers
- **telemetry**: System monitoring and telemetry workers
- **ledger**: Distributed ledger management workers
- **archival**: Data archival and backup workers
- **mechanist**: Automation and orchestration workers

## Usage

### Command Line Interface

```bash
# List available worker types
python forge_worker_cli.py --list-types

# Forge a worker (dry run)
python forge_worker_cli.py --type goat --name my-goat-worker --class-code A1 --dry-run

# Forge a worker (create files)
python forge_worker_cli.py --type mint --name mint-worker --class-code B2
```

### Programmatic Usage

```python
from worker_forge.forge_engine import forge_worker
from workers.registry import get_worker_template, list_registered_types

# List all registered types
types = list_registered_types()
print(f"Available types: {types}")

# Get template class for a specific type
template_class = get_worker_template('goat')
print(f"Goat template: {template_class}")

# Forge a worker
result = forge_worker(
    worker_name='my-worker',
    worker_type='goat',
    class_code='A1',
    dry_run=True
)
print(f"Worker serial: {result['worker_serial']}")
```

## Adding New Worker Types

To add a new worker type to the registry:

1. **Create the template class** (if needed):
   ```python
   from workers.templates.worker_template import WorkerTemplate

   class MyCustomWorker(WorkerTemplate):
       def __init__(self, config):
           super().__init__(config)
           # Custom initialization
   ```

2. **Register the type** in `workers/registry.py`:
   ```python
   REGISTERED_WORKER_TYPES = {
       # ... existing types ...
       "my_custom": MyCustomWorker,
   }
   ```

3. **Test the registration**:
   ```bash
   python forge_worker_cli.py --type my_custom --name test-worker --class-code X1 --dry-run
   ```

## Worker Template Features

All workers inherit from `WorkerTemplate` which provides:

- **Vault Integration**: Accountability vault, reflection vault, glyph trace
- **Envelope Verification**: NaCl-based cryptographic verification
- **Heartbeat System**: Async heartbeat loop for monitoring
- **FastAPI App**: Built-in web server with health endpoints
- **Task Processing**: Async task execution framework

### Key Methods

- `_check_vault_integrity()`: Validates vault data integrity
- `_verify_envelope()`: Cryptographically verifies incoming envelopes
- `start_heartbeat_loop()`: Begins async heartbeat monitoring
- `process_task()`: Handles incoming tasks (override in subclasses)

## Testing

Run the comprehensive test suite:

```bash
python test_worker_registry.py
```

This tests:
- Registry configuration
- Template instantiation
- Forge engine integration
- Worker type validation

## Integration with DALS Dashboard

Workers forged with this system will automatically appear in the DALS dashboard under the "Workers" tab, showing:

- Worker status and health
- Vault integrity status
- Heartbeat monitoring
- Task processing metrics

## File Structure

```
workers/
├── registry.py                 # Worker type registry
├── templates/
│   └── worker_template.py     # Base WorkerTemplate class
└── instances/                 # Forged worker storage
    ├── worker_{serial}.json   # Worker instance data
    └── ...

worker_forge/
├── forge_engine.py            # Registry-integrated forge engine
└── ...

forge_worker_cli.py            # Command-line interface
test_worker_registry.py        # Test suite
```

## Security Considerations

- All workers use cryptographic envelope verification
- Vault data is integrity-checked on instantiation
- Worker communications go through CALEON security layer
- Heartbeat monitoring detects worker failures

## Troubleshooting

### Worker Type Not Recognized
```
Error: Worker type 'xyz' is not registered
```
**Solution**: Check `workers/registry.py` and ensure the type is in `REGISTERED_WORKER_TYPES`

### Template Import Error
```
ImportError: No module named 'workers.templates.worker_template'
```
**Solution**: Ensure the `workers/` directory is in Python path and files exist

### Vault Integrity Failure
```
vault_integrity=False
```
**Solution**: Check that vault configuration is properly injected during forging

## Future Enhancements

- **Dynamic registration**: API endpoints for runtime worker type registration
- **Worker clustering**: Support for worker pools and load balancing
- **Template versioning**: Version management for worker templates
- **Advanced monitoring**: Enhanced telemetry and performance metrics
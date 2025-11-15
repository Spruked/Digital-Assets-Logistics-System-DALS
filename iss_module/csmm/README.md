# Caleon Self-Maintenance Module (CSMM)

The Caleon Self-Maintenance Module (CSMM) is a comprehensive autonomous system diagnosis, repair, and learning microservice for the Digital Asset Logistics System (DALS).

## Overview

CSMM provides autonomous capabilities for:

- **Continuous System Monitoring**: Real-time health assessment of all DALS components
- **Automatic Failure Diagnosis**: Intelligent detection and classification of system issues
- **Self-Repair Operations**: Automated repair actions including service restarts and configuration fixes
- **Learning from Experience**: Pattern recognition and optimization of repair strategies
- **Caleon Security Integration**: All operations validated through the Caleon security layer

## Architecture

```
CSMM FastAPI Service (Port 8009)
├── CSMM Engine (Core orchestrator)
├── Diagnostic Engine (Health monitoring & issue detection)
├── Repair Engine (Automated repair execution)
├── Learning Engine (Pattern analysis & optimization)
└── Configuration System (Environment-based settings)
```

## Key Components

### 1. CSMM Engine (`core/csmm_engine.py`)
Main orchestrator that coordinates all CSMM operations with continuous monitoring and emergency controls.

### 2. Diagnostic Engine (`diagnostics/diagnostic_engine.py`)
Performs comprehensive health checks on:
- DALS API (port 8003)
- UCM Service (port 8080)
- Caleon Security Layer
- Database connections
- Telemetry systems
- Inventory services

### 3. Repair Engine (`repair/repair_engine.py`)
Executes automated repair actions:
- Service restarts
- Connection reinitialization
- Configuration fixes
- Chain reaction repairs

### 4. Learning Engine (`learning/learning_engine.py`)
Analyzes repair patterns to:
- Identify recurring issues
- Predict potential failures
- Optimize repair strategies
- Generate proactive maintenance recommendations

## API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /status` - Comprehensive CSMM status

### Diagnostics
- `POST /diagnostics/run` - Run system diagnostics
- `GET /diagnostics/history` - Get diagnostic history

### Repairs
- `POST /repairs/execute` - Execute repair action
- `GET /repairs/status/{repair_id}` - Get repair status
- `DELETE /repairs/{repair_id}` - Cancel repair
- `GET /repairs/history` - Get repair history

### Learning & Insights
- `GET /learning/insights` - Get learning insights
- `GET /learning/health/{component}` - Get component health score
- `GET /learning/predictions/{component}` - Get failure predictions
- `GET /learning/export` - Export learning data
- `POST /learning/import` - Import learning data

### Issues
- `GET /issues/active` - Get active issues
- `GET /issues/critical` - Get critical issues

## Configuration

CSMM uses environment variables for configuration:

```bash
# Service Configuration
CSMM_HOST=0.0.0.0
CSMM_PORT=8009
CSMM_LOG_LEVEL=INFO

# Engine Settings
CSMM_DIAGNOSTIC_INTERVAL=300          # 5 minutes
CSMM_MAX_CONCURRENT_REPAIRS=3
CSMM_LEARNING_ENABLED=true

# Component Endpoints
DALS_API_ENDPOINT=http://localhost:8003
UCM_ENDPOINT=http://localhost:8080
DATABASE_URL=postgresql://...
```

## Running CSMM

### As a Service
```bash
# Run the FastAPI service
python -m iss_module.csmm.csmm_service

# Or directly with uvicorn
uvicorn iss_module.csmm.csmm_api:app --host 0.0.0.0 --port 8009
```

### Integration with DALS
CSMM integrates with existing DALS services:

```python
from iss_module.csmm import CSMMEngine

# Initialize and start CSMM
csmm = CSMMEngine()
await csmm.start()

# Run diagnostics
result = await csmm.diagnose_and_repair()

# Get status
status = await csmm.get_status()
```

## Security Integration

All CSMM operations are validated through the Caleon security layer:

- **Ethical Validation**: All repair actions checked for ethical compliance
- **Tamper Detection**: Continuous monitoring for unauthorized modifications
- **Founder Override**: Emergency bypass capability for critical situations
- **Drift Monitoring**: Detection of configuration drift from baseline

## DALS-001 Compliance

CSMM follows DALS-001 governance protocol:

- **Zero-or-Empty Policy**: Returns real data or zeros/None (never mock data)
- **Real-time Accuracy**: All metrics reflect actual system state
- **UI Formatting**: Frontend handles display of null values as "Never"

## Learning & Adaptation

CSMM continuously learns from repair operations:

- **Pattern Recognition**: Identifies recurring failure modes
- **Success Rate Tracking**: Monitors effectiveness of repair strategies
- **Predictive Maintenance**: Anticipates potential failures
- **Optimization**: Improves repair success rates over time

## Monitoring & Alerts

CSMM provides comprehensive monitoring:

- **Health Scores**: Component-level health assessment (0-100)
- **Risk Levels**: Low/Medium/High risk categorization
- **Active Issues**: Real-time issue tracking
- **Repair History**: Complete audit trail of repair operations

## Emergency Controls

- **Emergency Shutdown**: Founder override for critical situations
- **Repair Cancellation**: Ability to stop active repair operations
- **Manual Intervention**: API endpoints for human-directed repairs

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `iss_module.core` - DALS core utilities
- `iss_module.core.caleon_security_layer` - Security validation

## Development

### Testing
```bash
# Run CSMM tests
python -m pytest iss_module/csmm/tests/

# Integration testing
python test_csmm_integration.py
```

### Adding New Repair Actions

1. Add repair method to `RepairEngine`
2. Update action mapping in `__init__`
3. Add configuration if needed
4. Test with diagnostics

### Extending Diagnostics

1. Add component check to `DiagnosticEngine`
2. Update health assessment logic
3. Add component configuration
4. Test health scoring

## Troubleshooting

### Common Issues

1. **Security Blocks**: Check Caleon security layer configuration
2. **Connection Failures**: Verify component endpoints in configuration
3. **Import Errors**: Ensure all DALS modules are available
4. **Permission Issues**: Check file system permissions for logs/data

### Logs

CSMM logs are integrated with DALS logging:

```
DALS.CSMM.Engine - Core engine operations
DALS.CSMM.Diagnostic - Diagnostic operations
DALS.CSMM.Repair - Repair executions
DALS.CSMM.Learning - Learning analysis
```

### Debug Mode

Enable debug logging:
```bash
CSMM_LOG_LEVEL=DEBUG
```

## Future Enhancements

- **Predictive Maintenance**: ML-based failure prediction
- **Automated Scaling**: Dynamic resource allocation
- **Multi-region Support**: Distributed CSMM instances
- **Advanced Learning**: Neural network optimization
- **Integration APIs**: Third-party tool integration

## Contributing

Follow DALS development standards:

1. **DALS-001 Compliance**: Never return mock data
2. **Security First**: All operations through Caleon validation
3. **Comprehensive Testing**: Unit and integration tests required
4. **Documentation**: Update this README for API changes
5. **Logging**: Structured logging with correlation IDs

## License

Part of the Digital Asset Logistics System (DALS) - Sovereign AI Architecture
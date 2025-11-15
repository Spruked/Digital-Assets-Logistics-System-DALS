# DALS AI Coding Agent Instructions

## Architecture Overview

DALS (Digital Asset Logistics System) is a **sovereign AI architecture** with UCM as the cognitive brain:

```
Founder (Bryan Spruk) - Ultimate Authority
    ↓
UCM (Unified Cognition Module) - Cognitive Brain & Decision Engine (port 8080)
    ↓
CALEON Security Layer - Ethical Validation & Consent Gates
    ↓
DALS Core - ISS Module (port 8003 API, 8008 Dashboard)
```

### Key Components

- **ISS Module** (`iss_module/`): Core orchestrator providing time anchoring, asset tracking, and logging
- **UCM (Unified Cognition Module)**: Cognitive brain providing AI reasoning, decision making, and thought processing
- **CALEON Security Layer** (`iss_module/core/caleon_security_layer.py`): Ethical validation and consent gates with drift monitoring, tamper seals, honeypot mode, and founder override
- **UCM Connector** (`iss_module/integrations/ucm_connector.py`): Async HTTP bridge to UCM cognitive engine
- **API Layer** (`iss_module/api/`): FastAPI routers with modular integration (telemetry, CALEON, UCM)
- **Dashboard** (`iss_module/templates/dashboard.html`): 9-tab interface with real-time security monitoring and Thought Trace UI

### Service Boundaries

- **UCM runs independently** on port 8080 - cognitive brain and decision engine
- **DALS API** on port 8003 (canonical ISS API endpoint)
- **Dashboard Server** on port 8008
- All UCM operations route through CALEON security validation
- UCM has full control over DALS except human escalation from Harmonizer
- Founder override bypasses all AI layers for emergency control

## Critical Governance Protocol: DALS-001

**Zero-Or-Empty Protocol** - The most important rule in this codebase:

### Rules
1. **NO mock data** - Ever. No simulated metrics, no placeholder numbers
2. **Inactive modules return ZERO** - Never fake activity for inactive services
3. **Use `None` or empty strings** - Not "Never", "N/A", or "--" from backend
4. **UI handles display** - JavaScript converts `null` to "Never" in frontend only

### Implementation Pattern
```python
# ✅ CORRECT - DALS-001 Compliant
def get_status() -> Dict[str, Any]:
    """Get module status - DALS-001 compliant"""
    if not module_active:
        return {
            "status": "inactive",
            "metric_count": 0,
            "last_check": None  # UI will display "Never"
        }
    return actual_live_data()

# ❌ WRONG - Violates DALS-001
def get_status() -> Dict[str, Any]:
    return {
        "status": "active",
        "metric_count": 1234,  # Fake number!
        "last_check": "Never"  # Backend shouldn't use display text
    }
```

### Documentation Requirements
- Add `# DALS-001 compliant` comment to status methods
- Include docstring: `"""Get X status - DALS-001 compliant (real data or zeros)"""`
- Reference `vault/DALS-001-governance-enforcement.md` for full specification

## Canonical Stardate System

DALS uses **Y2K epoch (January 1, 2000)** for all time anchoring:

```python
from iss_module.core.utils import get_stardate, current_timecodes

# Get canonical stardate (always positive decimal)
stardate = get_stardate()  # Example: 9410.0762

# Get full timecode bundle
timecodes = current_timecodes()
# Returns: stardate, iso_timestamp, julian_date, iss_timestamp, anchor_hash
```

- Formula: `(now - Y2K_epoch).total_seconds() / 86400`
- Always 4 decimal places
- Used for logging, event tracking, asset metadata
- Import from `iss_module.core.utils`, NOT inline calculation

## Development Workflows

### Running Services Locally

```bash
# API Server (port 8003)
python -m iss_module.api.api

# Dashboard Server (port 8008)
python dashboard_server.py

# Full stack with Docker
docker-compose up -d

# Check UCM connectivity
curl http://localhost:8080/health
```

### Testing

```bash
# Integration tests
python test_integration.py

# ISS endpoint validation
python test_iss_endpoint.py

# Verify DALS-001 compliance
python -c "from iss_module.api.api import app; print('API loads - DALS-001 enforced')"
```

### Adding New API Endpoints

1. Create router in `iss_module/api/` (e.g., `new_feature_api.py`)
2. Define Pydantic models for requests/responses
3. Import router in `api.py` with try/except and availability flag:
   ```python
   try:
       from .new_feature_api import new_feature_router
       NEW_FEATURE_AVAILABLE = True
   except ImportError as e:
       logger.warning(f"New feature not available: {e}")
       NEW_FEATURE_AVAILABLE = False
   ```
4. Include router conditionally:
   ```python
   if NEW_FEATURE_AVAILABLE:
       app.include_router(new_feature_router)
       logger.info("New Feature API enabled")
   ```
5. All status endpoints **MUST** return real data or zeros (DALS-001)

## FastAPI Patterns

### Router Structure
- Use `APIRouter` with prefix and tags
- All async functions: `async def endpoint_name()`
- Pydantic models for validation: `class RequestModel(BaseModel)`
- Error handling: `raise HTTPException(status_code=X, detail="message")`

### Security Layer Integration
```python
from ..core.caleon_security_layer import CaleonSecurityLayer

security_layer = CaleonSecurityLayer()

@router.post("/secure-operation")
async def secure_operation(data: RequestModel):
    # All operations go through CALEON validation
    result = await security_layer.validate_and_execute(data)
    return result
```

### UCM Integration Pattern
```python
from ..integrations.ucm_connector import get_ucm_connector

ucm = get_ucm_connector(ucm_host="localhost", ucm_port=8080)
await ucm.connect()
response = await ucm.submit_reasoning_request(
    content="Query text",
    priority="normal"
)
```

## Logging Conventions

Use structured logging with correlation IDs:

```python
import logging
logger = logging.getLogger("DALS.Module.Component")

# Log with context
logger.info("Operation completed", extra={
    "correlation_id": request_id,
    "user_id": user_id,
    "operation": "asset_create"
})

# Security events (ALWAYS async)
await security_layer._log_security_event(
    ThreatType.UNAUTHORIZED_ACCESS,
    SecurityLevel.HIGH,
    "Security event description",
    {"additional": "context"}
)
```

## Dashboard Integration

JavaScript in `dashboard.html` follows these patterns:

### Fetching Status with DALS-001 Compliance
```javascript
async function fetchStatus() {
    const response = await fetch('/api/endpoint/status');
    const data = await response.json();
    
    // Handle null from backend (don't trust fake data)
    document.getElementById('timestamp').textContent = 
        data.last_check || 'Never';  // UI displays "Never", not backend
    document.getElementById('count').textContent = 
        data.count || '0';  // Always show zero if inactive
}
```

### Tab Navigation
- 9 tabs: Overview, CertSig, AI & UCM, Security, Telemetry, System, Web3, Business, Ops
- Tab switching uses localStorage persistence
- Active tab class: `tab-button active`

## Docker & Deployment

### Docker Compose Services
- `dals-controller`: Main DALS API (port 8003 canonical)
- `redis`: Caching and sessions (port 6379)
- `consul`: Service discovery (port 8500)
- UCM runs separately (not in docker-compose yet - coming soon)

### Environment Variables
```bash
ISS_SERVICE_NAME=dals-controller
ISS_HOST=0.0.0.0
ISS_PORT=8003
ENVIRONMENT=production
LOG_LEVEL=INFO
DALS_001_ENFORCED=true
```

## Common Pitfalls

1. **Don't return mock data** - Violates DALS-001, breaks user trust
2. **Don't use inline stardate calculations** - Import from `iss_module.core.utils`
3. **Don't forget async/await** - Security layer methods are ALL async
4. **Don't skip CALEON validation** - UCM commands MUST go through security gateway
5. **Don't hardcode ports** - Use environment variables (`settings.iss_port`)
6. **Don't mix display logic in backend** - Return `None`, let UI handle "Never"

## File Organization

```
iss_module/
├── core/               # Core logic: ISS, utils, security layer, validators
├── api/                # FastAPI routers: api.py (main), caleon_api, ucm_api, telemetry
├── integrations/       # External service connectors: ucm_connector
├── inventory/          # Asset tracking: inventory_manager, exporters
├── templates/          # HTML templates: dashboard.html, login.html
├── static/             # Frontend assets: icons, images, CSS, JS
├── data/               # Runtime data: logs, exports
└── models.py           # Pydantic schemas
```

## Key Files

- `iss_module/api/api.py`: Main FastAPI app with router inclusion
- `iss_module/core/caleon_security_layer.py`: Security gateway (1166 lines)
- `iss_module/integrations/ucm_connector.py`: UCM bridge (380 lines)
- `iss_module/templates/dashboard.html`: Full dashboard UI (4440 lines)
- `vault/DALS-001-governance-enforcement.md`: Governance specification
- `docker-compose.yml`: Production deployment configuration

## When to Ask

- Unclear about DALS-001 compliance in a specific scenario
- Need clarification on UCM vs CALEON responsibilities
- Founder override implementation details
- Integration with new external AI services
- Stardate calculation edge cases

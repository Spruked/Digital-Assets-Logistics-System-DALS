# DALS API Reference

This document provides comprehensive reference documentation for the Digital Asset Logistics System (DALS) API endpoints.

## 🛡️ Governance Compliance

All API endpoints comply with **DALS-001 "Zero-Or-Empty" governance protocol**:
- No mock or placeholder data
- Honest status reporting for inactive modules
- Live data only operation

## 🌟 Canonical Stardate System

DALS uses a canonical stardate system with Y2K epoch (January 1, 2000):
- **Formula**: `(current_time - Y2K_epoch).total_seconds() / 86400`
- **Format**: Decimal days with 4-decimal precision
- **Example**: `9410.0762`

## 📡 Endpoints

### Core System Endpoints

#### GET `/health`
Service health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-05T14:30:15Z"
}
```

#### GET `/api/v1/iss/now`
Returns current canonical stardate and system status.

**Response:**
```json
{
  "stardate": 9410.0762,
  "iso_timestamp": "2025-10-05T14:30:15Z",
  "system_status": "operational",
  "governance": "DALS-001 compliant"
}
```

### Module Status Endpoints

#### GET `/api/v1/caleon/status`
Caleon AI module status (DALS-001 compliant).

**Response (when inactive):**
```json
{
  "active": false,
  "cognitive_load": 0,
  "reasoning_patterns": 0,
  "status": "offline"
}
```

#### GET `/api/v1/certsig/status`
CertSig blockchain module status (DALS-001 compliant).

**Response (when inactive):**
```json
{
  "active": false,
  "signatures_processed": 0,
  "blockchain_height": 0,
  "status": "offline"
}
```

#### GET `/api/harmonizer/status`
Gyro-Cortical Harmonizer status - Final verdict engine (DALS-001 compliant).

**Response (when inactive):**
```json
{
  "status": "inactive",
  "active_cycles": 0,
  "last_convergence": null,
  "current_verdict_confidence": 0.0,
  "stability_threshold": 3.0,
  "philosophical_guides_used": 0
}
```

**Response (when active):**
```json
{
  "status": "active",
  "active_cycles": 5,
  "last_convergence": "9445.123456",
  "current_verdict_confidence": 0.87,
  "stability_threshold": 3.0,
  "philosophical_guides_used": 3
}
```

#### POST `/api/harmonizer/reason`
Process reasoning request through Gyro-Cortical Harmonizer.

**Request:**
```json
{
  "logic_packets": [
    {
      "packet_type": "helices",
      "content": {"patterns": ["pattern1", "pattern2"]},
      "confidence": 0.85,
      "source_module": "pattern_analyzer"
    }
  ],
  "context": {"request_id": "req_123"}
}
```

**Response:**
```json
{
  "verdict": {
    "confidence": 0.87,
    "risk_score": 0.23,
    "ethical_alignment": 0.91,
    "recommendations": []
  },
  "processing_time_ms": 245.67,
  "convergence_cycles": 3,
  "philosophical_guide": "categorical_imperative",
  "stability_achieved": true,
  "security_gate": {"block": false},
  "timestamp": "9445.123456"
}
```

### Data Management Endpoints

#### POST `/api/v1/vault/query`
Query captain's log entries.

**Request Body:**
```json
{
  "query": "search term",
  "category": "optional",
  "limit": 100
}
```

**Response:**
```json
{
  "entries": [],
  "total": 0,
  "stardate": 9410.0762
}
```

#### POST `/api/v1/log`
Add captain's log entry.

**Request Body:**
```json
{
  "message": "Log entry content",
  "category": "general",
  "tags": ["tag1", "tag2"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "stardate": 9410.0762,
  "status": "created"
}
```

#### GET `/api/v1/status`
Detailed service status.

**Response:**
```json
{
  "service": "dals-iss-module",
  "version": "1.0.0",
  "stardate": 9410.0762,
  "modules": {
    "iss": true,
    "caleon": false,
    "certsig": false,
    "prometheus": false
  },
  "governance": "DALS-001",
  "uptime": "24h 15m"
}
```

## 📚 Interactive Documentation

Visit `/docs` for interactive API documentation with request/response examples and testing capabilities.

## 🛡️ Error Responses

All endpoints follow consistent error response format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "stardate": 9410.0762,
  "governance": "DALS-001"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## 🔒 Authentication

Current implementation operates without authentication for development/demonstration purposes. Production deployments should implement appropriate authentication mechanisms.

## 📈 Rate Limiting

No rate limiting currently implemented. Production deployments should implement appropriate rate limiting based on use case requirements.
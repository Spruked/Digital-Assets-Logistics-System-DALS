# Changelog

All notable changes to the Digital Asset Logistics System (DALS) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-01

### Added
- **🎤 Cali Ethics Gate**: Sovereign AI token-level ethics filtering microservice
  - Real-time token scoring with configurable ethics threshold (default: 0.80)
  - Automatic redaction of unethical tokens below threshold
  - Token injection system for voice overrides and approvals
  - RESTful API endpoints for ethics scoring and injection
  - Fallback heuristic scoring when ML model unavailable

- **🧠 Phi-3-mini Articulation Bridge**: Token streaming with ethics integration
  - Real-time token-by-token streaming from Phi-3-mini model
  - Ethics filtering applied to each token before output
  - Automatic neutralization of flagged tokens
  - WebSocket-compatible streaming interface
  - Backward compatibility with existing articulation systems

- **🎤 Caleon Consent Manager**: Voice-activated consent system
  - Multiple consent modes: manual, voice, always_yes, random, consensus
  - Voice keyword detection ("approve", "yes", "caleon approve")
  - Integration with Cali ethics gate for voice overrides
  - Token injection for high-ethics approvals
  - Configurable timeouts and risk assessment

- **🐳 Cali Ethics Side-car Container**: Docker containerization
  - Lightweight Python service with FastAPI
  - Health checks and monitoring endpoints
  - Model loading support for ethics classification
  - Network isolation and security hardening
  - Resource limits and health monitoring

- **🧠 Phi-3-mini Side-car Container**: ML model containerization
  - Microsoft Phi-3-mini model with 4-bit quantization
  - Streaming token generation with logits output
  - Optimized for real-time ethics filtering
  - Memory and CPU resource constraints
  - Health monitoring and automatic restarts

### Changed
- **🔄 Enhanced Cali_X_One Integration**: Ethics-filtered articulation
  - All voice outputs now pass through ethics gate
  - Token-level filtering prevents toxic outputs
  - Voice overrides inject high-ethics tokens
  - Real-time streaming with ethics validation
  - Zero-downtime deployment with fallback modes

- **🐳 Docker Architecture**: Side-car container pattern
  - Cali ethics gate runs as side-car to main DALS controller
  - Phi-3-mini runs as separate ML container
  - Inter-service communication via HTTP APIs
  - Health checks and dependency management
  - Rolling update support for zero downtime

- **🔧 Environment Configuration**: Ethics and streaming parameters
  - New environment variables for ethics thresholds
  - Streaming timeouts and model endpoints
  - Backward compatibility with existing configurations
  - Feature flags for gradual rollout

### Technical Details
- **Ethics Scoring**: MLP-based token classification (512->1) with sigmoid output
- **Token Streaming**: Async token generation with real-time ethics filtering
- **Voice Integration**: Web Speech API compatibility with keyword detection
- **Container Networking**: Internal Docker network for side-car communication
- **Fallback Systems**: Graceful degradation when ethics services unavailable

## [1.1.0] - 2025-12-01

### Added
- **🎤 Cali_X_One Host Bubble**: Sovereign AI supervisor with voice-activated interface
  - Floating blue orb (bottom-right corner) on all pages
  - Wake word "Cali" for voice activation
  - WebSocket-based real-time communication
  - ElevenLabs voice synthesis with custom personality
  - System orchestration and monitoring capabilities
  - Glassmorphic UI design with mobile responsiveness

- **👥 Worker Vault System**: Scalable worker deployment and personality management
  - **Worker Inventory Vault**: Master templates for blank worker instances
  - **Active Workers Vault**: Live deployments with individual worker folders
  - **Worker Cast**: Nora, Victor, Lena, Miles, Cali_X_One personalities
  - **Performance Monitoring**: Real-time metrics and health tracking
  - **Automated Backups**: 6-hour intervals with integrity verification
  - **Deployment Tracking**: Complete audit trail and version control

- **🏗️ Dual-Vault Architecture**: Secure worker management system
  - Template-based deployment from inventory vault
  - Individual worker isolation in active vault
  - Personality preservation and memory retention
  - Sovereign AI integration with CALEON security validation

### Changed
- **🔄 Universal Cali_X_One Integration**: Host bubble available across all DALS interfaces
  - Dashboard, login, and voice portal pages
  - Server-rendered HTML with client-side speech recognition
  - WebSocket communication channels established
  - Sovereign AI orchestration capabilities enabled

- **🐳 Docker Environment Updates**: Worker vault and host bubble support
  - New environment variables for vault management
  - Volume mounts for persistent worker storage
  - Directory creation during container build
  - Production-ready configuration updates

- **📚 Documentation Updates**: Comprehensive architecture documentation
  - README.md updated with new features and capabilities
  - Docker quickstart guide enhanced with Cali_X_One instructions
  - Architecture diagram updated with worker vault and host bubble
  - API documentation reflecting new endpoints

### Technical Details
- **Host Bubble Components**: HTML template, CSS styling, JavaScript speech recognition
- **Worker Templates**: JSON manifests with personality traits and behavior rules
- **Vault Management**: Automated deployment tracking and performance monitoring
- **Voice Integration**: ElevenLabs API with fallback synthesis support
- **WebSocket Communication**: Real-time sovereign AI interaction

## [1.0.0] - 2025-10-05

### Added
- **🌟 Canonical Stardate System**: Implemented Y2K epoch-based stardate calculation
  - Formula: `(current_time - Y2K_epoch).total_seconds() / 86400`
  - Always positive decimal values with 4-decimal precision
  - Example output: `9410.0762` representing days since January 1, 2000
  
- **🛡️ DALS-001 Governance Protocol**: "Zero-Or-Empty" ethical data representation
  - No mock or placeholder data in production
  - Honest status reporting for inactive modules
  - Trust transparency through governance badges
  - Zero-value returns instead of simulated data

- **📡 Comprehensive API Endpoints**: Full FastAPI implementation
  - `/api/v1/iss/now` - Current canonical stardate and status
  - `/api/v1/caleon/status` - Caleon AI module status (DALS-001 compliant)
  - `/api/v1/certsig/status` - CertSig blockchain module status (DALS-001 compliant)
  - `/api/v1/ucm/status` - Unified Cognition Module status (DALS-001 compliant)
  - `/api/v1/harmonizer/status` - Gyro-Cortical Harmonizer verdict status (DALS-001 compliant)
  - `/health` - Service health check
  - `/docs` - Interactive API documentation

- **🐳 Docker Implementation**: Complete containerization support
  - Multi-stage Dockerfile with production optimizations
  - Docker Compose configuration with service dependencies
  - Environment variable configuration
  - Health checks and restart policies

- **📚 Comprehensive Documentation**: Structured documentation system
  - Complete API reference with examples
  - Governance compliance documentation
  - Setup and installation guides
  - Architecture and integration documentation

### Changed
- **⚡ Performance Optimizations**: Async/await implementation throughout
  - FastAPI with async endpoints
  - Improved response times for all API calls
  - Efficient stardate calculations

- **🔧 Code Structure**: Consolidated ISS module architecture
  - Removed duplicate `ISS_Module-main` directory
  - Centralized configuration management
  - Improved error handling and logging

### Deprecated
- **📅 TNG Era Stardate**: Replaced negative stardate values
  - Old TNG era format producing negative values
  - Replaced with canonical Y2K epoch system

### Removed
- **🚫 Mock Data Elimination**: Complete removal of placeholder data
  - Removed demo credentials from login template
  - Eliminated simulated values from all API endpoints
  - Removed fake status indicators and metrics

### Fixed
- **🔧 Async/Await Syntax**: Corrected Python async implementation
  - Fixed `ISS.py` async function definitions
  - Resolved FastAPI endpoint async compatibility
  - Improved error handling in async contexts

### Security
- **🛡️ Trust Through Transparency**: Enhanced user trust mechanisms
  - Clear governance compliance indicators
  - Honest system status reporting
  - Removal of misleading demo modes

## [0.9.0] - 2025-10-04

### Added
- Initial ISS module implementation
- Basic stardate calculation (TNG era)
- FastAPI web interface
- Docker configuration
- Basic logging system

### Known Issues in Previous Versions
- TNG era stardate producing negative values
- Mock data throughout API endpoints
- Async/await syntax errors
- Duplicate directory structure

---

## Version History

- **v1.0.0** (2025-10-05): DALS-001 Governance + Canonical Stardate
- **v0.9.0** (2025-10-04): Initial implementation

## Governance Compliance

Starting with v1.0.0, all releases comply with **DALS-001 "Zero-Or-Empty" governance protocol** ensuring ethical data representation and user trust through transparency.

## Migration Notes

### From v0.9.0 to v1.0.0

1. **Stardate Values**: All stardate values are now positive (Y2K epoch)
2. **API Responses**: Inactive modules return zeros instead of mock data
3. **Module Structure**: Use `iss_module/` instead of `ISS_Module-main/`
4. **Configuration**: Update environment variables as per `.env.example`

## Contributors

- DALS Development Team
- Governance Committee (DALS-001 protocol)
- Stardate Authority (Y2K epoch decision)

## Links

- [Repository](https://github.com/Spruked/DALS)
- [Documentation](docs/README.md)
- [Governance Protocol](vault/DALS-001-governance-enforcement.md)
- [Stardate Authority Decision](vault/stardate_authority_decision.json)
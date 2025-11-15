"""
ISS Module Configuration for UCM Integration
===========================================

Configuration classes and settings management compatible with 
UCM microservices architecture.

Provides:
- Environment-based configuration
- Service discovery settings  
- Circuit breaker configuration
- Middleware settings
- Database and storage configuration
- Logging configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EnvironmentType(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ISSSettings(BaseSettings):
    """
    ISS Module settings compatible with UCM
    
    Reads configuration from environment variables with fallback defaults.
    """
    
    # Basic service configuration
    service_name: str = Field(default="iss-controller")
    version: str = Field(default="1.0.0")
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT)
    
    # Network configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8003)
    
    # Service discovery
    service_registry_url: Optional[str] = Field(default=None)
    consul_host: Optional[str] = Field(default="localhost")
    consul_port: int = Field(default=8500)
    
    # Prometheus Prime API Gateway
    api_gateway_url: str = Field(default="http://localhost:8000")
    
    # Database and storage
    data_dir: str = Field(default="./data")
    log_storage_path: str = Field(default="./data/logs")
    vault_storage_path: str = Field(default="./data/vault")
    
    # Database URL (for persistent storage)
    database_url: Optional[str] = Field(default=None)
    
    # Redis configuration (for caching and sessions)
    redis_url: Optional[str] = Field(default="redis://localhost:6379")
    redis_enabled: bool = Field(default=False)
    
    # Logging configuration
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_format: str = Field(default="json")  # json or console
    log_file: Optional[str] = Field(default=None)
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    
    # Security settings
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    access_token_expire_minutes: int = Field(default=30)
    require_auth: bool = Field(default=False)
    admin_user: str = Field(default="admin")
    admin_password_hash: str = Field(
        default="$2b$12$hMDHY6YDS.LhqCsXXE8fFuYpL6vLq1Y7jZQlGChas0nHvcsgy8.26",  # Hash for "admin123"
    )
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = Field(default=True)
    circuit_breaker_failure_threshold: int = Field(default=5)
    circuit_breaker_recovery_timeout: int = Field(default=60)
    circuit_breaker_expected_exception: str = Field(default="Exception")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)  # seconds
    
    # Monitoring and metrics
    metrics_enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    health_check_interval: int = Field(default=30)  # seconds
    
    # ISS specific settings
    stardate_offset: float = Field(default=0.0)
    default_log_category: str = Field(default="general")
    max_log_entries: int = Field(default=10000)
    log_retention_days: int = Field(default=90)
    
    # Captain's Log settings
    captain_name: str = Field(default="Captain")
    ship_name: str = Field(default="ISS Module")
    auto_backup_enabled: bool = Field(default=True)
    backup_interval_hours: int = Field(default=24)
    
    # Export settings
    export_dir: str = Field(default="./exports")
    max_export_size_mb: int = Field(default=100)
    export_formats: List[str] = Field(default=["csv", "json", "markdown"])
    
    # VisiData integration
    visidata_enabled: bool = Field(default=False)
    visidata_port: int = Field(default=8080)
    
    # UCM integration
    ucm_integration_enabled: bool = Field(default=True)
    reasoning_timeout_ms: int = Field(default=5000)
    vault_query_limit: int = Field(default=1000)
    
    # External service URLs (for UCM ecosystem)
    cochlear_processor_url: Optional[str] = Field(default=None)
    phonatory_output_url: Optional[str] = Field(default=None)
    vault_manager_url: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == EnvironmentType.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == EnvironmentType.PRODUCTION
    
    @property
    def service_url(self) -> str:
        """Get the full service URL"""
        return f"http://{self.host}:{self.port}"
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information for registration"""
        return {
            "name": self.service_name,
            "version": self.version,
            "url": self.service_url,
            "health_check": f"{self.service_url}/health",
            "environment": self.ENVIRONMENT,
            "capabilities": [
                "reasoning_processing",
                "vault_queries",
                "log_management", 
                "time_anchoring",
                "data_export"
            ]
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.database_url,
            "data_dir": self.data_dir,
            "log_storage": self.log_storage_path,
            "vault_storage": self.vault_storage_path
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.log_level,
            "format": self.log_format,
            "file": self.log_file,
            "service": self.service_name
        }
    
    def get_circuit_breaker_config(self) -> Dict[str, Any]:
        """Get circuit breaker configuration"""
        return {
            "enabled": self.circuit_breaker_enabled,
            "failure_threshold": self.circuit_breaker_failure_threshold,
            "recovery_timeout": self.circuit_breaker_recovery_timeout,
            "expected_exception": self.circuit_breaker_expected_exception
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "enabled": self.rate_limit_enabled,
            "requests": self.rate_limit_requests,
            "window": self.rate_limit_window
        }


# Create global settings instance
settings = ISSSettings()


# Configuration validation
def validate_settings():
    """Validate settings and provide warnings for production"""
    issues = []
    
    if settings.is_production:
        if settings.secret_key == "dev-secret-key-change-in-production":
            issues.append("SECRET_KEY should be changed in production")
        
        if not settings.database_url:
            issues.append("DATABASE_URL should be set in production")
        
        if settings.log_level == LogLevel.DEBUG:
            issues.append("LOG_LEVEL should not be DEBUG in production")
    
    if settings.ucm_integration_enabled:
        if not settings.api_gateway_url:
            issues.append("API_GATEWAY_URL required for UCM integration")
    
    return issues


# Environment-specific configurations
class DevelopmentConfig:
    """Development environment specific settings"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = LogLevel.DEBUG
    circuit_breaker_enabled = False
    rate_limit_enabled = False


class ProductionConfig:
    """Production environment specific settings"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = LogLevel.INFO
    circuit_breaker_enabled = True
    rate_limit_enabled = True
    REQUIRE_AUTH = True


class TestingConfig:
    """Testing environment specific settings"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = LogLevel.DEBUG
    DATABASE_URL = "sqlite:///test.db"
    circuit_breaker_enabled = False
    rate_limit_enabled = False


def get_config_for_environment(env: EnvironmentType):
    """Get configuration class for environment"""
    configs = {
        EnvironmentType.DEVELOPMENT: DevelopmentConfig,
        EnvironmentType.PRODUCTION: ProductionConfig,
        EnvironmentType.TESTING: TestingConfig,
        EnvironmentType.STAGING: ProductionConfig  # Use production config for staging
    }
    return configs.get(env, DevelopmentConfig)


# Export main settings and utilities
__all__ = [
    'ISSSettings',
    'settings',
    'EnvironmentType',
    'LogLevel',
    'validate_settings',
    'DevelopmentConfig',
    'ProductionConfig', 
    'TestingConfig',
    'get_config_for_environment'
]
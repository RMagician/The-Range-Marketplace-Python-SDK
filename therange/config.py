"""
Configuration module for The Range Marketplace SDK.

Provides configurable environment settings for production and UAT environments.
"""

from typing import Optional


class EnvironmentConfig:
    """Configuration for a specific environment."""
    
    def __init__(self, base_url: str, name: str = ""):
        """
        Initialize environment configuration.
        
        Args:
            base_url: The base URL for API endpoints
            name: Optional name for the environment (e.g., "production", "uat")
        """
        self.base_url = base_url.rstrip("/") + "/"  # Ensure consistent trailing slash
        self.name = name
    
    def __repr__(self):
        return f"EnvironmentConfig(name='{self.name}', base_url='{self.base_url}')"


class Config:
    """Main configuration class for The Range Marketplace SDK."""
    
    # Predefined environments
    PRODUCTION = EnvironmentConfig("https://supplier.rstore.com/rest", "production")
    UAT = EnvironmentConfig("https://uatsupplier.rstore.com/rest", "uat")
    
    def __init__(self, environment: Optional[EnvironmentConfig] = None):
        """
        Initialize configuration.
        
        Args:
            environment: Environment configuration to use. Defaults to PRODUCTION.
        """
        self.environment = environment or self.PRODUCTION
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the current environment."""
        return self.environment.base_url
    
    @property
    def is_test_environment(self) -> bool:
        """Check if current environment is UAT/test environment."""
        return self.environment.name == "uat"
    
    @classmethod
    def production(cls) -> "Config":
        """Create a production configuration."""
        return cls(cls.PRODUCTION)
    
    @classmethod
    def uat(cls) -> "Config":
        """Create a UAT (test) configuration."""
        return cls(cls.UAT)
    
    @classmethod
    def custom(cls, base_url: str, name: str = "custom") -> "Config":
        """
        Create a custom configuration with specified base URL.
        
        Args:
            base_url: The base URL for API endpoints
            name: Optional name for the environment
        """
        return cls(EnvironmentConfig(base_url, name))
    
    def __repr__(self):
        return f"Config(environment={self.environment})"
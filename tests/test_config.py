"""
Unit tests for the configuration module.

Tests configuration classes including environment management,
URL construction, and integration with AuthClient and TheRangeManager.
"""

import pytest
from therange.config import Config, EnvironmentConfig
from therange.auth import AuthClient
from therange.manager import TheRangeManager


class TestEnvironmentConfig:
    """Test EnvironmentConfig class functionality."""
    
    def test_init_basic(self):
        """Test basic initialization of EnvironmentConfig."""
        config = EnvironmentConfig("https://api.example.com/rest")
        
        assert config.base_url == "https://api.example.com/rest/"
        assert config.name == ""
    
    def test_init_with_name(self):
        """Test initialization with name parameter."""
        config = EnvironmentConfig("https://api.example.com/rest", "production")
        
        assert config.base_url == "https://api.example.com/rest/"
        assert config.name == "production"
    
    def test_url_normalization_adds_trailing_slash(self):
        """Test that base_url always has a trailing slash."""
        config = EnvironmentConfig("https://api.example.com/rest")
        assert config.base_url == "https://api.example.com/rest/"
        
        config = EnvironmentConfig("https://api.example.com/rest/")
        assert config.base_url == "https://api.example.com/rest/"
    
    def test_repr(self):
        """Test string representation of EnvironmentConfig."""
        config = EnvironmentConfig("https://api.example.com/rest", "test")
        expected = "EnvironmentConfig(name='test', base_url='https://api.example.com/rest/')"
        assert repr(config) == expected


class TestConfig:
    """Test Config class functionality."""
    
    def test_init_default(self):
        """Test default initialization uses production environment."""
        config = Config()
        
        assert config.environment == Config.PRODUCTION
        assert config.base_url == "https://supplier.rstore.com/rest/"
        assert not config.is_test_environment
    
    def test_init_with_environment(self):
        """Test initialization with specific environment."""
        config = Config(Config.UAT)
        
        assert config.environment == Config.UAT
        assert config.base_url == "https://uatsupplier.rstore.com/rest/"
        assert config.is_test_environment
    
    def test_production_class_method(self):
        """Test production() class method."""
        config = Config.production()
        
        assert config.environment == Config.PRODUCTION
        assert config.base_url == "https://supplier.rstore.com/rest/"
        assert not config.is_test_environment
    
    def test_uat_class_method(self):
        """Test uat() class method."""
        config = Config.uat()
        
        assert config.environment == Config.UAT
        assert config.base_url == "https://uatsupplier.rstore.com/rest/"
        assert config.is_test_environment
    
    def test_custom_class_method(self):
        """Test custom() class method."""
        custom_url = "https://custom.api.com/v1/rest"
        config = Config.custom(custom_url, "custom")
        
        assert config.environment.base_url == "https://custom.api.com/v1/rest/"
        assert config.environment.name == "custom"
        assert config.base_url == "https://custom.api.com/v1/rest/"
        assert not config.is_test_environment  # Only UAT is considered test environment
    
    def test_custom_class_method_default_name(self):
        """Test custom() class method with default name."""
        config = Config.custom("https://example.com/api")
        
        assert config.environment.name == "custom"
    
    def test_predefined_environments(self):
        """Test predefined environment configurations."""
        # Production
        assert Config.PRODUCTION.base_url == "https://supplier.rstore.com/rest/"
        assert Config.PRODUCTION.name == "production"
        
        # UAT
        assert Config.UAT.base_url == "https://uatsupplier.rstore.com/rest/"
        assert Config.UAT.name == "uat"
    
    def test_repr(self):
        """Test string representation of Config."""
        config = Config.uat()
        expected = f"Config(environment={Config.UAT})"
        assert repr(config) == expected


class TestAuthClientWithConfig:
    """Test AuthClient integration with Config."""
    
    def test_auth_client_with_production_config(self):
        """Test AuthClient with production config."""
        config = Config.production()
        auth = AuthClient("user", "pass", config)
        
        assert auth.config == config
        assert auth.base_url == "https://supplier.rstore.com/rest/"
    
    def test_auth_client_with_uat_config(self):
        """Test AuthClient with UAT config."""
        config = Config.uat()
        auth = AuthClient("user", "pass", config)
        
        assert auth.config == config
        assert auth.base_url == "https://uatsupplier.rstore.com/rest/"
    
    def test_auth_client_with_custom_config(self):
        """Test AuthClient with custom config."""
        config = Config.custom("https://custom.api.com/rest", "staging")
        auth = AuthClient("user", "pass", config)
        
        assert auth.config == config
        assert auth.base_url == "https://custom.api.com/rest/"


class TestTheRangeManagerWithConfig:
    """Test TheRangeManager integration with Config."""
    
    def test_manager_with_production_config(self):
        """Test TheRangeManager with production config."""
        config = Config.production()
        manager = TheRangeManager("user", "pass", config)
        
        assert manager.auth.config == config
        assert manager.auth.base_url == "https://supplier.rstore.com/rest/"
    
    def test_manager_with_uat_config(self):
        """Test TheRangeManager with UAT config."""
        config = Config.uat()
        manager = TheRangeManager("user", "pass", config)
        
        assert manager.auth.config == config
        assert manager.auth.base_url == "https://uatsupplier.rstore.com/rest/"
    
    def test_manager_with_custom_config(self):
        """Test TheRangeManager with custom config."""
        config = Config.custom("https://staging.api.com/rest", "staging")
        manager = TheRangeManager("user", "pass", config)
        
        assert manager.auth.config == config
        assert manager.auth.base_url == "https://staging.api.com/rest/"


class TestConfigIntegrationScenarios:
    """Test realistic configuration usage scenarios."""
    
    def test_e2e_testing_scenario(self):
        """Test typical e2e testing scenario with multiple environments."""
        # Production setup
        prod_config = Config.production()
        prod_manager = TheRangeManager("user", "pass", prod_config)
        
        # UAT setup
        uat_config = Config.uat()
        uat_manager = TheRangeManager("user", "pass", uat_config)
        
        # Custom staging setup
        staging_config = Config.custom("https://staging.therange.com/rest", "staging")
        staging_manager = TheRangeManager("user", "pass", staging_config)
        
        # Verify different environments
        assert prod_manager.auth.base_url == "https://supplier.rstore.com/rest/"
        assert uat_manager.auth.base_url == "https://uatsupplier.rstore.com/rest/"
        assert staging_manager.auth.base_url == "https://staging.therange.com/rest/"
    
    def test_config_injection_dependency_pattern(self):
        """Test configuration as dependency injection pattern."""
        def create_manager_for_environment(env_name: str) -> TheRangeManager:
            """Factory function that creates manager based on environment name."""
            if env_name == "production":
                config = Config.production()
            elif env_name == "uat":
                config = Config.uat()
            elif env_name == "staging":
                config = Config.custom("https://staging.api.com/rest", "staging")
            else:
                raise ValueError(f"Unknown environment: {env_name}")
            
            return TheRangeManager("test_user", "test_pass", config)
        
        # Test factory function
        prod_manager = create_manager_for_environment("production")
        uat_manager = create_manager_for_environment("uat")
        staging_manager = create_manager_for_environment("staging")
        
        assert prod_manager.auth.base_url == "https://supplier.rstore.com/rest/"
        assert uat_manager.auth.base_url == "https://uatsupplier.rstore.com/rest/"
        assert staging_manager.auth.base_url == "https://staging.api.com/rest/"
    
    def test_config_with_different_api_versions(self):
        """Test configuration with different API versions."""
        v1_config = Config.custom("https://api.therange.com/v1/rest", "v1")
        v2_config = Config.custom("https://api.therange.com/v2/rest", "v2")
        
        v1_manager = TheRangeManager("user", "pass", v1_config)
        v2_manager = TheRangeManager("user", "pass", v2_config)
        
        assert v1_manager.auth.base_url == "https://api.therange.com/v1/rest/"
        assert v2_manager.auth.base_url == "https://api.therange.com/v2/rest/"
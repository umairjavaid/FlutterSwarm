"""
Configuration management for FlutterSwarm.
Provides centralized configuration loading and access with environment-specific overrides.
"""

import os
import yaml
import json
import threading
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from copy import deepcopy

# Use comprehensive logging system with function tracking
from utils.function_logger import track_function
from utils.comprehensive_logging import get_logger

# Use comprehensive logging system
logger = get_logger("FlutterSwarm.Config")


@dataclass
class ConfigPaths:
    """Configuration file paths."""
    main_config: str = "main_config.yaml"
    agent_config: str = "agent_config.yaml"
    user_config: str = "user_config.yaml"
    env_config: str = ".env"


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""
    pass


class ConfigManager:
    """
    Centralized configuration manager for FlutterSwarm.
    Handles loading, merging, and accessing configuration from multiple sources.
    """
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def __init__(self, 
                 config_dir: str = "config",
                 environment: Optional[str] = None,
                 user_config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            environment: Environment name (development, production, testing)
            user_config_file: Optional user-specific configuration file
        """
        self.config_dir = Path(config_dir)
        self.environment = environment or os.getenv('FLUTTERSWARM_ENV', 'development')
        self.user_config_file = user_config_file
        
        # Configuration storage
        self._config: Dict[str, Any] = {}
        self._agent_configs: Dict[str, Any] = {}
        self._loaded = False
        
        # Configuration file paths
        self.paths = ConfigPaths()
        
        # Load configurations
        self.reload()
    
    @track_function(agent_id="system", log_args=False, log_return=False)
    def reload(self) -> None:
        """Reload all configuration files."""
        try:
            # Load main configuration
            self._load_main_config()
            
            # Load agent configurations
            self._load_agent_config()
            
            # Load user configuration if specified
            if self.user_config_file:
                self._load_user_config()
            
            # Apply environment-specific overrides
            self._apply_environment_overrides()
            
            # Load environment variables
            self._load_environment_variables()
            
            # Validate configuration
            self._validate_config()
            
            self._loaded = True
            logger.info(f"Configuration loaded successfully for environment: {self.environment}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _load_main_config(self) -> None:
        """Load the main configuration file."""
        config_path = self.config_dir / self.paths.main_config
        if not config_path.exists():
            raise ConfigurationError(f"Main configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except (yaml.YAMLError, ValueError, TypeError) as e:
            raise ConfigurationError(f"Failed to parse YAML configuration file {config_path}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file {config_path}: {e}") from e
    
    def _load_agent_config(self) -> None:
        """Load agent-specific configuration."""
        config_path = self.config_dir / "agent_config.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._agent_configs = yaml.safe_load(f) or {}
            except (yaml.YAMLError, ValueError, TypeError) as e:
                logger.error(f"Failed to parse agent configuration YAML: {e}")
                self._agent_configs = {}
            except Exception as e:
                logger.error(f"Failed to load agent configuration: {e}")
                self._agent_configs = {}
    
    def _load_user_config(self) -> None:
        """Load user-specific configuration."""
        if not self.user_config_file:
            return
            
        config_path = Path(self.user_config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    self._merge_configs(self._config, user_config)
            except (yaml.YAMLError, ValueError, TypeError) as e:
                logger.error(f"Failed to parse user configuration YAML: {e}")
            except Exception as e:
                logger.error(f"Failed to load user configuration: {e}")
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides."""
        environments = self._config.get('environments', {})
        if self.environment in environments:
            env_overrides = environments[self.environment]
            self._merge_configs(self._config, env_overrides)
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables."""
        # API Keys
        api_keys = {
            'ANTHROPIC_API_KEY': 'agents.llm.primary.api_key',
            'OPENAI_API_KEY': 'agents.llm.fallback.api_key',
            'GITHUB_TOKEN': 'integrations.apis.github.token',
            'DISCORD_WEBHOOK': 'integrations.apis.discord.webhook'
        }
        
        for env_var, config_path in api_keys.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(config_path, value)
        
        # Other environment variables
        env_mappings = {
            'FLUTTERSWARM_LOG_LEVEL': 'system.logging.level',
            'FLUTTERSWARM_OUTPUT_DIR': 'project.defaults.output_directory',
            'FLUTTERSWARM_TEMP_DIR': 'project.defaults.temp_directory',
            'FLUTTER_SDK_PATH': 'project.flutter.sdk_path',
            'FLUTTERSWARM_DEBUG': 'development.debug.enable_debug_mode',
            'FLUTTERSWARM_MAX_AGENTS': 'system.performance.max_concurrent_agents',
            'FLUTTERSWARM_TIMEOUT': 'system.performance.task_timeout'
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Convert boolean strings
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                # Convert numeric strings
                elif value.isdigit():
                    value = int(value)
                
                self._set_nested_value(config_path, value)
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        required_sections = ['system', 'project', 'agents', 'communication']
        
        for section in required_sections:
            if section not in self._config:
                raise ConfigurationError(f"Required configuration section missing: {section}")
        
        # Validate specific required values using direct access (not self.get to avoid circular dependency)
        required_values = [
            'system.name',
            'system.version',
            'agents.llm.primary.model',
            'project.defaults.output_directory'
        ]
        
        for value_path in required_values:
            if not self._get_direct(value_path):
                raise ConfigurationError(f"Required configuration value missing: {value_path}")
    
    def _get_direct(self, path: str) -> Any:
        """
        Get a configuration value using dot notation without validation checks.
        Used internally during config loading/validation.
        
        Args:
            path: Dot-separated path to the configuration value
            
        Returns:
            Configuration value or None if not found
        """
        keys = path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            path: Dot-separated path to the configuration value
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call reload() first.")
        
        keys = path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent configuration dictionary
        """
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call reload() first.")
        
        # Get base agent config
        agent_config = self._agent_configs.get('agents', {}).get(agent_id, {})
        
        # Apply global agent settings
        global_config = self.get('agents.global', {})
        merged_config = deepcopy(global_config)
        self._merge_configs(merged_config, agent_config)
        
        # Apply agent-specific overrides from main config
        overrides = self.get(f'agents.overrides.{agent_id}', {})
        self._merge_configs(merged_config, overrides)
        
        # Apply global LLM configuration
        llm_config = self.get('agents.llm.primary', {})
        if 'llm' not in merged_config:
            merged_config['llm'] = {}
        
        for key, value in llm_config.items():
            if key not in merged_config['llm']:
                merged_config['llm'][key] = value
        
        return merged_config
    
    def get_all(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call reload() first.")
        return deepcopy(self._config)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a complete configuration section."""
        return self.get(section, {})
    
    def set(self, path: str, value: Any, save: bool = False) -> None:
        """
        Set a configuration value.
        
        Args:
            path: Dot-separated path to the configuration value
            value: Value to set
            save: Whether to save changes to file
        """
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call reload() first.")
        
        self._set_nested_value(path, value)
        
        if save:
            self.save()
    
    def save(self, config_file: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_file: Optional specific file to save to
        """
        if not self._loaded:
            raise ConfigurationError("Configuration not loaded. Call reload() first.")
        
        output_file = config_file or (self.config_dir / "user_config.yaml")
        output_path = Path(output_file)
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def validate_agent_requirements(self, agent_id: str) -> bool:
        """
        Validate that an agent has all required configuration.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if agent configuration is valid
        """
        agent_config = self.get_agent_config(agent_id)
        
        required_fields = ['name', 'role', 'capabilities']
        for field in required_fields:
            if field not in agent_config:
                logger.warning(f"Agent {agent_id} missing required field: {field}")
                return False
        
        # Validate LLM configuration
        llm_config = agent_config.get('llm', {})
        if not llm_config.get('model'):
            logger.warning(f"Agent {agent_id} missing LLM model configuration")
            return False
        
        return True
    
    def get_environment(self) -> str:
        """Get the current environment name."""
        return self.environment
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == 'production'
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == 'testing'
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get_section('system.logging')
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return self.get_section('system.performance')
    
    def get_project_config(self) -> Dict[str, Any]:
        """Get project configuration."""
        return self.get_section('project')
    
    def get_llm_config(self, fallback: bool = False) -> Dict[str, Any]:
        """
        Get LLM configuration.
        
        Args:
            fallback: Whether to get fallback LLM config
            
        Returns:
            LLM configuration dictionary
        """
        key = 'fallback' if fallback else 'primary'
        return self.get(f'agents.llm.{key}', {})
    
    def get_application_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self.get_section('application')
    
    def get_cli_config(self) -> Dict[str, Any]:
        """Get CLI configuration."""
        return self.get_section('application.cli')
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration."""
        return self.get_section('application.display')
    
    def get_status_config(self) -> Dict[str, Any]:
        """Get status configuration."""
        return self.get_section('application.status')
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get_section('application.monitoring')
    
    def get_examples_config(self) -> Dict[str, Any]:
        """Get examples configuration."""
        return self.get_section('application.examples')
    
    def get_filesystem_config(self) -> Dict[str, Any]:
        """Get filesystem configuration."""
        return self.get_section('filesystem')
    
    def get_templates_config(self) -> Dict[str, Any]:
        """Get templates configuration - should return empty as all code is LLM-generated."""
        return {}  # No hardcoded templates - all code generated by LLM agents
    
    def get_content_config(self) -> Dict[str, Any]:
        """Get content configuration."""
        return self.get_section('content')
    
    def get_messages_config(self) -> Dict[str, Any]:
        """Get messages configuration."""
        return self.get_section('content.messages')
    
    def get_qa_config(self) -> Dict[str, Any]:
        """Get quality assurance configuration."""
        return self.get_section('quality_assurance')
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration."""
        return self.get_section('deployment')
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.get_section('security')
    
    def get_communication_config(self) -> Dict[str, Any]:
        """Get communication configuration."""
        return self.get_section('communication')
    
    def get_integrations_config(self) -> Dict[str, Any]:
        """Get integrations configuration."""
        return self.get_section('integrations')
    
    def get_timeout_setting(self, timeout_type: str) -> int:
        """
        Get a specific timeout setting.
        
        Args:
            timeout_type: Type of timeout (agent_response, task_execution, etc.)
            
        Returns:
            Timeout value in seconds
        """
        return self.get(f'application.monitoring.timeouts.{timeout_type}', 60)
    
    def get_interval_setting(self, interval_type: str) -> int:
        """
        Get a specific interval setting.
        
        Args:
            interval_type: Type of interval (qa_monitoring, heartbeat_check, etc.)
            
        Returns:
            Interval value in seconds
        """
        return self.get(f'application.monitoring.intervals.{interval_type}', 30)
    
    def get_threshold_setting(self, threshold_type: str) -> int:
        """
        Get a specific threshold setting.
        
        Args:
            threshold_type: Type of threshold (max_monitoring_rounds, error_retry_limit, etc.)
            
        Returns:
            Threshold value
        """
        return self.get(f'application.monitoring.thresholds.{threshold_type}', 3)
    
    def get_display_setting(self, setting_type: str) -> Any:
        """
        Get a specific display setting.
        
        Args:
            setting_type: Type of display setting
            
        Returns:
            Setting value
        """
        return self.get(f'application.display.{setting_type}')
    
    def get_cli_setting(self, setting_type: str) -> Any:
        """
        Get a specific CLI setting.
        
        Args:
            setting_type: Type of CLI setting
            
        Returns:
            Setting value
        """
        return self.get(f'application.cli.{setting_type}')
    
    def get_message(self, message_type: str) -> str:
        """
        Get a specific message template.
        
        Args:
            message_type: Type of message
            
        Returns:
            Message string
        """
        return self.get(f'content.messages.{message_type}', f'[{message_type}]')
    
    def get_status_icon(self, status: str) -> str:
        """
        Get status icon for a specific status.
        
        Args:
            status: Status type
            
        Returns:
            Icon string
        """
        return self.get(f'application.display.status_icons.{status}', '❓')
    
    def get_file_template(self, template_type: str) -> str:
        """
        Get file template.
        
        Args:
            template_type: Type of template
            
        Returns:
            Template string
        """
        return self.get(f'content.file_templates.{template_type}', '')
    
    def get_build_setting(self, setting_type: str) -> Any:
        """
        Get build configuration setting.
        
        Args:
            setting_type: Type of build setting
            
        Returns:
            Setting value
        """
        return self.get(f'deployment.build.{setting_type}')
    
    def get_cicd_setting(self, setting_type: str) -> Any:
        """
        Get CI/CD configuration setting.
        
        Args:
            setting_type: Type of CI/CD setting
            
        Returns:
            Setting value
        """
        return self.get(f'deployment.cicd.{setting_type}')
    
    def __repr__(self) -> str:
        """String representation of configuration manager."""
        return f"ConfigManager(environment={self.environment}, loaded={self._loaded})"


# Global configuration instance with thread-safe singleton pattern
_config_instance = None
_config_lock = threading.Lock()


def get_config() -> ConfigManager:
    """Get the global configuration manager instance - thread-safe singleton."""
    global _config_instance
    if _config_instance is None:
        with _config_lock:
            if _config_instance is None:  # Double-check pattern
                _config_instance = ConfigManager()
                try:
                    _config_instance.reload()
                except Exception as e:
                    logger.warning(f"Failed to load config during initialization: {e}")
                    # Continue with default config
    return _config_instance


def reload_config() -> None:
    """Reload the global configuration - thread-safe."""
    global _config_instance
    with _config_lock:
        if _config_instance:
            try:
                _config_instance.reload()
            except Exception as e:
                logger.error(f"Failed to reload config: {e}")
        else:
            _config_instance = ConfigManager()
            try:
                _config_instance.reload()
            except Exception as e:
                logger.warning(f"Failed to load config during reload: {e}")


# Convenience functions
def get_setting(path: str, default: Any = None) -> Any:
    """Get a configuration setting."""
    return get_config().get(path, default)


def get_agent_setting(agent_id: str) -> Dict[str, Any]:
    """Get agent-specific configuration."""
    return get_config().get_agent_config(agent_id)


def get_environment() -> str:
    """Get current environment."""
    return get_config().get_environment()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return get_setting('development.debug.enable_debug_mode', False)

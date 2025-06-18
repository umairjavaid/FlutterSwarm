"""
Unit tests for the ConfigManager class.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from pathlib import Path

from config.config_manager import ConfigManager, ConfigurationError


@pytest.mark.unit
class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data for testing."""
        return {
            'system': {
                'name': 'FlutterSwarm',
                'version': '1.0.0',
                'logging': {
                    'level': 'INFO',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'project': {
                'defaults': {
                    'output_directory': './flutter_projects',
                    'backup_directory': './backups'
                }
            },
            'agents': {
                'llm': {
                    'primary': {
                        'model': 'test-model-name',
                        'temperature': 0.7,
                        'max_tokens': 4000
                    }
                },
                'orchestrator': {
                    'capabilities': ['coordination', 'planning'],
                    'timeout': 60,
                    'max_retries': 3
                },
                'implementation': {
                    'capabilities': ['coding', 'flutter'],
                    'timeout': 120,
                    'max_retries': 2
                }
            },
            'communication': {
                'messaging': {
                    'queue_size': 500,
                    'message_ttl': 3600,
                    'max_recent_messages': 10
                },
                'collaboration': {
                    'max_concurrent_collaborations': 5,
                    'timeout': 300
                }
            },
            'tools': {
                'timeout_default': 60,
                'flutter': {
                    'timeout': 300
                },
                'terminal': {
                    'timeout': 120
                }
            },
            'application': {
                'examples': {
                    'default_timeout': 300,
                    'demo_mode': True
                },
                'monitoring': {
                    'thresholds': {
                        'max_monitoring_rounds': 5
                    },
                    'intervals': {
                        'status_update': 2
                    }
                },
                'display': {
                    'status_icons': {
                        'idle': '💤',
                        'working': '🔄',
                        'completed': '✅',
                        'error': '❌'
                    }
                }
            },
            'content': {
                'messages': {
                    'welcome': '🐝 Welcome to FlutterSwarm!',
                    'error': '❌ An error occurred'
                }
            },
            'cli': {
                'console_width': 80,
                'colors': True
            }
        }
    
    @pytest.fixture
    def mock_config_files(self, sample_config_data):
        """Mock configuration files."""
        import yaml
        
        main_config = yaml.dump(sample_config_data)
        agent_config = yaml.dump(sample_config_data['agents'])
        
        files = {
            'config/main_config.yaml': main_config,
            'config/agent_config.yaml': agent_config
        }
        
        def mock_file_open(filename, mode='r', encoding=None):
            # Convert Path objects to strings and normalize
            filename_str = str(filename)
            # Check if the filename ends with one of our expected files
            for file_key in files.keys():
                if filename_str.endswith(file_key) or filename_str == file_key:
                    from io import StringIO
                    return StringIO(files[file_key])
            
            raise FileNotFoundError(f"File {filename} not found")
        
        return mock_file_open
    
    def test_initialization(self, mock_config_files):
        """Test ConfigManager initialization."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Check that the configuration was loaded successfully
                assert config._loaded is True
                assert config._config is not None
                assert config._agent_configs is not None
                
                # Test that we can access some configuration values
                assert config.get('system.name') == 'FlutterSwarm'
                assert config.get('system.version') == '1.0.0'
                
    def test_get_nested_value(self, mock_config_files, sample_config_data):
        """Test getting nested configuration values."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test simple key - Note: environment variables may be added
                value = config.get('agents')
                # Check core structure is preserved
                assert 'orchestrator' in value
                assert 'implementation' in value
                assert 'llm' in value
                
                # Test nested key
                value = config.get('communication.messaging.queue_size')
                assert value == 500
                
                # Test with default value
                value = config.get('nonexistent.key', 'default')
                assert value == 'default'
                
                # Test deep nesting
                value = config.get('tools.flutter.timeout')
                assert value == 300
                
    def test_get_agent_config(self, mock_config_files, sample_config_data):
        """Test getting agent-specific configuration."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test existing agent - get_agent_config merges with LLM config
                orchestrator_config = config.get_agent_config('orchestrator')
                
                # The method should return a merged config that includes LLM settings
                assert 'llm' in orchestrator_config
                assert orchestrator_config['llm']['model'] == 'test-model-name'
                
                # Test non-existent agent returns dict with just LLM config
                unknown_config = config.get_agent_config('unknown_agent')
                assert 'llm' in unknown_config
                
    def test_get_specific_configs(self, mock_config_files, sample_config_data):
        """Test getting specific configuration sections."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test communication config
                comm_config = config.get_communication_config()
                assert comm_config == sample_config_data['communication']
                
                # Test tools config (get_tools_config doesn't exist, use get_section)
                tools_config = config.get_section('tools')
                assert tools_config == sample_config_data['tools']
                
                # Test examples config
                examples_config = config.get_examples_config()
                assert examples_config == sample_config_data['application']['examples']
                
                # Test monitoring config
                monitoring_config = config.get_monitoring_config()
                assert monitoring_config == sample_config_data['application']['monitoring']
                
    def test_get_setting_methods(self, mock_config_files, sample_config_data):
        """Test convenience methods for getting settings."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test CLI settings using get() method
                width = config.get('cli.console_width')
                assert width == 80
                
                colors = config.get('cli.colors')
                assert colors is True
                
                # Test interval settings
                status_interval = config.get_interval_setting('status_update')
                assert status_interval == 2
                
                # Test display config
                display_config = config.get_display_config()
                assert display_config == sample_config_data['application']['display']
                
                # Test messages config
                messages_config = config.get_messages_config()
                assert messages_config == sample_config_data['content']['messages']
                
    def test_missing_config_files(self):
        """Test behavior when configuration files are missing."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(ConfigurationError, match="Main configuration file not found"):
                config = ConfigManager()
            
    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML files."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            with patch('os.path.exists', return_value=True):
                with pytest.raises(ConfigurationError):
                    config = ConfigManager()
                
    def test_default_values(self, mock_config_files):
        """Test default values when keys don't exist."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test with default value
                value = config.get('nonexistent.deeply.nested.key', 'default_value')
                assert value == 'default_value'
                
                # Test without default value
                value = config.get('nonexistent.key')
                assert value is None
                
    def test_environment_variable_override(self, mock_config_files):
        """Test that environment variables can override config values."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                with patch.dict(os.environ, {'FLUTTERSWARM_LOG_LEVEL': 'DEBUG'}):
                    config = ConfigManager()
                    
                    # Environment variables should override config values
                    log_level = config.get('system.logging.level')
                    assert log_level == 'DEBUG'  # From environment variable
                    
    def test_config_validation(self, mock_config_files):
        """Test configuration validation."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test that required sections exist
                all_config = config.get_all()
                assert 'agents' in all_config
                assert 'communication' in all_config
                assert 'tools' in all_config
                
    def test_get_config_singleton(self, mock_config_files):
        """Test that ConfigManager works as expected."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config1 = ConfigManager()
                config2 = ConfigManager()
                
                # Both should be properly initialized
                assert config1._loaded is True
                assert config2._loaded is True
                
    def test_complex_nested_structure(self, mock_config_files):
        """Test handling of complex nested configuration structures."""
        complex_config = {
            'system': {
                'name': 'FlutterSwarm',
                'version': '1.0.0'
            },
            'project': {
                'defaults': {
                    'output_directory': './flutter_projects'
                }
            },
            'agents': {
                'llm': {
                    'primary': {
                        'model': 'test-model',
                        'temperature': 0.7
                    }
                }
            },
            'communication': {},
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'value': 'deep_value'
                        }
                    }
                }
            }
        }
        
        import yaml
        complex_yaml = yaml.dump(complex_config)
        
        with patch('builtins.open', mock_open(read_data=complex_yaml)):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                value = config.get('level1.level2.level3.level4.value')
                assert value == 'deep_value'
                
    def test_config_type_preservation(self, mock_config_files):
        """Test that configuration value types are preserved."""
        with patch('builtins.open', side_effect=mock_config_files):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager()
                
                # Test integer
                queue_size = config.get('communication.messaging.queue_size')
                assert isinstance(queue_size, int)
                assert queue_size == 500
                
                # Test boolean
                demo_mode = config.get('application.examples.demo_mode')
                assert isinstance(demo_mode, bool)
                assert demo_mode is True
                
                # Test string
                welcome_msg = config.get('content.messages.welcome')
                assert isinstance(welcome_msg, str)
                assert welcome_msg == '🐝 Welcome to FlutterSwarm!'
                
                # Test list
                capabilities = config.get('agents.orchestrator.capabilities')
                assert isinstance(capabilities, list)
                assert 'coordination' in capabilities

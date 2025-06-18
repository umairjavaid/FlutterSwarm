# FlutterSwarm Testing Guide

This guide covers the comprehensive testing suite for FlutterSwarm, including how to run tests, understand test structure, and maintain test quality.

## Overview

The FlutterSwarm testing suite follows industry best practices and is organized into four main categories:

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test component interactions
- **End-to-End Tests** (`tests/e2e/`): Test complete workflows
- **Performance Tests** (`tests/performance/`): Test system performance and scalability

## Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt
```

### Running Tests

Use the convenient test runner script:

```bash
# Run all tests
python run_tests.py all

# Run specific test types
python run_tests.py unit           # Unit tests only
python run_tests.py integration    # Integration tests only
python run_tests.py e2e           # End-to-end tests only
python run_tests.py performance   # Performance tests only

# Quick tests (fast tests only, excludes slow/network tests)
python run_tests.py quick

# Generate coverage report
python run_tests.py coverage
```

### Advanced Options

```bash
# Verbose output
python run_tests.py unit --verbose

# Stop on first failure
python run_tests.py all --fail-fast

# Run tests matching a pattern
python run_tests.py unit --pattern "test_orchestrator"
```

### Direct pytest Commands

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_orchestrator_agent.py -v

# Run tests by marker
pytest -m "unit"
pytest -m "not slow"
pytest -m "requires_flutter"

# Run with specific verbosity
pytest tests/ -v --tb=short
```

## Test Structure

### Directory Organization

```
tests/
├── __init__.py                              # Test package initialization
├── conftest.py                              # Shared fixtures and configuration
├── fixtures/                                # Test data and constants
│   ├── test_constants.py                    # Shared test constants
│   └── sample_data.py                       # Sample test data
├── mocks/                                   # Mock implementations
│   ├── __init__.py
│   └── mock_implementations.py              # Comprehensive mocks
├── unit/                                    # Unit tests
│   ├── test_base_agent.py                   # Base agent functionality
│   ├── test_config_manager.py               # Configuration management
│   ├── test_flutter_swarm.py                # Main FlutterSwarm class
│   ├── test_implementation_agent.py         # Implementation agent
│   ├── test_orchestrator_agent.py           # Orchestrator agent
│   ├── test_security_agent.py               # Security agent
│   ├── test_shared_state.py                 # Shared state management
│   ├── test_testing_agent.py                # Testing agent
│   ├── test_tool_implementations.py         # Tool implementations
│   └── test_tools.py                        # Tool framework
├── integration/                             # Integration tests
│   ├── test_advanced_agent_collaboration.py # Complex agent interactions
│   ├── test_agent_collaboration.py          # Basic agent interactions
│   ├── test_cli_integration.py              # CLI integration tests
│   ├── test_flutter_swarm_integration.py    # System integration
│   └── test_tool_integration.py             # Tool integration
├── e2e/                                     # End-to-end tests
│   ├── test_complete_workflows.py           # Basic workflows
│   └── test_comprehensive_workflows.py      # Advanced workflows
└── performance/                             # Performance tests
    └── test_performance_load.py             # Performance and load tests
```

### Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests  
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.requires_flutter`: Tests requiring Flutter SDK
- `@pytest.mark.requires_network`: Tests requiring network access

## Test Categories

### Unit Tests

Test individual components in isolation with comprehensive mocking:

**Coverage Areas:**
- Agent functionality (orchestrator, implementation, testing, security)
- Configuration management
- Shared state management
- Tool implementations (terminal, file, Flutter, Git, analysis)
- Base framework components

**Key Features:**
- Fast execution (< 1 second per test)
- No external dependencies
- Comprehensive mocking
- High code coverage
- Edge case testing

### Integration Tests

Test component interactions and system integration:

**Coverage Areas:**
- Agent collaboration and communication
- Tool integration with agents
- CLI integration with the system
- Configuration loading and validation
- Cross-component data flow

**Key Features:**
- Medium execution time (1-10 seconds per test)
- Limited external dependencies
- Real component interactions
- End-to-end message flows

### End-to-End Tests

Test complete user workflows from start to finish:

**Coverage Areas:**
- Complete project creation workflows
- Multi-platform build processes
- Error handling and recovery
- CLI command execution
- Documentation generation
- Security scanning workflows
- CI/CD pipeline simulation

**Key Features:**
- Longer execution time (10+ seconds per test)
- May require external tools (Flutter SDK)
- Real file system operations
- Complete workflow validation

### Performance Tests

Test system performance, scalability, and resource usage:

**Coverage Areas:**
- Startup time optimization
- Concurrent build handling
- Memory usage monitoring
- Agent response time measurement
- Scalability testing
- Long-running stability
- Load testing scenarios

**Key Features:**
- Performance benchmarking
- Resource monitoring
- Scalability validation
- Memory leak detection
- Throughput measurement

## Test Data and Fixtures

### Shared Fixtures (`conftest.py`)

- `temp_directory`: Temporary directory for file operations
- `mock_anthropic_client`: Mocked AI client
- `mock_shared_state`: Mocked shared state
- `mock_config_manager`: Mocked configuration
- `sample_project_config`: Sample project configuration

### Test Constants (`fixtures/test_constants.py`)

- Project configurations
- Agent configurations
- File content templates
- Expected outputs
- Error messages

### Mock Implementations (`mocks/mock_implementations.py`)

- `MockAgent`: Base mock agent
- `MockTool`: Base mock tool
- `MockConfigManager`: Configuration manager mock
- `MockProjectManager`: Project manager mock
- Specialized agent mocks

## Writing New Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from agents.orchestrator_agent import OrchestratorAgent

class TestOrchestratorAgent:
    @pytest.fixture
    def agent(self, mock_shared_state, mock_config_manager):
        return OrchestratorAgent(
            shared_state=mock_shared_state,
            config_manager=mock_config_manager
        )

    @pytest.mark.unit
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "Orchestrator"
        assert agent.status == AgentStatus.IDLE
    
    @pytest.mark.unit
    async def test_process_message(self, agent, mock_shared_state):
        """Test message processing."""
        message = {
            "type": MessageType.TASK,
            "content": "Create new project"
        }
        
        result = await agent.process_message(message)
        
        assert result["status"] == "success"
        mock_shared_state.add_message.assert_called()
```

### Integration Test Example

```python
import pytest
from flutter_swarm import FlutterSwarm

class TestFlutterSwarmIntegration:
    @pytest.mark.integration
    async def test_complete_agent_workflow(self, temp_directory):
        """Test complete workflow with real agent interactions."""
        swarm = FlutterSwarm()
        await swarm.initialize()
        
        result = await swarm.create_project(
            name="test_app",
            output_dir=temp_directory
        )
        
        assert result["success"] is True
        assert "test_app" in result["project_path"]
```

### Performance Test Example

```python
import pytest
import time
import psutil
from flutter_swarm import FlutterSwarm

class TestPerformance:
    @pytest.mark.performance
    def test_startup_time(self):
        """Test system startup time."""
        start_time = time.time()
        swarm = FlutterSwarm()
        startup_time = time.time() - start_time
        
        # Should start in under 2 seconds
        assert startup_time < 2.0
    
    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage stays within limits."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        swarm = FlutterSwarm()
        # ... perform operations ...
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not use more than 100MB additional memory
        assert memory_increase < 100 * 1024 * 1024
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run quick tests
      run: python run_tests.py quick
    
    - name: Run full test suite
      run: python run_tests.py all
    
    - name: Generate coverage report
      run: python run_tests.py coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Best Practices

### Test Organization

1. **One test class per component**: Group related tests together
2. **Descriptive test names**: Use clear, descriptive test method names
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
4. **Independent tests**: Each test should be independent and not rely on others

### Mocking Strategy

1. **Mock external dependencies**: Always mock external services, APIs, file systems
2. **Use shared mocks**: Leverage `conftest.py` and `mock_implementations.py`
3. **Mock at the boundary**: Mock at the integration points, not internal methods
4. **Verify mock calls**: Assert that mocks are called with expected parameters

### Performance Testing

1. **Set realistic thresholds**: Use achievable but meaningful performance targets
2. **Isolate performance tests**: Run performance tests separately from functional tests
3. **Monitor trends**: Track performance metrics over time
4. **Clean up resources**: Ensure tests clean up after themselves

### Test Data Management

1. **Use fixtures**: Centralize test data in fixtures and constants
2. **Parameterized tests**: Use `@pytest.mark.parametrize` for testing multiple scenarios
3. **Minimal test data**: Use the smallest dataset that validates the behavior
4. **Clean state**: Ensure each test starts with a clean state

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `PYTHONPATH` includes the project root
2. **Async test failures**: Use `@pytest.mark.asyncio` for async tests
3. **Mock not working**: Verify mock patch targets and import paths
4. **Slow tests**: Use `@pytest.mark.slow` for tests > 10 seconds

### Debug Commands

```bash
# Run with maximum verbosity
pytest -vvv --tb=long

# Run single test with debugging
pytest tests/unit/test_orchestrator_agent.py::TestOrchestratorAgent::test_initialization -s

# Show test coverage gaps
pytest --cov=. --cov-report=term-missing

# Profile test execution time
pytest --durations=10
```

## Coverage Goals

- **Overall coverage**: > 80%
- **Unit test coverage**: > 90%
- **Integration test coverage**: > 70%
- **Critical path coverage**: 100%

## Maintenance

### Regular Tasks

1. **Update test data**: Keep test constants and fixtures current
2. **Review slow tests**: Optimize or mark appropriately
3. **Clean up mocks**: Remove unused mocks and update existing ones
4. **Update documentation**: Keep this guide current with changes

### When Adding New Features

1. **Write tests first**: Follow TDD practices where possible
2. **Test all paths**: Include happy path, error cases, and edge cases
3. **Update mocks**: Add new components to mock implementations
4. **Document changes**: Update test documentation for new patterns

This comprehensive testing suite ensures FlutterSwarm maintains high quality, reliability, and performance as it evolves.

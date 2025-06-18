# FlutterSwarm Agent Tools

This document describes the comprehensive tool system implemented for FlutterSwarm agents, enabling them to perform real-world development tasks.

## Overview

The FlutterSwarm tool system provides agents with the ability to:
- Execute shell commands and terminal operations
- Perform file operations (read, write, copy, move, delete)
- Run Flutter-specific commands (build, test, analyze, pub commands)
- Execute Git version control operations
- Perform code analysis, security scanning, and quality checks

## Tool Architecture

### Base Tool System

All tools inherit from the `BaseTool` class which provides:
- Async execution with timeout handling
- Standardized result format (`ToolResult`)
- Parameter validation
- Error handling and status reporting

### Tool Manager

The `ToolManager` class orchestrates tool access and provides:
- Tool registration and discovery
- Agent-specific tool access (via `AgentToolbox`)
- Batch and parallel execution capabilities
- Tool recommendation based on agent type

## Available Tools

### 1. Terminal Tool (`TerminalTool`)

Execute shell commands with full control over the environment.

**Capabilities:**
- Execute shell commands with timeout control
- Run scripts from content (bash, python, dart)
- Check command availability
- Get environment information
- Background process execution

**Example Usage:**
```python
# Execute a command
result = await agent.run_command("flutter --version")

# Run a script
script_result = await agent.execute_tool(
    "terminal", 
    operation="execute_script",
    script_content="echo 'Hello World'",
    script_type="bash"
)

# Check if command exists
exists = await agent.execute_tool("terminal", operation="check_command_exists", command="flutter")
```

### 2. File Tool (`FileTool`)

Comprehensive file and directory operations.

**Capabilities:**
- Read/write files with encoding support
- Copy, move, delete files and directories
- Create directory structures
- Search files with patterns
- JSON/YAML parsing and serialization
- File existence checks

**Example Usage:**
```python
# Read a file
content = await agent.read_file("lib/main.dart")

# Write a file
await agent.write_file("lib/models/user.dart", dart_code)

# Search for files
result = await agent.execute_tool("file", operation="search", pattern="*.dart")

# Create directories
await agent.execute_tool("file", operation="create_directory", directory="lib/features/auth")
```

### 3. Flutter Tool (`FlutterTool`)

Flutter-specific development operations.

**Capabilities:**
- Create Flutter projects
- Build for multiple platforms (Android, iOS, Web, Desktop)
- Run tests with coverage
- Code analysis and formatting
- Package management (pub get, pub add)
- Project cleaning
- Device management
- Flutter doctor diagnostics

**Example Usage:**
```python
# Build for Android
await agent.execute_tool("flutter", operation="build", platform="apk")

# Run tests with coverage
await agent.execute_tool("flutter", operation="test", coverage=True)

# Add packages
await agent.execute_tool("flutter", operation="pub_add", packages=["dio", "bloc"])

# Analyze code
await agent.execute_tool("flutter", operation="analyze")
```

### 4. Git Tool (`GitTool`)

Version control operations for project management.

**Capabilities:**
- Repository initialization and cloning
- Staging, committing, and pushing changes
- Branch management (create, checkout, delete, list)
- Remote management
- Tag operations
- Stash management
- Diff and log viewing
- Reset operations

**Example Usage:**
```python
# Initialize repository
await agent.execute_tool("git", operation="init")

# Add files and commit
await agent.execute_tool("git", operation="add", all_files=True)
await agent.execute_tool("git", operation="commit", message="Initial commit")

# Create and switch to branch
await agent.execute_tool("git", operation="branch", action="create", branch_name="feature/auth")
await agent.execute_tool("git", operation="branch", action="checkout", branch_name="feature/auth")

# Push changes
await agent.execute_tool("git", operation="push", remote="origin", branch="main")
```

### 5. Analysis Tool (`AnalysisTool`)

Code analysis, quality checks, and security scanning.

**Capabilities:**
- Dart code analysis with issue detection
- Security vulnerability scanning
- Code complexity analysis
- Dependency vulnerability checking
- Code metrics calculation
- Test coverage analysis
- Dead code detection
- Performance issue identification

**Example Usage:**
```python
# Analyze Dart code
await agent.execute_tool("analysis", operation="dart_analyze")

# Security scan
await agent.execute_tool("analysis", operation="security_scan", scan_type="comprehensive")

# Code metrics
await agent.execute_tool("analysis", operation="code_metrics")

# Dead code analysis
await agent.execute_tool("analysis", operation="dead_code")
```

## Agent-Specific Tool Access

Each agent type has access to tools relevant to their responsibilities:

### Implementation Agent
- **Primary Tools:** terminal, file, flutter, git, analysis
- **Use Cases:** Code generation, project structure creation, dependency management

### Testing Agent
- **Primary Tools:** terminal, file, flutter, analysis
- **Use Cases:** Test creation, test execution, coverage analysis

### Security Agent
- **Primary Tools:** terminal, file, analysis, git
- **Use Cases:** Security scanning, secure code generation, vulnerability analysis

### Quality Assurance Agent
- **Primary Tools:** terminal, file, flutter, analysis, git
- **Use Cases:** Project validation, quality metrics, issue detection

### Architecture Agent
- **Primary Tools:** terminal, file, analysis
- **Use Cases:** Structure validation, architectural analysis

### DevOps Agent
- **Primary Tools:** terminal, file, flutter, git
- **Use Cases:** Build automation, deployment, CI/CD setup

## Tool Result Format

All tools return a standardized `ToolResult` object:

```python
@dataclass
class ToolResult:
    status: ToolStatus  # SUCCESS, ERROR, WARNING, TIMEOUT
    output: str         # Command output or result message
    error: Optional[str] = None      # Error message if failed
    data: Optional[Dict[str, Any]] = None  # Structured data
    execution_time: Optional[float] = None # Time taken
```

## Error Handling

The tool system provides comprehensive error handling:

- **Timeout Protection:** All tools have configurable timeouts
- **Exception Handling:** Graceful handling of tool failures
- **Status Reporting:** Clear success/failure indication
- **Error Details:** Detailed error messages for debugging

## Examples

### Implementation Agent Creating a Feature

```python
async def implement_auth_feature(self):
    # Create directory structure
    await self.execute_tool("file", operation="create_directory", 
                          directory="lib/features/auth/presentation/pages")
    
    # Generate model file
    model_code = await self.think("Generate User model with email and password fields")
    await self.write_file("lib/features/auth/data/models/user.dart", model_code)
    
    # Add dependencies
    await self.execute_tool("flutter", operation="pub_add", 
                          packages=["firebase_auth", "flutter_bloc"])
    
    # Format code
    await self.run_command("dart format lib/features/auth/")
    
    # Analyze for issues
    analysis = await self.execute_tool("analysis", operation="dart_analyze")
    return analysis
```

### Testing Agent Creating Tests

```python
async def create_comprehensive_tests(self, target_files):
    # Create test directories
    await self.execute_tool("file", operation="create_directory", directory="test/unit")
    await self.execute_tool("file", operation="create_directory", directory="test/widget")
    
    # Generate unit tests
    for file_path in target_files:
        content = await self.read_file(file_path)
        test_code = await self.generate_test_code(content.output)
        
        test_file = file_path.replace("lib/", "test/").replace(".dart", "_test.dart")
        await self.write_file(test_file, test_code)
    
    # Run tests
    test_result = await self.execute_tool("flutter", operation="test", coverage=True)
    return test_result
```

### Security Agent Implementing Security

```python
async def implement_secure_storage(self):
    # Add security dependencies
    await self.execute_tool("flutter", operation="pub_add", 
                          packages=["flutter_secure_storage", "crypto"])
    
    # Generate secure storage service
    storage_code = await self.think("Generate secure storage service with encryption")
    await self.write_file("lib/core/storage/secure_storage.dart", storage_code)
    
    # Perform security scan
    security_scan = await self.execute_tool("analysis", operation="security_scan")
    
    # Check for vulnerabilities
    if security_scan.data and security_scan.data.get("issues"):
        await self.fix_security_issues(security_scan.data["issues"])
    
    return security_scan
```

### Quality Assurance Agent Validation

```python
async def validate_project_quality(self, project_id):
    results = {}
    
    # Code analysis
    results["code_analysis"] = await self.execute_tool("analysis", operation="dart_analyze")
    
    # Security scan
    results["security"] = await self.execute_tool("analysis", operation="security_scan")
    
    # Code metrics
    results["metrics"] = await self.execute_tool("analysis", operation="code_metrics")
    
    # Test coverage
    results["coverage"] = await self.execute_tool("analysis", operation="test_coverage")
    
    # Structure validation
    results["structure"] = await self.validate_project_structure()
    
    return results
```

## Running the Demo

To see the tools in action, run the demo script:

```bash
python demo_agent_tools.py
```

This will demonstrate:
- File operations across all agents
- Flutter command execution
- Git operations
- Security scanning
- Code analysis
- Error handling scenarios

## Configuration

Tools can be configured through the main configuration system:

```yaml
# config/main_config.yaml
tools:
  timeout_default: 60
  flutter:
    timeout: 300
  terminal:
    timeout: 120
  analysis:
    security_scan_depth: "comprehensive"
```

The tool system is now fully integrated into FlutterSwarm, providing agents with real-world development capabilities while maintaining security, reliability, and ease of use.

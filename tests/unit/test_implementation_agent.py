"""
Unit tests for the ImplementationAgent.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from agents.implementation_agent import ImplementationAgent
from shared.state import AgentStatus, MessageType, AgentMessage
from tests.mocks.mock_implementations import MockToolManager, MockAnthropicClient
from tests.fixtures.test_constants import AGENT_CAPABILITIES, TEST_FILE_PATHS


@pytest.mark.unit
class TestImplementationAgent:
    """Test suite for ImplementationAgent."""
    
    @pytest.fixture
    def implementation_agent(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Create implementation agent for testing."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            return ImplementationAgent()
    
    def test_initialization(self, implementation_agent):
        """Test implementation agent initialization."""
        assert implementation_agent.agent_id == "implementation"
        assert implementation_agent.capabilities == AGENT_CAPABILITIES["implementation"]
        assert not implementation_agent.is_running
        assert implementation_agent.status == AgentStatus.IDLE
        
    @pytest.mark.asyncio
    async def test_dart_code_generation(self, implementation_agent):
        """Test Dart code generation capabilities."""
        # Mock AI response for code generation
        implementation_agent.llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""
class User {
  final String id;
  final String email;
  final String name;
  
  User({required this.id, required this.email, required this.name});
  
  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'name': name,
  };
}
"""
        ))
        
        # Mock file operations
        implementation_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="File created successfully"
        ))
        
        # Generate model code
        result = await implementation_agent._generate_model_code({
            "model_name": "User",
            "fields": ["id", "email", "name"],
            "file_path": "lib/models/user.dart"
        })
        
        # Verify code generation
        assert result["status"] == "completed"
        implementation_agent.llm.ainvoke.assert_called_once()
        implementation_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_widget_creation(self, implementation_agent):
        """Test Flutter widget creation."""
        # Mock AI response for widget generation
        implementation_agent.llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""
class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            TextFormField(
              controller: _emailController,
              decoration: InputDecoration(labelText: 'Email'),
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
            ),
            TextFormField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Password'),
              obscureText: true,
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
            ),
            ElevatedButton(
              onPressed: _handleLogin,
              child: Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
  
  void _handleLogin() {
    if (_formKey.currentState?.validate() ?? false) {
      // Handle login logic
    }
  }
}
"""
        ))
        
        # Mock file writing
        implementation_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Widget file created"
        ))
        
        # Create widget
        result = await implementation_agent._create_widget({
            "widget_name": "LoginPage",
            "widget_type": "StatefulWidget", 
            "features": ["form", "validation"],
            "file_path": "lib/pages/login_page.dart"
        })
        
        # Verify widget creation
        assert result["status"] == "completed"
        assert "widget_created" in result
        
    @pytest.mark.asyncio
    async def test_api_integration_code(self, implementation_agent):
        """Test API integration code generation."""
        # Mock API service generation
        implementation_agent._generate_api_service = AsyncMock(return_value={
            "status": "completed",
            "service_file": "lib/services/api_service.dart",
            "methods": ["get", "post", "put", "delete"]
        })
        
        # Generate API integration
        result = await implementation_agent._create_api_integration({
            "api_name": "UserAPI",
            "base_url": "https://api.example.com",
            "endpoints": [
                {"path": "/users", "method": "GET"},
                {"path": "/users", "method": "POST"},
                {"path": "/users/{id}", "method": "PUT"}
            ]
        })
        
        # Verify API integration
        assert result["status"] == "completed"
        implementation_agent._generate_api_service.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_state_management_setup(self, implementation_agent):
        """Test state management implementation."""
        # Mock state management code generation
        implementation_agent._setup_bloc_pattern = AsyncMock(return_value={
            "status": "completed",
            "bloc_files": ["user_bloc.dart", "user_event.dart", "user_state.dart"]
        })
        
        # Setup state management
        result = await implementation_agent._implement_state_management({
            "pattern": "bloc",
            "entities": ["User", "Product"],
            "features": ["authentication", "shopping_cart"]
        })
        
        # Verify state management setup
        assert result["status"] == "completed"
        implementation_agent._setup_bloc_pattern.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_dependency_management(self, implementation_agent):
        """Test dependency addition and management."""
        # Mock Flutter tool for adding dependencies
        implementation_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Dependencies added successfully"
        ))
        
        # Add dependencies
        result = await implementation_agent._add_dependencies([
            "http", "provider", "shared_preferences", "flutter_bloc"
        ])
        
        # Verify dependencies were added
        assert result["status"] == "completed"
        implementation_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_project_structure_creation(self, implementation_agent):
        """Test project structure creation."""
        # Mock directory and file creation
        implementation_agent._create_directory_structure = AsyncMock(return_value={
            "status": "completed",
            "directories": ["lib/models", "lib/services", "lib/pages", "lib/widgets"]
        })
        implementation_agent._create_base_files = AsyncMock(return_value={
            "status": "completed",
            "files": ["main.dart", "app.dart", "routes.dart"]
        })
        
        # Create project structure
        result = await implementation_agent._create_project_structure({
            "project_name": "TestApp",
            "architecture": "clean_architecture",
            "features": ["authentication", "user_management"]
        })
        
        # Verify structure creation
        assert result["status"] == "completed"
        implementation_agent._create_directory_structure.assert_called_once()
        implementation_agent._create_base_files.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_code_formatting(self, implementation_agent):
        """Test code formatting and linting."""
        # Mock dart format tool
        implementation_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Formatted 5 files"
        ))
        
        # Format code
        result = await implementation_agent._format_code(["lib/main.dart", "lib/models/user.dart"])
        
        # Verify formatting
        assert result["status"] == "completed"
        implementation_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_code_analysis(self, implementation_agent):
        """Test code analysis for issues."""
        # Mock analysis tool
        implementation_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="No issues found",
            data={"issues": [], "warnings": []}
        ))
        
        # Analyze code
        result = await implementation_agent._analyze_code()
        
        # Verify analysis
        assert result["status"] == "completed"
        implementation_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_localization_setup(self, implementation_agent):
        """Test internationalization setup."""
        # Mock localization file generation
        implementation_agent._generate_l10n_files = AsyncMock(return_value={
            "status": "completed",
            "languages": ["en", "es", "fr"],
            "files": ["app_en.arb", "app_es.arb", "app_fr.arb"]
        })
        
        # Setup localization
        result = await implementation_agent._setup_localization({
            "languages": ["en", "es", "fr"],
            "default_language": "en"
        })
        
        # Verify localization setup
        assert result["status"] == "completed"
        implementation_agent._generate_l10n_files.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_error_handling_implementation(self, implementation_agent):
        """Test error handling code generation."""
        # Mock error handling setup
        implementation_agent._implement_error_handling = AsyncMock(return_value={
            "status": "completed",
            "error_classes": ["AppException", "NetworkException", "ValidationException"]
        })
        
        # Implement error handling
        result = await implementation_agent._setup_error_handling({
            "error_types": ["network", "validation", "authentication"],
            "logging": True
        })
        
        # Verify error handling
        assert result["status"] == "completed"
        implementation_agent._implement_error_handling.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_database_integration(self, implementation_agent):
        """Test database integration implementation."""
        # Mock database setup
        implementation_agent._setup_database = AsyncMock(return_value={
            "status": "completed",
            "database_type": "sqlite",
            "dao_files": ["user_dao.dart", "product_dao.dart"]
        })
        
        # Setup database
        result = await implementation_agent._implement_database({
            "database_type": "sqlite",
            "entities": ["User", "Product"],
            "relationships": ["user_products"]
        })
        
        # Verify database setup
        assert result["status"] == "completed"
        implementation_agent._setup_database.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_theme_implementation(self, implementation_agent):
        """Test theme and styling implementation."""
        # Mock theme generation
        implementation_agent._generate_theme = AsyncMock(return_value={
            "status": "completed",
            "theme_files": ["app_theme.dart", "colors.dart"],
            "supports_dark_mode": True
        })
        
        # Implement theme
        result = await implementation_agent._implement_theme({
            "primary_color": "#2196F3",
            "secondary_color": "#FF9800", 
            "dark_mode": True,
            "custom_fonts": ["Roboto"]
        })
        
        # Verify theme implementation
        assert result["status"] == "completed"
        implementation_agent._generate_theme.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_navigation_setup(self, implementation_agent):
        """Test navigation system implementation."""
        # Mock navigation setup
        implementation_agent._setup_navigation = AsyncMock(return_value={
            "status": "completed",
            "router_file": "app_router.dart",
            "route_count": 5
        })
        
        # Setup navigation
        result = await implementation_agent._implement_navigation({
            "navigation_type": "go_router",
            "routes": ["/home", "/login", "/profile", "/settings"],
            "nested_routing": True
        })
        
        # Verify navigation setup
        assert result["status"] == "completed"
        implementation_agent._setup_navigation.assert_called_once()
        
    def test_code_quality_validation(self, implementation_agent):
        """Test code quality validation methods."""
        # Test code complexity calculation
        complex_code = """
        void complexMethod() {
          if (condition1) {
            if (condition2) {
              for (int i = 0; i < 10; i++) {
                if (condition3) {
                  while (condition4) {
                    // Complex nested logic
                  }
                }
              }
            }
          }
        }
        """
        
        complexity = implementation_agent._calculate_code_complexity(complex_code)
        assert complexity > 5  # Should detect high complexity
        
        # Test naming convention validation
        valid_names = ["userName", "isValid", "calculateTotal"]
        invalid_names = ["user_name", "IsValid", "Calculate_Total"]
        
        for name in valid_names:
            assert implementation_agent._validate_naming_convention(name, "camelCase")
            
        for name in invalid_names:
            assert not implementation_agent._validate_naming_convention(name, "camelCase")
            
    @pytest.mark.asyncio
    async def test_performance_optimization(self, implementation_agent):
        """Test performance optimization suggestions."""
        # Mock performance analysis
        implementation_agent._analyze_performance_bottlenecks = AsyncMock(return_value={
            "bottlenecks": ["large_list_rendering", "frequent_rebuilds"],
            "suggestions": ["use_list_view_builder", "implement_memo"]
        })
        
        # Analyze performance
        result = await implementation_agent._optimize_performance({
            "target_files": ["lib/pages/list_page.dart"],
            "performance_requirements": {"fps": 60, "startup_time": "< 2s"}
        })
        
        # Verify performance analysis
        implementation_agent._analyze_performance_bottlenecks.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_responsive_design_implementation(self, implementation_agent):
        """Test responsive design implementation."""
        # Mock responsive layout generation
        implementation_agent._generate_responsive_layout = AsyncMock(return_value={
            "status": "completed",
            "breakpoints": ["mobile", "tablet", "desktop"],
            "layout_files": ["responsive_layout.dart"]
        })
        
        # Implement responsive design
        result = await implementation_agent._implement_responsive_design({
            "target_screens": ["home", "profile", "settings"],
            "breakpoints": {"mobile": 480, "tablet": 768, "desktop": 1024}
        })
        
        # Verify responsive implementation
        assert result["status"] == "completed"
        implementation_agent._generate_responsive_layout.assert_called_once()

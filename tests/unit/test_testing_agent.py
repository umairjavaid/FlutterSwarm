"""
Unit tests for the TestingAgent.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from agents.testing_agent import TestingAgent
from shared.state import AgentStatus, MessageType, AgentMessage
from tests.mocks.mock_implementations import MockToolManager, MockAnthropicClient
from tests.fixtures.test_constants import AGENT_CAPABILITIES, TEST_FILE_PATHS


@pytest.mark.unit
class TestTestingAgent:
    """Test suite for TestingAgent."""
    
    @pytest.fixture
    def testing_agent(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Create testing agent for testing."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            return TestingAgent()
    
    def test_initialization(self, testing_agent):
        """Test testing agent initialization."""
        assert testing_agent.agent_id == "testing"
        assert testing_agent.capabilities == AGENT_CAPABILITIES["testing"]
        assert not testing_agent.is_running
        assert testing_agent.status == AgentStatus.IDLE
        
    @pytest.mark.asyncio
    async def test_unit_test_generation(self, testing_agent):
        """Test unit test generation capabilities."""
        # Mock AI response for test generation
        testing_agent.llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""
import 'package:test/test.dart';
import 'package:myapp/models/user.dart';

void main() {
  group('User Model Tests', () {
    test('should create user with valid data', () {
      final user = User(id: '1', email: 'test@example.com', name: 'Test User');
      
      expect(user.id, equals('1'));
      expect(user.email, equals('test@example.com'));
      expect(user.name, equals('Test User'));
    });
    
    test('should convert user to JSON', () {
      final user = User(id: '1', email: 'test@example.com', name: 'Test User');
      final json = user.toJson();
      
      expect(json['id'], equals('1'));
      expect(json['email'], equals('test@example.com'));
      expect(json['name'], equals('Test User'));
    });
  });
}
"""
        ))
        
        # Mock file operations
        testing_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Test file created successfully"
        ))
        
        # Generate unit tests
        result = await testing_agent._generate_unit_tests({
            "target_file": "lib/models/user.dart",
            "class_name": "User",
            "methods": ["toJson", "fromJson"],
            "test_file": "test/models/user_test.dart"
        })
        
        # Verify test generation
        assert result["status"] == "completed"
        testing_agent.llm.ainvoke.assert_called_once()
        testing_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_widget_test_generation(self, testing_agent):
        """Test widget test generation."""
        # Mock widget test generation
        testing_agent.llm.ainvoke = AsyncMock(return_value=MagicMock(
            content="""
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:myapp/pages/login_page.dart';

void main() {
  group('LoginPage Widget Tests', () {
    testWidgets('should display email and password fields', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: LoginPage()));
      
      expect(find.byType(TextFormField), findsNWidgets(2));
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
    });
    
    testWidgets('should show error when fields are empty', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: LoginPage()));
      
      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();
      
      expect(find.text('Required'), findsNWidgets(2));
    });
  });
}
"""
        ))
        
        # Mock file operations
        testing_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Widget test created"
        ))
        
        # Generate widget tests
        result = await testing_agent._generate_widget_tests({
            "widget_file": "lib/pages/login_page.dart",
            "widget_name": "LoginPage",
            "test_scenarios": ["form_validation", "user_interaction"],
            "test_file": "test/widget/login_page_test.dart"
        })
        
        # Verify widget test generation
        assert result["status"] == "completed"
        testing_agent.llm.ainvoke.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_integration_test_generation(self, testing_agent):
        """Test integration test generation."""
        # Mock integration test generation
        testing_agent._generate_integration_test_flow = AsyncMock(return_value={
            "status": "completed",
            "test_file": "integration_test/app_test.dart",
            "test_scenarios": ["user_login_flow", "data_persistence"]
        })
        
        # Generate integration tests
        result = await testing_agent._create_integration_tests({
            "user_flows": ["login", "create_todo", "logout"],
            "api_endpoints": ["/auth/login", "/todos"],
            "database_operations": ["create", "read", "update", "delete"]
        })
        
        # Verify integration test generation
        assert result["status"] == "completed"
        testing_agent._generate_integration_test_flow.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_test_execution(self, testing_agent):
        """Test test execution and reporting."""
        # Mock Flutter test tool
        testing_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="All tests passed: 25 passed, 0 failed",
            data={
                "tests_total": 25,
                "tests_passed": 25,
                "tests_failed": 0,
                "coverage_percentage": 87.5,
                "execution_time": 15.2
            }
        ))
        
        # Execute tests
        result = await testing_agent._run_tests({
            "test_types": ["unit", "widget"],
            "coverage": True,
            "timeout": 300
        })
        
        # Verify test execution
        assert result["status"] == "completed"
        assert result["tests_passed"] == 25
        assert result["coverage_percentage"] == 87.5
        testing_agent.tool_manager.execute_tool.assert_called()
        
    @pytest.mark.asyncio
    async def test_coverage_analysis(self, testing_agent):
        """Test coverage analysis and reporting."""
        # Mock coverage analysis
        testing_agent.tool_manager.execute_tool = AsyncMock(return_value=MagicMock(
            status="SUCCESS",
            output="Coverage report generated",
            data={
                "overall_coverage": 85.7,
                "file_coverage": {
                    "lib/models/user.dart": 95.0,
                    "lib/services/api_service.dart": 78.5,
                    "lib/pages/login_page.dart": 82.3
                },
                "uncovered_lines": [
                    {"file": "lib/services/api_service.dart", "lines": [45, 67, 89]}
                ]
            }
        ))
        
        # Analyze coverage
        result = await testing_agent._analyze_coverage()
        
        # Verify coverage analysis
        assert result["overall_coverage"] == 85.7
        assert "file_coverage" in result
        assert "uncovered_lines" in result
        
    @pytest.mark.asyncio
    async def test_performance_testing(self, testing_agent):
        """Test performance testing capabilities."""
        # Mock performance test generation
        testing_agent._generate_performance_tests = AsyncMock(return_value={
            "status": "completed",
            "test_files": ["test/performance/scroll_performance_test.dart"],
            "metrics": ["frame_time", "memory_usage", "cpu_usage"]
        })
        
        # Create performance tests
        result = await testing_agent._create_performance_tests({
            "target_widgets": ["ListView", "GridView"],
            "performance_metrics": ["fps", "memory", "startup_time"],
            "test_scenarios": ["large_dataset", "rapid_scrolling"]
        })
        
        # Verify performance test creation
        assert result["status"] == "completed"
        testing_agent._generate_performance_tests.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_mock_data_generation(self, testing_agent):
        """Test mock data generation for tests."""
        # Mock data generation
        testing_agent._generate_mock_data = AsyncMock(return_value={
            "status": "completed",
            "mock_files": ["test/mocks/mock_user_data.dart", "test/mocks/mock_api_responses.dart"],
            "data_types": ["User", "Product", "Order"]
        })
        
        # Generate mock data
        result = await testing_agent._create_mock_data({
            "entities": ["User", "Product", "Order"],
            "api_responses": ["/users", "/products", "/orders"],
            "edge_cases": True
        })
        
        # Verify mock data generation
        assert result["status"] == "completed"
        testing_agent._generate_mock_data.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_test_automation_setup(self, testing_agent):
        """Test test automation setup."""
        # Mock automation setup
        testing_agent._setup_test_automation = AsyncMock(return_value={
            "status": "completed",
            "automation_files": ["test/automation/test_runner.dart"],
            "ci_integration": True
        })
        
        # Setup test automation
        result = await testing_agent._create_test_automation({
            "ci_platform": "github_actions",
            "test_schedule": "on_push",
            "notification_settings": {"slack": True, "email": False}
        })
        
        # Verify automation setup
        assert result["status"] == "completed"
        testing_agent._setup_test_automation.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_test_data_validation(self, testing_agent):
        """Test test data validation."""
        # Mock validation
        testing_agent._validate_test_data = AsyncMock(return_value={
            "valid": True,
            "issues": [],
            "suggestions": ["Add edge case tests for empty strings"]
        })
        
        # Validate test data
        result = await testing_agent._validate_test_completeness({
            "source_files": ["lib/models/user.dart", "lib/services/api_service.dart"],
            "test_files": ["test/models/user_test.dart", "test/services/api_service_test.dart"]
        })
        
        # Verify validation
        assert result["valid"] == True
        testing_agent._validate_test_data.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_accessibility_testing(self, testing_agent):
        """Test accessibility testing generation."""
        # Mock accessibility test generation
        testing_agent._generate_accessibility_tests = AsyncMock(return_value={
            "status": "completed",
            "test_files": ["test/accessibility/login_a11y_test.dart"],
            "checks": ["semantic_labels", "contrast_ratio", "screen_reader"]
        })
        
        # Generate accessibility tests
        result = await testing_agent._create_accessibility_tests({
            "target_pages": ["LoginPage", "HomePage"],
            "accessibility_standards": ["WCAG_2.1"],
            "test_tools": ["flutter_accessibility"]
        })
        
        # Verify accessibility test generation
        assert result["status"] == "completed"
        testing_agent._generate_accessibility_tests.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_snapshot_testing(self, testing_agent):
        """Test snapshot testing implementation."""
        # Mock snapshot test generation
        testing_agent._generate_snapshot_tests = AsyncMock(return_value={
            "status": "completed",
            "snapshot_files": ["test/snapshots/login_page_snapshot_test.dart"],
            "snapshots_created": 5
        })
        
        # Generate snapshot tests
        result = await testing_agent._create_snapshot_tests({
            "target_widgets": ["LoginPage", "UserProfile", "ProductCard"],
            "test_variations": ["light_theme", "dark_theme", "different_screen_sizes"]
        })
        
        # Verify snapshot test generation
        assert result["status"] == "completed"
        testing_agent._generate_snapshot_tests.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_end_to_end_testing(self, testing_agent):
        """Test end-to-end testing setup."""
        # Mock E2E test generation
        testing_agent._generate_e2e_tests = AsyncMock(return_value={
            "status": "completed",
            "test_files": ["integration_test/user_journey_test.dart"],
            "user_journeys": ["new_user_onboarding", "purchase_flow"]
        })
        
        # Generate E2E tests
        result = await testing_agent._create_e2e_tests({
            "user_journeys": ["registration", "login", "make_purchase", "logout"],
            "test_devices": ["android", "ios"],
            "test_environments": ["staging", "production"]
        })
        
        # Verify E2E test generation
        assert result["status"] == "completed"
        testing_agent._generate_e2e_tests.assert_called_once()
        
    def test_test_quality_metrics(self, testing_agent):
        """Test test quality metrics calculation."""
        # Mock test metrics
        test_metrics = {
            "total_tests": 50,
            "assertion_count": 125,
            "coverage_percentage": 85.5,
            "test_types": {"unit": 30, "widget": 15, "integration": 5}
        }
        
        # Calculate quality score
        quality_score = testing_agent._calculate_test_quality_score(test_metrics)
        
        # Verify quality calculation
        assert 0 <= quality_score <= 100
        assert quality_score > 70  # Should be good quality with high coverage
        
    @pytest.mark.asyncio
    async def test_test_maintenance(self, testing_agent):
        """Test test maintenance and cleanup."""
        # Mock test maintenance
        testing_agent._cleanup_obsolete_tests = AsyncMock(return_value={
            "removed_tests": 3,
            "updated_tests": 7,
            "status": "completed"
        })
        
        # Perform test maintenance
        result = await testing_agent._maintain_tests({
            "source_changes": ["lib/models/user.dart", "lib/services/api_service.dart"],
            "cleanup_criteria": ["orphaned_tests", "deprecated_methods"]
        })
        
        # Verify maintenance
        assert result["status"] == "completed"
        testing_agent._cleanup_obsolete_tests.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_test_reporting(self, testing_agent):
        """Test comprehensive test reporting."""
        # Mock test report generation
        testing_agent._generate_test_report = AsyncMock(return_value={
            "status": "completed",
            "report_file": "test_reports/test_summary.html",
            "report_data": {
                "total_tests": 50,
                "passed": 48,
                "failed": 2,
                "coverage": 85.5,
                "execution_time": 45.3
            }
        })
        
        # Generate test report
        result = await testing_agent._create_test_report({
            "include_coverage": True,
            "include_performance": True,
            "format": "html"
        })
        
        # Verify report generation
        assert result["status"] == "completed"
        assert "report_data" in result
        testing_agent._generate_test_report.assert_called_once()

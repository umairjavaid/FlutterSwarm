"""
Testing Agent - Creates unit, widget, and integration tests for Flutter applications.
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

class TestingAgent(BaseAgent):
    """
    The Testing Agent specializes in creating comprehensive test suites.
    It generates unit, widget, and integration tests for Flutter applications.
    """
    
    def __init__(self):
        super().__init__("testing")
        self.test_types = ["unit", "widget", "integration", "golden"]
        self.testing_frameworks = ["flutter_test", "mockito", "bloc_test", "patrol"]
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing tasks."""
        if "create_unit_tests" in task_description:
            return await self._create_unit_tests(task_data)
        elif "create_widget_tests" in task_description:
            return await self._create_widget_tests(task_data)
        elif "create_integration_tests" in task_description:
            return await self._create_integration_tests(task_data)
        elif "setup_test_infrastructure" in task_description:
            return await self._setup_test_infrastructure(task_data)
        else:
            return await self._handle_general_testing_task(task_description, task_data)
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "test_strategy":
            return await self._provide_test_strategy(data)
        elif collaboration_type == "test_coverage_analysis":
            return await self._analyze_test_coverage(data)
        elif collaboration_type == "test_automation_setup":
            return await self._setup_test_automation(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "file_added":
            await self._auto_generate_tests(change_data)
        elif event == "implementation_completed":
            await self._create_comprehensive_tests(change_data["project_id"])
    
    async def _create_unit_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create unit tests for business logic and models using tools."""
        project_id = task_data["project_id"]
        target_files = task_data.get("target_files", [])
        
        project = shared_state.get_project_state(project_id)
        
        self.logger.info(f"🧪 Creating unit tests for {len(target_files)} files")
        
        # First, analyze the target files to understand their structure
        file_analyses = []
        for file_path in target_files:
            read_result = await self.read_file(file_path)
            if read_result.status.value == "success":
                analysis = await self._analyze_code_for_testing(read_result.output, file_path)
                file_analyses.append(analysis)
        
        # Generate unit tests based on analysis
        test_files_created = []
        
        for analysis in file_analyses:
            test_code = await self._generate_unit_test_code(analysis)
            
            # Determine test file path
            source_file = analysis["file_path"]
            test_file_path = self._get_test_file_path(source_file, "unit")
            
            # Create test directory if needed
            test_dir = os.path.dirname(test_file_path)
            await self.execute_tool("file", operation="create_directory", directory=test_dir)
            
            # Write test file
            write_result = await self.write_file(test_file_path, test_code)
            
            if write_result.status.value == "success":
                test_files_created.append(test_file_path)
                self.logger.info(f"✅ Created unit test: {test_file_path}")
            else:
                self.logger.error(f"❌ Failed to create test: {test_file_path}")
        
        # Run the tests to ensure they work
        test_result = await self.execute_tool("flutter", operation="test")
        
        # Format the test files
        await self.run_command("dart format test/")
        
        return {
            "test_type": "unit",
            "target_files": target_files,
            "test_files_created": test_files_created,
            "test_execution_result": test_result.data if test_result.data else {},
            "tests_passing": test_result.status.value == "success"
        }
    
    async def _create_widget_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create widget tests for UI components using tools."""
        project_id = task_data["project_id"]
        widget_files = task_data.get("widget_files", [])
        
        self.logger.info(f"🎨 Creating widget tests for {len(widget_files)} widgets")
        
        test_files_created = []
        
        for widget_file in widget_files:
            # Read the widget file
            read_result = await self.read_file(widget_file)
            if read_result.status.value != "success":
                continue
            
            # Analyze the widget for testing
            widget_analysis = await self._analyze_widget_for_testing(read_result.output, widget_file)
            
            # Generate widget test code
            test_code = await self._generate_widget_test_code(widget_analysis)
            
            # Write widget test file
            test_file_path = self._get_test_file_path(widget_file, "widget")
            test_dir = os.path.dirname(test_file_path)
            await self.execute_tool("file", operation="create_directory", directory=test_dir)
            
            write_result = await self.write_file(test_file_path, test_code)
            
            if write_result.status.value == "success":
                test_files_created.append(test_file_path)
                self.logger.info(f"✅ Created widget test: {test_file_path}")
        
        # Run widget tests
        test_result = await self.execute_tool("flutter", operation="test")
        
        return {
            "test_type": "widget",
            "widget_files": widget_files,
            "test_files_created": test_files_created,
            "test_execution_result": test_result.data if test_result.data else {},
            "tests_passing": test_result.status.value == "success"
        }
    
    async def _create_integration_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create integration tests using tools."""
        project_id = task_data["project_id"]
        test_scenarios = task_data.get("scenarios", [])
        
        self.logger.info(f"🔄 Creating integration tests for {len(test_scenarios)} scenarios")
        
        # Create integration test directory
        integration_test_dir = "integration_test"
        await self.execute_tool("file", operation="create_directory", directory=integration_test_dir)
        
        test_files_created = []
        
        for scenario in test_scenarios:
            scenario_name = scenario.get("name", "test_scenario")
            
            # Generate integration test code
            test_code = await self._generate_integration_test_code(scenario)
            
            # Write integration test file
            test_file_path = f"{integration_test_dir}/{scenario_name.lower()}_test.dart"
            write_result = await self.write_file(test_file_path, test_code)
            
            if write_result.status.value == "success":
                test_files_created.append(test_file_path)
                self.logger.info(f"✅ Created integration test: {test_file_path}")
        
        # Add integration test dependencies if needed
        await self._ensure_integration_test_dependencies()
        
        return {
            "test_type": "integration",
            "scenarios": test_scenarios,
            "test_files_created": test_files_created,
            "status": "completed"
        }
    
    async def _setup_test_infrastructure(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup testing infrastructure using tools."""
        project_id = task_data["project_id"]
        
        self.logger.info("🏗️ Setting up test infrastructure")
        
        # Create test directories
        test_directories = [
            "test/unit",
            "test/widget",
            "test/integration",
            "test/mocks",
            "test/fixtures"
        ]
        
        for directory in test_directories:
            await self.execute_tool("file", operation="create_directory", directory=directory)
        
        # Add testing dependencies
        test_dependencies = [
            "mockito",
            "build_runner",
            "json_annotation"
        ]
        
        await self.execute_tool("flutter", operation="pub_add", packages=test_dependencies, dev=True)
        
        # Create test helper files
        await self._create_test_helpers()
        
        # Create mock generation configuration
        await self._create_mock_config()
        
        # Generate initial mocks
        await self.run_command("dart run build_runner build")
        
        return {
            "status": "completed",
            "directories_created": test_directories,
            "dependencies_added": test_dependencies
        }
    
    async def _create_test_helpers(self) -> None:
        """Create test helper files."""
        # Create test utils
        test_utils_code = '''
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class TestUtils {
  static Widget makeTestableWidget(Widget child) {
    return MaterialApp(
      home: child,
    );
  }
  
  static Future<void> pumpUntilFound(
    WidgetTester tester,
    Finder finder, {
    Duration timeout = const Duration(seconds: 10),
  }) async {
    bool timerDone = false;
    final timer = Timer(timeout, () => timerDone = true);
    
    while (timerDone != true) {
      await tester.pump();
      
      final found = tester.any(finder);
      if (found) {
        timerDone = true;
      }
    }
    
    timer.cancel();
  }
}
'''
        
        await self.write_file("test/test_utils.dart", test_utils_code)
        
        # Create mock data factory
        mock_data_code = '''
class MockDataFactory {
  static Map<String, dynamic> createUserJson() {
    return {
      'id': '1',
      'name': 'Test User',
      'email': 'test@example.com',
    };
  }
  
  // Add more mock data factories as needed
}
'''
        
        await self.write_file("test/fixtures/mock_data.dart", mock_data_code)
    
    async def _create_mock_config(self) -> None:
        """Create build runner configuration for mocks."""
        build_yaml_content = '''
targets:
  $default:
    builders:
      mockito|mockBuilder:
        generate_for:
          - test/**_test.dart
'''
        
        await self.write_file("build.yaml", build_yaml_content)
    
    async def _ensure_integration_test_dependencies(self) -> None:
        """Ensure integration test dependencies are added."""
        integration_deps = ["integration_test"]
        
        # Check if already in pubspec
        pubspec_result = await self.read_file("pubspec.yaml")
        if pubspec_result.status.value == "success":
            if "integration_test" not in pubspec_result.output:
                await self.execute_tool("flutter", operation="pub_add", packages=integration_deps, dev=True)

    async def _analyze_code_for_testing(self, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze Dart code to determine testability and generate hints for testing."""
        # Placeholder for code analysis logic
        return {
            "file_path": file_path,
            "functions": self._extract_functions(code),
            "dependencies": self._extract_dependencies(code),
            "has_flutter_widget": "MaterialApp" in code or "CupertinoApp" in code,
            "is_bloc_used": "BlocProvider" in code or "BlocListener" in code,
            "is_getx_used": "GetMaterialApp" in code or "GetBuilder" in code,
            "is_provider_used": "ChangeNotifierProvider" in code or "Provider" in code,
            "mockable_services": self._identify_mockable_services(code)
        }
    
    async def _analyze_widget_for_testing(self, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze Flutter widget code to generate testing hints."""
        # Placeholder for widget analysis logic
        return {
            "file_path": file_path,
            "widget_tree": self._extract_widget_tree(code),
            "key_widgets": self._extract_key_widgets(code),
            "is_stateful": "StatefulWidget" in code,
            "dependencies": self._extract_dependencies(code),
            "mockable_services": self._identify_mockable_services(code)
        }
    
    def _extract_functions(self, code: str) -> List[str]:
        """Extract function names from Dart code."""
        import re
        pattern = r'\bvoid\s+(\w+)\s*\('
        matches = re.findall(pattern, code)
        return matches
    
    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract package dependencies from Dart code."""
        import re
        pattern = r'import\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(pattern, code)
        return matches
    
    def _extract_widget_tree(self, code: str) -> List[str]:
        """Extract widget tree structure from Flutter widget code."""
        import re
        pattern = r'(\w+)\s*:\s*([^,]+)'
        matches = re.findall(pattern, code)
        return [f"{m[0]}: {m[1]}" for m in matches]
    
    def _extract_key_widgets(self, code: str) -> List[str]:
        """Extract keys of widgets that have keys assigned."""
        import re
        pattern = r'key:\s*ValueKey\(([^)]+)\)'
        matches = re.findall(pattern, code)
        return [m[0] for m in matches]
    
    def _identify_mockable_services(self, code: str) -> List[str]:
        """Identify services in the code that can be mocked."""
        # Heuristic: services are often classes that are instantiated in the code
        import re
        pattern = r'new\s+(\w+)\s*\('
        matches = re.findall(pattern, code)
        return matches
    
    async def _generate_unit_test_code(self, analysis: Dict[str, Any]) -> str:
        """Generate unit test code based on analysis of the Dart code."""
        # Simplified test code generation
        test_code = '''
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:myapp/[[FILE_PATH]]';

class MockService extends Mock implements [[SERVICE_NAME]] {}

void main() {
  group('[[CLASS_NAME]]', () {
    MockService mockService;
    [[CLASS_NAME]] instance;

    setUp(() {
      mockService = MockService();
      instance = [[CLASS_NAME]](mockService);
    });

    test('should do something', () async {
      // Arrange
      when(mockService.someMethod()).thenAnswer((_) async => 'some value');

      // Act
      final result = await instance.someFunction();

      // Assert
      expect(result, 'expected value');
      verify(mockService.someMethod()).called(1);
    });
  });
}
'''
        
        # Replace placeholders with actual values
        file_path = analysis["file_path"].replace("/", ".").replace(".dart", "")
        service_name = analysis["dependencies"][0] if analysis["dependencies"] else "MyService"
        class_name = analysis["functions"][0] + "Test" if analysis["functions"] else "MyServiceTest"
        
        test_code = test_code.replace("[[FILE_PATH]]", file_path)
        test_code = test_code.replace("[[SERVICE_NAME]]", service_name)
        test_code = test_code.replace("[[CLASS_NAME]]", class_name)
        
        return test_code
    
    async def _generate_widget_test_code(self, analysis: Dict[str, Any]) -> str:
        """Generate widget test code based on analysis of the Flutter widget code."""
        # Simplified widget test code generation
        test_code = '''
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:myapp/[[FILE_PATH]]';

void main() {
  testWidgets('should build [[WIDGET_NAME]] correctly', (WidgetTester tester) async {
    // Arrange
    await tester.pumpWidget(MaterialApp(home: [[WIDGET_NAME]]()));

    // Act
    // Interact with the widget if needed

    // Assert
    expect(find.byType([[WIDGET_NAME]]), findsOneWidget);
  });
}
'''
        
        # Replace placeholders with actual values
        file_path = analysis["file_path"].replace("/", ".").replace(".dart", "")
        widget_name = analysis["key_widgets"][0] if analysis["key_widgets"] else "MyWidget"
        
        test_code = test_code.replace("[[FILE_PATH]]", file_path)
        test_code = test_code.replace("[[WIDGET_NAME]]", widget_name)
        
        return test_code
    
    async def _generate_integration_test_code(self, scenario: Dict[str, Any]) -> str:
        """Generate integration test code based on the user scenario."""
        # Simplified integration test code generation
        test_code = '''
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:myapp/[[APP_PATH]]' as app;

void main() {
  testWidgets('[[SCENARIO_NAME]]', (WidgetTester tester) async {
    // Arrange
    app.main();
    await tester.pumpAndSettle();

    // Act
    // Perform actions for the scenario

    // Assert
    // Verify expected outcomes
  });
}
'''
        
        scenario_name = scenario.get("name", "test_scenario")
        app_path = scenario.get("app_path", "lib/main.dart")
        
        # Replace placeholders with actual values
        test_code = test_code.replace("[[SCENARIO_NAME]]", scenario_name)
        test_code = test_code.replace("[[APP_PATH]]", app_path)
        
        return test_code
    
    async def _provide_test_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide testing strategy recommendations."""
        project_complexity = data.get("complexity", "medium")
        features = data.get("features", [])
        
        strategy_prompt = f"""
        Provide a comprehensive testing strategy for:
        
        Project Complexity: {project_complexity}
        Features: {features}
        
        Recommend:
        1. Test pyramid distribution (unit vs widget vs integration)
        2. Testing frameworks and tools
        3. Test coverage targets
        4. Automation strategy
        5. Performance testing approach
        6. Security testing considerations
        
        Provide specific recommendations based on Flutter best practices.
        """
        
        strategy = await self.think(strategy_prompt, {
            "complexity": project_complexity,
            "features": features
        })
        
        return {
            "strategy": strategy,
            "complexity": project_complexity,
            "test_types": self.test_types
        }
    
    async def _auto_generate_tests(self, change_data: Dict[str, Any]) -> None:
        """Automatically generate tests for new files."""
        filename = change_data.get("filename", "")
        
        if filename.endswith('.dart') and not filename.startswith('test/'):
            # This is a new implementation file, generate tests
            project_id = change_data.get("project_id")
            if project_id:
                await self._create_unit_tests({
                    "project_id": project_id,
                    "target_files": [filename]
                })
    
    async def _handle_general_testing_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general testing tasks."""
        response = await self.think(f"Handle testing task: {task_description}", task_data)
        return {"response": response, "task": task_description}

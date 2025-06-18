"""
Testing Agent - Creates unit, widget, and integration tests for Flutter applications.
"""

import asyncio
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
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
        """Create unit tests for business logic and models."""
        project_id = task_data["project_id"]
        target_files = task_data.get("target_files", [])
        
        project = shared_state.get_project_state(project_id)
        
        unit_test_prompt = f"""
        Create comprehensive unit tests for the following Flutter/Dart code:
        
        Target Files: {target_files}
        Project Context: {project.name}
        
        Generate unit tests that cover:
        
        1. **Model Tests**:
           - Serialization/deserialization (toJson/fromJson)
           - Equality and hashCode
           - copyWith methods
           - Edge cases and null handling
        
        2. **Repository Tests**:
           - Mock external dependencies
           - Test success scenarios
           - Test error scenarios
           - Test caching behavior
        
        3. **Business Logic Tests**:
           - Use case implementations
           - State management logic
           - Validation logic
           - Error handling
        
        4. **Utility Function Tests**:
           - Helper functions
           - Extension methods
           - Validators
           - Formatters
        
        Follow these testing best practices:
        - Use descriptive test names (should_returnUser_when_validEmailProvided)
        - Arrange, Act, Assert pattern
        - Mock external dependencies using mockito
        - Test edge cases and error conditions
        - Use proper test groups and setUp/tearDown
        
        Example unit test structure:
        import 'package:flutter_test/flutter_test.dart';
        import 'package:mockito/mockito.dart';
        import 'package:mockito/annotations.dart';
        
        @GenerateMocks([ApiService])
        void main() {{
          group('UserRepository', () {{
            late UserRepository repository;
            late MockApiService mockApiService;
            
            setUp(() {{
              mockApiService = MockApiService();
              repository = UserRepository(mockApiService);
            }});
            
            group('getUser', () {{
              test('should return User when API call is successful', () async {{
                // Arrange
                const userId = '123';
                final userJson = {{'id': userId, 'name': 'John'}};
                when(mockApiService.getUser(userId))
                    .thenAnswer((_) async => userJson);
                
                // Act
                final result = await repository.getUser(userId);
                
                // Assert
                expect(result, isA<User>());
                expect(result.id, userId);
                verify(mockApiService.getUser(userId)).called(1);
              }});
              
              test('should throw Exception when API call fails', () async {{
                // Arrange
                const userId = '123';
                when(mockApiService.getUser(userId))
                    .thenThrow(ApiException('Network error'));
                
                // Act & Assert
                expect(
                  () => repository.getUser(userId),
                  throwsA(isA<ApiException>()),
                );
              }});
            }});
          }});
        }}
        
        Generate complete test files with proper imports and mocks.
        """
        
        test_code = await self.think(unit_test_prompt, {
            "project": project,
            "target_files": target_files,
            "test_frameworks": self.testing_frameworks
        })
        
        test_files = await self._parse_and_create_test_files(project_id, test_code, "unit")
        
        return {
            "test_type": "unit",
            "target_files": target_files,
            "test_files_created": test_files,
            "code": test_code
        }
    
    async def _create_widget_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create widget tests for UI components."""
        project_id = task_data["project_id"]
        widgets = task_data.get("widgets", [])
        
        widget_test_prompt = f"""
        Create comprehensive widget tests for these Flutter widgets:
        
        Widgets: {widgets}
        
        Generate widget tests that cover:
        
        1. **Widget Rendering**:
           - Verify widgets are built correctly
           - Check for required child widgets
           - Validate initial state
        
        2. **User Interactions**:
           - Tap gestures
           - Text input
           - Scroll behavior
           - Form submissions
        
        3. **State Changes**:
           - Loading states
           - Error states
           - Success states
           - Navigation transitions
        
        4. **Accessibility**:
           - Semantic labels
           - Screen reader support
           - Keyboard navigation
        
        5. **Responsive Design**:
           - Different screen sizes
           - Orientation changes
           - Platform differences
        
        Use these widget testing patterns:
        import 'package:flutter/material.dart';
        import 'package:flutter_test/flutter_test.dart';
        import 'package:bloc_test/bloc_test.dart';
        import 'package:flutter_bloc/flutter_bloc.dart';
        
        void main() {{
          group('LoginScreen Widget Tests', () {{
            late AuthBloc mockAuthBloc;
            
            setUp(() {{
              mockAuthBloc = MockAuthBloc();
            }});
            
            Widget createWidgetUnderTest() {{
              return MaterialApp(
                home: BlocProvider<AuthBloc>(
                  create: (_) => mockAuthBloc,
                  child: const LoginScreen(),
                ),
              );
            }}
            
            testWidgets('should display email and password fields', (tester) async {{
              // Arrange
              when(() => mockAuthBloc.state).thenReturn(AuthInitial());
              
              // Act
              await tester.pumpWidget(createWidgetUnderTest());
              
              // Assert
              expect(find.byType(TextFormField), findsNWidgets(2));
              expect(find.text('Email'), findsOneWidget);
              expect(find.text('Password'), findsOneWidget);
            }});
            
            testWidgets('should trigger login when button pressed', (tester) async {{
              // Arrange
              when(() => mockAuthBloc.state).thenReturn(AuthInitial());
              
              // Act
              await tester.pumpWidget(createWidgetUnderTest());
              await tester.enterText(find.byType(TextFormField).first, 'test@example.com');
              await tester.enterText(find.byType(TextFormField).last, 'password');
              await tester.tap(find.byType(ElevatedButton));
              await tester.pump();
              
              // Assert
              verify(() => mockAuthBloc.add(any(that: isA<AuthLoginRequested>()))).called(1);
            }});
            
            testWidgets('should show loading indicator when authenticating', (tester) async {{
              // Arrange
              when(() => mockAuthBloc.state).thenReturn(AuthLoading());
              
              // Act
              await tester.pumpWidget(createWidgetUnderTest());
              
              // Assert
              expect(find.byType(CircularProgressIndicator), findsOneWidget);
            }});
          }});
        }}
        
        Generate complete widget test files with proper test setup and teardown.
        """
        
        test_code = await self.think(widget_test_prompt, {
            "widgets": widgets,
            "project": shared_state.get_project_state(project_id)
        })
        
        test_files = await self._parse_and_create_test_files(project_id, test_code, "widget")
        
        return {
            "test_type": "widget",
            "widgets": widgets,
            "test_files_created": test_files,
            "code": test_code
        }
    
    async def _create_integration_tests(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create integration tests for complete user flows."""
        project_id = task_data["project_id"]
        user_flows = task_data.get("user_flows", [])
        
        integration_test_prompt = f"""
        Create integration tests for these user flows:
        
        User Flows: {user_flows}
        
        Generate integration tests that cover:
        
        1. **End-to-End User Journeys**:
           - Complete authentication flow
           - CRUD operations
           - Navigation between screens
           - Data persistence
        
        2. **API Integration**:
           - Real API calls (with test environment)
           - Network error handling
           - Data synchronization
        
        3. **Platform Integration**:
           - Device features (camera, location, etc.)
           - Push notifications
           - Deep links
        
        4. **Performance Testing**:
           - App startup time
           - Scroll performance
           - Memory usage
        
        Use integration_test package:
        import 'package:flutter/material.dart';
        import 'package:flutter_test/flutter_test.dart';
        import 'package:integration_test/integration_test.dart';
        import 'package:myapp/main.dart' as app;
        
        void main() {{
          IntegrationTestWidgetsFlutterBinding.ensureInitialized();
          
          group('User Authentication Flow', () {{
            testWidgets('complete login and logout flow', (tester) async {{
              // Start the app
              app.main();
              await tester.pumpAndSettle();
              
              // Navigate to login screen
              await tester.tap(find.text('Login'));
              await tester.pumpAndSettle();
              
              // Enter credentials
              await tester.enterText(find.byKey(const Key('email_field')), 'test@example.com');
              await tester.enterText(find.byKey(const Key('password_field')), 'password123');
              
              // Submit login
              await tester.tap(find.byKey(const Key('login_button')));
              await tester.pumpAndSettle();
              
              // Verify successful login
              expect(find.text('Welcome'), findsOneWidget);
              
              // Logout
              await tester.tap(find.byKey(const Key('logout_button')));
              await tester.pumpAndSettle();
              
              // Verify logout
              expect(find.text('Login'), findsOneWidget);
            }});
          }});
        }}
        
        Generate complete integration test files with realistic user scenarios.
        """
        
        test_code = await self.think(integration_test_prompt, {
            "user_flows": user_flows,
            "project": shared_state.get_project_state(project_id)
        })
        
        test_files = await self._parse_and_create_test_files(project_id, test_code, "integration")
        
        return {
            "test_type": "integration",
            "user_flows": user_flows,
            "test_files_created": test_files,
            "code": test_code
        }
    
    async def _setup_test_infrastructure(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up testing infrastructure and configuration."""
        project_id = task_data["project_id"]
        
        infrastructure_prompt = f"""
        Set up comprehensive testing infrastructure for this Flutter project:
        
        Create the following test configuration files:
        
        1. **Test Configuration**:
           - test/flutter_test_config.dart
           - Test environment setup
           - Mock service configurations
        
        2. **Test Utilities**:
           - test/helpers/test_helpers.dart
           - Common test widgets
           - Mock data factories
           - Test utilities
        
        3. **Mock Definitions**:
           - test/mocks/mocks.dart
           - Mockito annotations
           - Mock class generations
        
        4. **Golden Test Setup**:
           - Golden file management
           - Cross-platform golden tests
           - Screenshot comparisons
        
        5. **CI/CD Test Scripts**:
           - test_runner.dart
           - Coverage reporting
           - Test result formatting
        
        Example test configuration:
        // test/flutter_test_config.dart
        import 'dart:async';
        import 'package:flutter_test/flutter_test.dart';
        
        Future<void> testExecutable(FutureOr<void> Function() testMain) async {{
          setUpAll(() async {{
            // Global test setup
            TestWidgetsFlutterBinding.ensureInitialized();
          }});
          
          await testMain();
        }}
        
        Include proper package dependencies and build configurations.
        """
        
        infrastructure_code = await self.think(infrastructure_prompt, {
            "project": shared_state.get_project_state(project_id)
        })
        
        files_created = await self._parse_and_create_test_files(project_id, infrastructure_code, "infrastructure")
        
        return {
            "infrastructure_type": "testing",
            "files_created": files_created,
            "code": infrastructure_code
        }
    
    async def _parse_and_create_test_files(self, project_id: str, test_content: str, test_type: str) -> List[str]:
        """Parse and create test files."""
        files_created = []
        
        # Simplified file parsing - in real implementation, this would be more sophisticated
        lines = test_content.split('\n')
        current_file = None
        current_content = []
        
        for line in lines:
            if line.startswith('// File:') or line.startswith('# File:'):
                if current_file and current_content:
                    shared_state.add_file_to_project(
                        project_id, 
                        current_file, 
                        '\n'.join(current_content)
                    )
                    files_created.append(current_file)
                
                current_file = line.split(':', 1)[1].strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        if current_file and current_content:
            shared_state.add_file_to_project(
                project_id, 
                current_file, 
                '\n'.join(current_content)
            )
            files_created.append(current_file)
        
        # Store test results
        project = shared_state.get_project_state(project_id)
        if project:
            project.test_results[test_type] = {
                "files_created": files_created,
                "status": "created",
                "coverage": "pending"
            }
        
        return files_created
    
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

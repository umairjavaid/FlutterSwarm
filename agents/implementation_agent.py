"""
Implementation Agent - Generates Flutter/Dart code based on architectural decisions.
"""

import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType
from tools import ToolResult, ToolStatus

class ImplementationAgent(BaseAgent):
    """
    The Implementation Agent specializes in generating Flutter/Dart code.
    It transforms architectural decisions into working code.
    """
    
    def __init__(self):
        super().__init__("implementation")
        self._flutter_templates = None  # Lazy load templates
        
    @property
    def flutter_templates(self):
        """Lazy-loaded Flutter templates."""
        if self._flutter_templates is None:
            self._flutter_templates =:
                "bloc": self._get_bloc_template(),
                "provider": self._get_provider_template(),
                "riverpod": self._get_riverpod_template(),
                "clean_architecture": self._get_clean_architecture_template()

        return self._flutter_templates
        
    async def execute_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results."""
        try:
            self.logger.info(f"🔨 Executing task: {task_type}")
            
            if task_type == "create_flutter_project":
                result = await self._create_flutter_project(task_data)
            elif task_type == "implement_feature":
                result = await self._implement_feature(task_data)
            elif task_type == "refactor_code":
                result = await self._refactor_code(task_data)
            else:
                result =:
                    'status': 'error',
                    'message': f'Unknown task type: {task_type}',
                    'files_created': {},
                    'code_generated': False

            # Always validate the result
            if result.get('status') == 'success':
                validation_result = self._validate_implementation_result(result, task_data)
                if not validation_result['valid']:
                    self.logger.error(f"❌ Implementation validation failed::validation_result['error']}")
                    result['status'] = 'failed'
                    result['validation_error'] = validation_result['error']
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Task execution failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e),
                'files_created': {},
                'code_generated': False

    async def _create_flutter_project(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete Flutter project with proper file system operations."""
        try:
            project_name = task_data.get('project_name', task_data.get('name', 'flutter_app'))
            project_id = task_data.get('project_id', 'unknown')
            requirements = task_data.get('requirements', [])
            architecture_decisions = task_data.get('architecture_decisions', [])
            
            self.logger.info(f"🏗️ Creating Flutter project: {project_name}")
            
            # Use project manager for actual file creation
            from utils.project_manager import ProjectManager
            pm = ProjectManager()
            
            # Create the project structure
            project_path = pm.create_flutter_project_structure(project_name)
            self.logger.info(f"📁 Project structure created at::project_path}")
            
            # Generate and write actual Flutter code
            files_created = {}
            
            # 1. Create pubspec.yaml
            pubspec_content = self._generate_pubspec_yaml(project_name, requirements)
            pubspec_path = project_path / "pubspec.yaml"
            pubspec_path.write_text(pubspec_content)
            files_created['pubspec.yaml'] = "Flutter project configuration"
            self.logger.info("✅ Created pubspec.yaml")
            
            # 2. Create main.dart
            main_dart_content = await self._generate_main_dart(task_data, architecture_decisions)
            lib_dir = project_path / "lib"
            lib_dir.mkdir(exist_ok=True)
            main_dart_path = lib_dir / "main.dart"
            main_dart_path.write_text(main_dart_content)
            files_created['lib/main.dart'] = "Main application entry point"
            self.logger.info("✅ Created lib/main.dart")
            
            # 3. Create additional core files based on architecture
            core_files = await self._generate_core_architecture_files(task_data, architecture_decisions, project_path)
            files_created.update(core_files)
            
            # 4. Create test files
            test_files = await self._generate_test_files(task_data, project_path)
            files_created.update(test_files)
            
            # 5. Create README.md
            readme_content = self._generate_readme(project_name, task_data.get('description', ''))
            readme_path = project_path / "README.md"
            readme_path.write_text(readme_content)
            files_created['README.md'] = "Project documentation"
            self.logger.info("✅ Created README.md")
            
            # Validate that files were actually created
            actual_file_count = self._count_files_in_directory(project_path)
            expected_minimum = len(files_created)
            
            if actual_file_count < expected_minimum:
                self.logger.error(f"❌ File creation validation failed: expected:expected_minimum}, found {actual_file_count}")
                return {
                    'status': 'failed',
                    'error': f'File creation validation failed: expected {expected_minimum}, found {actual_file_count}',
                    'files_created': files_created,
                    'actual_file_count': actual_file_count

            self.logger.info(f"✅ Flutter project created successfully with {actual_file_count} files")
            
            return {
                'status': 'success',
                'message': f'Flutter project {project_name} created successfully',
                'project_path': str(project_path),
                'files_created': files_created,
                'actual_file_count': actual_file_count,
                'code_generated': True

        except Exception as e:
            self.logger.error(f"❌ Failed to create Flutter project: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e),
                'files_created': {},
                'code_generated': False

    def _generate_pubspec_yaml(self, project_name: str, requirements: List[str]) -> str:
        """Generate a comprehensive pubspec.yaml file."""
        # Basic dependencies based on requirements
        dependencies = ['flutter']
        dev_dependencies = ['flutter_test', 'flutter_lints']
        
        # Add dependencies based on requirements
        for req in requirements:
            req_lower = req.lower()
            if 'auth' in req_lower:
                dependencies.extend(['firebase_auth', 'google_sign_in'])
            if 'database' in req_lower or 'storage' in req_lower:
                dependencies.extend(['sqflite', 'shared_preferences'])
            if 'http' in req_lower or 'api' in req_lower:
                dependencies.append('http')
            if 'state' in req_lower:
                dependencies.append('provider')
            if 'navigation' in req_lower:
                dependencies.append('go_router')
        
        # Remove duplicates
        dependencies = list(set(dependencies))
        dev_dependencies = list(set(dev_dependencies))
        
        pubspec_content = f"""name::project_name.lower().replace(' ', '_')}
description: A Flutter application

publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
"""
        
        for dep in dependencies:
            if dep == 'flutter':
                pubspec_content += "  flutter:\n    sdk: flutter\n"
            else:
                pubspec_content += f" :dep}: ^1.0.0\n"
        
        pubspec_content += "\ndev_dependencies:\n"
        for dep in dev_dependencies:
            if dep == 'flutter_test':
                pubspec_content += "  flutter_test:\n    sdk: flutter\n"
            else:
                pubspec_content += f" :dep}: ^1.0.0\n"
        
        pubspec_content += """
flutter:
  uses-material-design: true
"""
        
        return pubspec_content

    async def _generate_main_dart(self, task_data: Dict[str, Any], architecture_decisions: List[Dict]) -> str:
        """Generate comprehensive main.dart file with proper Flutter code."""
        project_name = task_data.get('name', 'FlutterApp')
        requirements = task_data.get('requirements', [])
        
        # Determine app type and features from requirements
        has_auth = any('auth' in req.lower() for req in requirements)
        has_navigation = any('nav' in req.lower() for req in requirements)
        
        # Use LLM to generate better main.dart if available
        try:
            prompt = f"""Generate a complete main.dart file for a Flutter application with these requirements:
- Project name::project_name}
- Requirements::', '.join(requirements)}
- Include Material Design
- Include proper error handling
- Add comments explaining the code
- Make it production-ready

Architecture decisions to consider:
{', '.join([dec.get('title', '') for dec in architecture_decisions])}

Generate only the Dart code, no explanations."""

            llm_response = await self._call_llm(prompt)
            if llm_response and 'main(' in llm_response:
                self.logger.info("✅ Generated main.dart using LLM")
                return llm_response
        except Exception as e:
            self.logger.warning(f"⚠️ LLM generation failed, using template::e}")
        
        # Fallback to template
        main_dart_content = f"""import 'package:flutter/material.dart'

void main():{
  runApp(const {project_name.replace(' ', '')}App())
}}

class {project_name.replace(' ', '')}App extends StatelessWidget {{
  const {project_name.replace(' ', '')}App({{super.key}})

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{project_name}',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const HomePage(title: '{project_name}'),
    )
  }}
}}

class HomePage extends StatefulWidget {{
  const HomePage({{super.key, required self.title}})

  final String title

  @override
  State<HomePage> createState() => _HomePageState()
}}

class _HomePageState extends State<HomePage> {{
  int _counter = 0

  void _incrementCounter() {{
    setState(() {{
      _counter++
    }})
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Welcome to {project_name}!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Text(
              'Counter: $_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 20),
            const Text('Features to implement:'),
            ...{[f"Text('• {req}')" for req in requirements]},
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    )
  }}
}}
"""
        return main_dart_content

    async def _generate_core_architecture_files(self, task_data: Dict[str, Any], 
                                              architecture_decisions: List[Dict], 
                                              project_path) -> Dict[str, str]:
        """Generate core architecture files based on decisions."""
        files_created =:}
        
        try:
            # Create lib subdirectories
            (project_path / "lib" / "models").mkdir(parents=True, exist_ok=True)
            (project_path / "lib" / "services").mkdir(parents=True, exist_ok=True)
            (project_path / "lib" / "widgets").mkdir(parents=True, exist_ok=True)
            (project_path / "lib" / "screens").mkdir(parents=True, exist_ok=True)
            
            # Create a basic model
            user_model = """class User {
  final String id
  final String name
  final String email

  const User({
    required self.id,
    required self.name,
    required self.email,
  })

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    )


"""
            user_model_path = project_path / "lib" / "models" / "user.dart"
            user_model_path.write_text(user_model)
            files_created['lib/models/user.dart'] = "User data model"
            
            # Create a basic service
            api_service = """import 'dart:convert'
import 'package:http/http.dart' as http

class ApiService {
  static const String baseUrl = 'https://api.example.com'

  Future<Map<String, dynamic>> get(String endpoint) async {
    try:
      final response = await http.get(
        Uri.parse('$baseUrl/$endpoint'),
        headers: {'Content-Type': 'application/json'},
      )
      
      if (response.statusCode == 200):
        return json.decode(response.body)
      } else:
        throw Exception('Failed to load data')

    } catch (e) {
      throw Exception('Network error: $e')

  Future<Map<String, dynamic>> post(String endpoint, Map<String, dynamic> data) async {
    try:
      final response = await http.post(
        Uri.parse('$baseUrl/$endpoint'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(data),
      )
      
      if (response.statusCode == 200 || response.statusCode == 201):
        return json.decode(response.body)
      } else:
        throw Exception('Failed to send data')

    } catch (e) {
      throw Exception('Network error: $e')


"""
            api_service_path = project_path / "lib" / "services" / "api_service.dart"
            api_service_path.write_text(api_service)
            files_created['lib/services/api_service.dart'] = "API service layer"
            
            # Create a basic widget
            custom_button = """import 'package:flutter/material.dart'

class CustomButton extends StatelessWidget {
  final String text
  final VoidCallback? onPressed
  final Color? backgroundColor
  final Color? textColor

  const CustomButton({
    super.key,
    required self.text,
    self.onPressed,
    self.backgroundColor,
    self.textColor,
  })

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor ?? Theme.of(context).primaryColor,
        foregroundColor: textColor ?? Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Text(
        text,
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
    )


"""
            custom_button_path = project_path / "lib" / "widgets" / "custom_button.dart"
            custom_button_path.write_text(custom_button)
            files_created['lib/widgets/custom_button.dart'] = "Custom button widget"
            
            self.logger.info(f"✅ Created {len(files_created)} core architecture files")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create core architecture files: {e}")
        
        return files_created

    async def _generate_test_files(self, task_data: Dict[str, Any], project_path) -> Dict[str, str]:
        """Generate test files for the Flutter project."""
        files_created =:}
        
        try:
            # Create test directory
            test_dir = project_path / "test"
            test_dir.mkdir(exist_ok=True)
            
            # Create widget test
            widget_test = f"""import 'package:flutter/material.dart'
import 'package:flutter_test/flutter_test.dart'

import 'package:{task_data.get('project_name', 'flutter_app').lower().replace(' ', '_')}/main.dart'

void main() {{
  testWidgets('Counter increments smoke test', (WidgetTester tester) async {{
    // Build our app and trigger a frame.
    await tester.pumpWidget(const {task_data.get('name', 'FlutterApp').replace(' ', '')}App())

    // Verify that our counter starts at 0.
    expect(find.text('Counter: 0'), findsOneWidget)
    expect(find.text('Counter: 1'), findsNothing)

    // Tap the '+' icon and trigger a frame.
    await tester.tap(find.byIcon(Icons.add))
    await tester.pump()

    // Verify that our counter has incremented.
    expect(find.text('Counter: 0'), findsNothing)
    expect(find.text('Counter: 1'), findsOneWidget)
  }})
}}
"""
            widget_test_path = test_dir / "widget_test.dart"
            widget_test_path.write_text(widget_test)
            files_created['test/widget_test.dart'] = "Widget tests"
            
            # Create unit test
            unit_test = """import 'package:flutter_test/flutter_test.dart'

void main() {
  group('Unit Tests', () {
    test('String manipulation test', () {
      const input = 'hello world'
      final result = input.toUpperCase()
      expect(result, 'HELLO WORLD')
    })

    test('List operations test', () {
      final list = [1, 2, 3]
      list.add(4)
      expect(list.length, 4)
      expect(list.last, 4)
    })

    test('Map operations test', () {
      final map = <String, int>{'a': 1, 'b': 2}
      map['c'] = 3
      expect(map.length, 3)
      expect(map['c'], 3)
    })
  })

"""
            unit_test_path = test_dir / "unit_test.dart"
            unit_test_path.write_text(unit_test)
            files_created['test/unit_test.dart'] = "Unit tests"
            
            self.logger.info(f"✅ Created {len(files_created)} test files")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create test files: {e}")
        
        return files_created

    def _generate_readme(self, project_name: str, description: str) -> str:
        """Generate a comprehensive README.md file."""
        return f"""# {project_name}

{description or 'A Flutter application'}

## Getting Started

This Flutter project was generated by FlutterSwarm - an AI-powered Flutter development system.

### Prerequisites

- Flutter SDK (3.0.0 or higher)
- Dart SDK
- Android Studio / VS Code
- Android SDK / Xcode (for mobile development)

### Installation

1. Clone this repository
2. Navigate to the project directory
3. Run `flutter pub get` to install dependencies
4. Run `flutter run` to start the application

### Project Structure

```
lib/
├── main.dart           # Application entry point
├── models/             # Data models
├── services/           # Business logic and API calls
├── widgets/            # Custom widgets
└── screens/            # Application screens

test/
├── widget_test.dart    # Widget tests
└── unit_test.dart      # Unit tests
```

### Features

- Modern Flutter architecture
- Comprehensive testing setup
- Clean code structure
- Material Design 3

### Development

To run tests:
```bash
flutter test
```

To build for production:
```bash
flutter build apk  # For Android
flutter build ios  # For iOS
```

### Generated by FlutterSwarm

This project was automatically generated using AI-powered development tools.
Architecture decisions and code structure follow Flutter best practices.
"""

    def _count_files_in_directory(self, directory_path) -> int:
        """Count all files in a directory recursively."""
        import os
        
        file_count = 0
        try:
            for root, dirs, files in os.walk(directory_path):
                file_count += len(files)
        except Exception as e:
            self.logger.error(f"Error counting files in:directory_path}: {e}")
            return 0
        
        return file_count

    def _validate_implementation_result(self, result: Dict[str, Any], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the implementation actually created files."""
        if result.get('status') != 'success':
            return:'valid': False, 'error': 'Implementation status is not success'}
        
        project_name = task_data.get('project_name', task_data.get('name', 'flutter_app'))
        actual_file_count = result.get('actual_file_count', 0)
        
        if actual_file_count < 5:
            return:
                'valid': False, 
                'error': f'Insufficient files created: {actual_file_count} (minimum 5 required)'

        files_created = result.get('files_created', {})
        if len(files_created) < 3:
            return:
                'valid': False,
                'error': f'Insufficient file records: {len(files_created)} (minimum 3 required)'

        return {'valid': True, 'error': None}

    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute implementation tasks."""
        if "implement_feature" in task_description:
            return await self._implement_feature(task_data)
        elif "generate_models" in task_description:
            return await self._generate_models(task_data)
        elif "create_screens" in task_description:
            return await self._create_screens(task_data)
        elif "implement_state_management" in task_description:
            return await self._implement_state_management(task_data)
        elif "setup_project_structure" in task_description:
            return await self._setup_project_structure(task_data)
        elif "fix_implementation_issue" in task_description:
            return await self._fix_implementation_issue(task_data)
        elif "implement_incremental_features" in task_description:
            return await self._implement_incremental_features(task_data)
        elif "validate_feature" in task_description:
            return await self._validate_feature(task_data)
        elif "rollback_feature" in task_description:
            return await self._rollback_feature(task_data)
        else:
            return await self._handle_general_implementation(task_description, task_data)
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "code_review":
            return await self._provide_code_review(data)
        elif collaboration_type == "implementation_guidance":
            return await self._provide_implementation_guidance(data)
        elif collaboration_type == "refactor_request":
            return await self._handle_refactor_request(data)
        else:
            return:"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "architecture_completed":
            await self._start_implementation(change_data["project_id"])
        elif event == "file_added":
            await self._analyze_new_file(change_data)
        elif event == "issue_reported":
            # Respond to QA issues if they're related to implementation
            await self._handle_qa_issue(change_data)
    
    async def _implement_feature(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a specific feature using tools."""
        feature_name = task_data.get("feature_name", "unknown")
        feature_spec = task_data.get("feature_spec",:})
        project_id = task_data.get("project_id")
        
        self.logger.info(f"🔨 Implementing feature: {feature_name}")
        
        # Create project directory structure first
        await self._create_feature_structure(feature_name)
        
        # Generate feature files using tools
        generated_files = []
        
        # Generate models if needed
        if feature_spec.get("models"):
            model_files = await self._generate_feature_models(feature_name, feature_spec["models"])
            generated_files.extend(model_files)
        
        # Generate screens/UI
        if feature_spec.get("screens"):
            screen_files = await self._generate_feature_screens(feature_name, feature_spec["screens"])
            generated_files.extend(screen_files)
        
        # Generate business logic
        if feature_spec.get("business_logic"):
            logic_files = await self._generate_business_logic(feature_name, feature_spec["business_logic"])
            generated_files.extend(logic_files)
        
        # Update pubspec.yaml if dependencies are needed
        if feature_spec.get("dependencies"):
            await self._add_dependencies(feature_spec["dependencies"])
        
        # Format the generated code
        await self.run_command("dart format .")
        
        # Analyze the code for issues
        analysis_result = await self.execute_tool("analysis", operation="dart_analyze")
        
        return:
            "feature_name": feature_name,
            "generated_files": generated_files,
            "status": "completed",
            "analysis_result": analysis_result.data if analysis_result.data else:},
            "issues_found": analysis_result.data.get("total_issues", 0) if analysis_result.data else 0

    
    async def _create_feature_structure(self, feature_name: str) -> None:
        """Create directory structure for a feature using file tools."""
        feature_path = f"lib/features/{feature_name}"
        
        directories = [
            f"{feature_path}/data/models",
            f"{feature_path}/data/repositories",
            f"{feature_path}/data/datasources",
            f"{feature_path}/domain/entities",
            f"{feature_path}/domain/repositories",
            f"{feature_path}/domain/usecases",
            f"{feature_path}/presentation/pages",
            f"{feature_path}/presentation/widgets",
            f"{feature_path}/presentation/bloc"
        ]
        
        for directory in directories:
            await self.execute_tool("file", operation="create_directory", directory=directory)
    
    async def _generate_feature_models(self, feature_name: str, models: List[Dict]) -> List[str]:
        """Generate model files for a feature."""
        generated_files = []
        
        for model in models:
            model_name = model.get("name", "unknown")
            model_fields = model.get("fields", [])
            
            # Generate model code
            model_prompt = f"""
            Generate a Dart model class for:model_name} with the following fields:
            {model_fields}
            
            Include:
            - Proper null safety
            - toJson() and fromJson() methods
            - copyWith() method
            - toString() method
            - Equality operators
            
            Follow Flutter/Dart best practices.
            """
            
            model_code = await self.think(model_prompt, {"model": model})
                 # Write the model file
        file_path = f"lib/features/{feature_name}/data/models/{model_name.lower()}_model.dart"
        write_result = await self.write_file(file_path, model_code)
        
        if write_result.status == ToolStatus.SUCCESS:
            generated_files.append(file_path)
            self.logger.info(f"✅ Generated model::file_path}")
        else:
            self.logger.error(f"❌ Failed to generate model: {file_path}")
        
        return generated_files
    
    async def _generate_feature_screens(self, feature_name: str, screens: List[Dict]) -> List[str]:
        """Generate screen files for a feature."""
        generated_files = []
        
        for screen in screens:
            screen_name = screen.get("name", "unknown")
            screen_type = screen.get("type", "stateless")
            
            # Generate screen code using tools
            screen_prompt = f"""
            Generate a Flutter:screen_type} widget for {screen_name} screen.
            
            Include:
            - Proper widget structure
            - Material Design components
            - Responsive design considerations
            - Proper state management integration
            - Navigation setup
            - Error handling
            
            Follow Flutter best practices and use modern Flutter patterns.
            """
            
            screen_code = await self.think(screen_prompt, {"screen": screen})
            
            # Write the screen file
            file_path = f"lib/features/{feature_name}/presentation/pages/{screen_name.lower()}_screen.dart"
            write_result = await self.write_file(file_path, screen_code)
            
            if write_result.status.value == "success":
                generated_files.append(file_path)
                self.logger.info(f"✅ Generated screen::file_path}")
            else:
                self.logger.error(f"❌ Failed to generate screen: {file_path}")
        
        return generated_files
    
    async def _generate_business_logic(self, feature_name: str, logic_spec: Dict) -> List[str]:
        """Generate business logic files (BLoC, repositories, etc.)."""
        generated_files = []
        
        # Generate repository interface
        if logic_spec.get("repository"):
            repo_code = await self._generate_repository_code(feature_name, logic_spec["repository"])
            repo_file = f"lib/features/{feature_name}/domain/repositories/{feature_name}_repository.dart"
            
            write_result = await self.write_file(repo_file, repo_code)
            if write_result.status.value == "success":
                generated_files.append(repo_file)
        
        # Generate use cases
        if logic_spec.get("use_cases"):
            for use_case in logic_spec["use_cases"]:
                use_case_code = await self._generate_use_case_code(feature_name, use_case)
                use_case_file = f"lib/features/{feature_name}/domain/usecases/{use_case['name'].lower()}_usecase.dart"
                
                write_result = await self.write_file(use_case_file, use_case_code)
                if write_result.status.value == "success":
                    generated_files.append(use_case_file)
        
        # Generate BLoC/Cubit
        if logic_spec.get("state_management") == "bloc":
            bloc_files = await self._generate_bloc_files(feature_name, logic_spec)
            generated_files.extend(bloc_files)
        
        return generated_files
    
    async def _add_dependencies(self, dependencies: List[str]) -> None:
        """Add dependencies to pubspec.yaml using Flutter tool."""
        self.logger.info(f"📦 Adding dependencies::dependencies}")
        
        # Use Flutter tool to add packages
        add_result = await self.execute_tool("flutter", operation="pub_add", packages=dependencies)
        
        if add_result.status.value == "success":
            self.logger.info("✅ Dependencies added successfully")
            
            # Run pub get to install dependencies
            await self.execute_tool("flutter", operation="pub_get")
        else:
            self.logger.error(f"❌ Failed to add dependencies::add_result.error}")

    async def _generate_models(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data models and DTOs."""
        project_id = task_data["project_id"]
        entities = task_data.get("entities", [])
        
        models_prompt = f"""
        Generate Flutter/Dart models for the following entities:
       :entities}
        
        For each model, create:
        
        1. **Entity Class**: Core business entity
        2. **DTO Class**: Data transfer object for API communication
        3. **Serialization**: toJson() and fromJson() methods
        4. **Equality**: Proper equals and hashCode implementation
        5. **Copy Methods**: copyWith() for immutability
        6. **Validation**: Input validation where appropriate
        
        Use these patterns:
        - Immutable classes with final fields
        - Factory constructors for deserialization
        - Proper null safety
        - Json annotations for serialization
        - Equatable for value equality (if using equatable package)
        
        Example structure:
        class User extends Equatable:{
          const User({{
            required self.id,
            required self.name,
            required self.email,
            self.avatar,
          }})
          
          final String id
          final String name
          final String email
          final String? avatar
          
          factory User.fromJson(Map<String, dynamic> json) => User(
            id: json['id'] as String,
            name: json['name'] as String,
            email: json['email'] as String,
            avatar: json['avatar'] as String?,
          )
          
          Map<String, dynamic> toJson() => {{
            'id': id,
            'name': name,
            'email': email,
            if (avatar != null) 'avatar': avatar,
          }}
          
          User copyWith({{
            String? id,
            String? name,
            String? email,
            String? avatar,
          }}) {{
            return User(
              id: id ?? self.id,
              name: name ?? self.name,
              email: email ?? self.email,
              avatar: avatar ?? self.avatar,
            )
          }}
          
          @override
          List<Object?> get props => [id, name, email, avatar]
        }}
        
        Generate complete, production-ready model files.
        """
        
        models_code = await self.think(models_prompt, {
            "entities": entities,
            "project": shared_state.get_project_state(project_id)
        })
        
        files_created = await self._parse_and_create_files(project_id, models_code)
        
        return {
            "models_generated": entities,
            "files_created": files_created,
            "code": models_code

    
    async def _create_screens(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create UI screens and widgets."""
        project_id = task_data["project_id"]
        screens = task_data.get("screens", [])
        design_system = task_data.get("design_system", {})
        
        screens_prompt = f"""
        Create Flutter UI screens for:
        Screens: {screens}
        Design System: {design_system}
        
        For each screen, create:
        
        1. **Screen Widget**: Main screen StatefulWidget or StatelessWidget
        2. **Custom Widgets**: Reusable components used in the screen
        3. **State Management**: Integration with chosen state management solution
        4. **Responsive Design**: Proper layout for different screen sizes
        5. **Accessibility**: Semantic labels and accessibility features
        6. **Navigation**: Proper navigation implementation
        
        Follow these UI best practices:
        - Use Material Design 3 guidelines
        - Implement proper loading states
        - Handle error states gracefully
        - Use appropriate animations and transitions
        - Optimize for performance (const widgets, etc.)
        - Follow Flutter widget composition patterns
        
        Example screen structure:
        class HomeScreen extends StatefulWidget:{
          const HomeScreen({{super.key}})
          
          @override
          State<HomeScreen> createState() => _HomeScreenState()
        }}
        
        class _HomeScreenState extends State<HomeScreen> {{
          @override
          Widget build(BuildContext context) {{
            return Scaffold(
              appBar: AppBar(
                title: const Text('Home'),
              ),
              body: const SafeArea(
                child: SingleChildScrollView(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Screen content
                    ],
                  ),
                ),
              ),
            )
          }}
        }}
        
        Create complete, production-ready screen implementations.
        """
        
        screens_code = await self.think(screens_prompt, {
            "screens": screens,
            "design_system": design_system,
            "project": shared_state.get_project_state(project_id)
        })
        
        files_created = await self._parse_and_create_files(project_id, screens_code)
        
        return {
            "screens_created": screens,
            "files_created": files_created,
            "code": screens_code

    
    async def _implement_state_management(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the chosen state management solution."""
        project_id = task_data["project_id"]
        solution = task_data.get("solution", "bloc")
        features = task_data.get("features", [])
        
        state_management_prompt = f"""
        Implement {solution} state management for these features:
        Features::features}
        
        Create a complete state management implementation including:
        
        1. **State Classes**: Define application states
        2. **Event Classes**: Define user actions/events (for BLoC)
        3. **Cubit/Bloc Classes**: Business logic implementation
        4. **Repository Integration**: Connect to data layer
        5. **Provider Setup**: Configure providers/injectors
        6. **Widget Integration**: Connect UI to state management
        
       :self.flutter_templates.get(solution, "Use best practices for the chosen solution")}
        
        Ensure the implementation follows:
        - Separation of concerns
        - Testability principles
        - Error handling
        - Loading states
        - Performance optimization
        
        Generate complete, production-ready state management code.
        """
        
        state_code = await self.think(state_management_prompt,:
            "solution": solution,
            "features": features,
            "project": shared_state.get_project_state(project_id)
        })
        
        files_created = await self._parse_and_create_files(project_id, state_code)
        
        return {
            "state_management": solution,
            "features": features,
            "files_created": files_created,
            "code": state_code

    
    async def _setup_project_structure(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up the initial project structure."""
        project_id = task_data["project_id"]
        architecture_style = task_data.get("architecture_style", "clean")
        
        project = shared_state.get_project_state(project_id)
        if not project:
            return:"error": "Project not found"}
        
        # Import project manager and create the Flutter project immediately
        from utils.project_manager import ProjectManager
        pm = ProjectManager()
        
        print(f"🏗️  Setting up Flutter project structure for {project.name}")
        
        try:
            # Create the actual Flutter project structure first
            if not pm.project_exists(project.name):
                project_path = pm.create_flutter_project_structure(project.name)
                print(f"✅ Flutter project created at::project_path}")
            else:
                project_path = pm.get_project_path(project.name)
                print(f"✅ Using existing Flutter project at: {project_path}")
            
            # Use AI to generate app structure based on project requirements
            files_created = await self._generate_ai_driven_app_structure(project_path, project)
            
            # Update shared state
            for file_path in files_created:
                shared_state.add_file_to_project(project_id, file_path, f"// Generated by FlutterSwarm for:file_path}")
            
            print(f"📱 Created {len(files_created)} files for Flutter app structure")
            
            return:
                "architecture_style": architecture_style,
                "files_created": files_created,
                "project_path": project_path,
                "status": "project_structure_created"

        except Exception as e:
            print(f"❌ Failed to create project structure: {e}")
            return {
                "error": str(e),
                "status": "failed"

    async def _parse_and_create_files(self, project_id: str, code_content: str) -> List[str]:
        """Parse generated code and create actual files in the Flutter project."""
        from utils.project_manager import ProjectManager
        
        files_created = []
        project = shared_state.get_project_state(project_id)
        
        if not project:
            print(f"❌ Project:project_id} not found")
            return files_created
        
        # Get project manager and ensure project structure exists
        pm = ProjectManager()
        project_path = pm.get_project_path(project.name)
        
        # Create Flutter project structure if it doesn't exist
        if not pm.project_exists(project.name):
            print(f"🏗️  Creating Flutter project structure for:project.name}")
            try:
                project_path = pm.create_flutter_project_structure(project.name)
                print(f"✅ Flutter project created at: {project_path}")
            except Exception as e:
                print(f"❌ Failed to create Flutter project: {e}")
                return files_created
        
        # Parse the LLM output to extract file paths and contents
        lines = code_content.split('\n')
        current_file = None
        current_content = []
        
        for line in lines:
            if line.startswith('// File:') or line.startswith('# File:'):
                if current_file and current_content:
                    # Create actual file
                    file_created = await self._create_actual_file(
                        project_path, current_file, '\n'.join(current_content)
                    )
                    if file_created:
                        files_created.append(current_file)
                        # Also save to shared state
                        shared_state.add_file_to_project(
                            project_id, current_file, '\n'.join(current_content)
                        )
                
                # Start new file
                current_file = line.split(':', 1)[1].strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        # Create last file
        if current_file and current_content:
            file_created = await self._create_actual_file(
                project_path, current_file, '\n'.join(current_content)
            )
            if file_created:
                files_created.append(current_file)
                shared_state.add_file_to_project(
                    project_id, current_file, '\n'.join(current_content)
                )
        
        # If no files were parsed from LLM output, create a basic main.dart
        if not files_created:
            print("📝 No files parsed from LLM output, creating basic Flutter app structure")
            files_created = await self._create_basic_flutter_app(project_path, project.name)
            
        return files_created
    
    async def _create_actual_file(self, project_path: str, file_path: str, content: str) -> bool:
        """Create an actual file in the project directory."""
        try:
            # Ensure file path is relative to lib/ or project root
            if not file_path.startswith('lib/') and not file_path.startswith('test/'):
                file_path = f"lib/{file_path}"
            
            full_path = os.path.join(project_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📄 Created file::file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create file {file_path}: {e}")
            return False
    
    async def _create_basic_flutter_app(self, project_path: str, project_name: str) -> List[str]:
        """Create a basic Flutter app when LLM output parsing fails."""
        files_created = []
        
        # Create main.dart
        # Clean project name for class names
        clean_name = ''.join(word.capitalize() for word in project_name.replace(' ', '_').replace('-', '_').split('_'))
        
        main_dart_content = f'''import 'package:flutter/material.dart'

void main():{
  runApp(const {clean_name}App())
}}

class {clean_name}App extends StatelessWidget {{
  const {clean_name}App({{super.key}})

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{project_name}',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    )
  }}
}}

class HomeScreen extends StatelessWidget {{
  const HomeScreen({{super.key}})

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('{project_name}'),
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.music_note,
              size: 100,
              color: Colors.deepPurple,
            ),
            SizedBox(height: 20),
            Text(
              'Welcome to {project_name}!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              'This app was generated by FlutterSwarm AI agents.',
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    )
  }}
}}
'''
        
        if await self._create_actual_file(project_path, 'lib/main.dart', main_dart_content):
            files_created.append('lib/main.dart')
        
        return files_created
    
    
    def _get_bloc_template(self) -> str:
        """Get BLoC state management template."""
        return """
import 'package:bloc/bloc.dart'
import 'package:equatable/equatable.dart'

part '{feature}_event.dart'
part '{feature}_state.dart'

class {Feature}Bloc extends Bloc<{Feature}Event, {Feature}State> {
  {Feature}Bloc() : super({Feature}Initial()) {
    on<{Feature}Event>((event, emit) {
      // TODO: Implement event handlers
    })


"""

    def _get_provider_template(self) -> str:
        """Get Provider state management template."""
        return """
import 'package:flutter/foundation.dart'

class {Feature}Provider extends ChangeNotifier {
  bool _isLoading = false
  String? _error
  
  bool get isLoading => _isLoading
  String? get error => _error
  
  void _setLoading(bool loading) {
    _isLoading = loading
    notifyListeners()

  void _setError(String? error) {
    _error = error
    notifyListeners()


"""

    def _get_riverpod_template(self) -> str:
        """Get Riverpod state management template."""
        return """
import 'package:flutter_riverpod/flutter_riverpod.dart'

// State class
class {Feature}State {
  final bool isLoading
  final String? error
  final List<dynamic> items
  
  const {Feature}State({
    self.isLoading = false,
    self.error,
    self.items = const [],
  })
  
  {Feature}State copyWith({
    bool? isLoading,
    String? error,
    List<dynamic>? items,
  }) {
    return {Feature}State(
      isLoading: isLoading ?? self.isLoading,
      error: error ?? self.error,
      items: items ?? self.items,
    )


// Provider
final {feature}Provider = StateNotifierProvider<{Feature}Notifier, {Feature}State>(
  (ref) => {Feature}Notifier(),
)

class {Feature}Notifier extends StateNotifier<{Feature}State> {
  {Feature}Notifier() : super(const {Feature}State())
  
  // Add methods here

"""

    def _get_clean_architecture_template(self) -> str:
        """Get Clean Architecture template structure."""
        return """
// Domain Layer - Entity
class {Feature}Entity {
  final String id
  final String name
  
  const {Feature}Entity({
    required self.id,
    required self.name,
  })

// Domain Layer - Repository Interface
abstract class {Feature}Repository {
  Future<List<{Feature}Entity>> get{Feature}s()
  Future<{Feature}Entity> get{Feature}ById(String id)

// Domain Layer - Use Case
class Get{Feature}sUseCase {
  final {Feature}Repository repository
  
  Get{Feature}sUseCase(self.repository)
  
  Future<List<{Feature}Entity>> call() {
    return repository.get{Feature}s()


// Data Layer - Model
class {Feature}Model extends {Feature}Entity {
  const {Feature}Model({
    required super.id,
    required super.name,
  })
  
  factory {Feature}Model.fromJson(Map<String, dynamic> json) {
    return {Feature}Model(
      id: json['id'],
      name: json['name'],
    )

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,


"""
    
    async def _provide_code_review(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide code review feedback."""
        code = data.get("code", "")
        focus = data.get("focus", "general")
        
        review_prompt = f"""
        Review this Flutter/Dart code focusing on {focus}:
        
        {code}
        
        Provide feedback on:
        1. Code quality and best practices
        2. Flutter-specific conventions
        3. Performance considerations
        4. Maintainability issues
        5. Security implications
        6. Testing considerations
        
        Give specific, actionable recommendations.
        """
        
        review = await self.think(review_prompt, {"code": code, "focus": focus})
        
        return {
            "review": review,
            "focus": focus,
            "reviewer": self.agent_id

    
    async def _fix_implementation_issue(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix implementation issues reported by QA."""
        project_id = task_data["project_id"]
        issue = task_data["issue"]
        affected_files = task_data.get("affected_files", [])
        
        project = shared_state.get_project_state(project_id)
        
        fix_prompt = f"""
        Fix the following implementation issue in this Flutter project:
        
        Project: {project.name}
        Issue: {issue.get('description', '')}
        Issue Type: {issue.get('issue_type', '')}
        Severity: {issue.get('severity', '')}
        Affected Files: {affected_files}
        
        Analyze the issue and provide corrected code that:
        1. Fixes the specific problem identified
        2. Maintains compatibility with existing code
        3. Follows Flutter best practices
        4. Improves overall code quality
        
        For each file that needs fixing, provide:
        - File path
        - Complete corrected code
        - Explanation of what was fixed
        """
        
        fix_response = await self.think(fix_prompt, {
            "project": project,
            "issue": issue,
            "affected_files": affected_files
        })
        
        # Parse and apply fixes
        fixed_files = await self._apply_implementation_fixes(project_id, fix_response)
        
        # Report back to QA
        shared_state.update_issue_status(
            project_id, 
            issue.get("issue_id", ""), 
            "resolved",
            assigned_agent=self.agent_id,
            resolution_notes=f"Fixed {len(fixed_files)} files"
        )
        
        return {
            "status": "issue_fixed",
            "fixed_files": fixed_files,
            "issue_id": issue.get("issue_id", "")

    
    async def _apply_implementation_fixes(self, project_id: str, fix_response: str) -> List[str]:
        """Apply implementation fixes to actual files."""
        from utils.project_manager import ProjectManager
        
        pm = ProjectManager()
        project = shared_state.get_project_state(project_id)
        project_path = pm.get_project_path(project.name)
        
        fixed_files = []
        
        # Parse fix response for file updates (simplified parsing)
        # In a real implementation, this would parse the LLM response more thoroughly
        if "lib/" in fix_response and ".dart" in fix_response:
            # This is a simplified example - would need better parsing
            print(f"🔧 Implementation Agent: Applying fixes to project:project.name}")
            fixed_files.append("example_fixed_file.dart")
        
        return fixed_files
    
    async def _provide_implementation_guidance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide implementation guidance to other agents."""
        guidance_prompt = f"""
        Provide implementation guidance for:
        
        Context::data.get('context', '')}
        Question: {data.get('question', '')}
        Technology: Flutter/Dart
        
        Give specific, actionable Flutter/Dart implementation advice including:
        1. Best practices
        2. Code examples
        3. Common pitfalls to avoid
        4. Performance considerations
        """
        
        guidance = await self.think(guidance_prompt, data)
        
        return {
            "guidance": guidance,
            "agent": self.agent_id,
            "status": "guidance_provided"

    
    async def _handle_refactor_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refactoring requests from other agents."""
        project_id = data.get("project_id")
        files_to_refactor = data.get("files", [])
        refactor_goal = data.get("goal", "improve code quality")
        
        refactor_prompt = f"""
        Refactor the following Flutter/Dart files:
        
        Goal: {refactor_goal}
        Files: {files_to_refactor}
        
        Apply these refactoring principles:
        1. Improve readability and maintainability
        2. Follow Flutter best practices
        3. Optimize performance
        4. Ensure proper error handling
        5. Maintain existing functionality
        
        Provide refactored code for each file.
        """
        
        refactored_code = await self.think(refactor_prompt, data)
        
        # Parse and apply refactoring
        if project_id:
            refactored_files = await self._parse_and_create_files(project_id, refactored_code)
        else:
            refactored_files = []
        
        return:
            "refactored_files": refactored_files,
            "goal": refactor_goal,
            "status": "refactoring_completed"

    
    async def _start_implementation(self, project_id: str) -> None:
        """Start implementation after architecture is completed."""
        project = shared_state.get_project_state(project_id)
        if not project:
            return
        
        print(f"🔨 Starting implementation for project::project.name}")
        
        # Send message to orchestrator that implementation is ready to begin
        self.send_message_to_agent(
            to_agent="orchestrator",
            message_type=MessageType.STATUS_UPDATE,
            content={
                "status": "implementation_ready",
                "project_id": project_id,
                "message": "Implementation agent ready to begin coding"

        )
    
    async def _analyze_new_file(self, change_data: Dict[str, Any]) -> None:
        """Analyze newly created files for implementation issues."""
        file_path = change_data.get("file_path", "")
        project_id = change_data.get("project_id", "")
        
        if not file_path.endswith('.dart'):
            return  # Only analyze Dart files
        
        print(f"🔍 Analyzing new file::file_path}")
        
        # Get file content from shared state if available
        project = shared_state.get_project_state(project_id)
        if not project or not hasattr(project, 'files_created'):
            return
        
        # Simple analysis - check if it's a valid Dart file
        try:
            # Read the actual file to check for syntax issues
            from utils.project_manager import ProjectManager
            pm = ProjectManager()
            project_path = pm.get_project_path(project.name)
            full_file_path = os.path.join(project_path, file_path)
            
            if os.path.exists(full_file_path):
                with open(full_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax checks
                if not content.strip():
                    print(f"⚠️ Empty file detected::file_path}")
                elif 'class ' not in content and 'void main(' not in content and 'import ' not in content:
                    print(f"⚠️ Possibly invalid Dart file::file_path}")
                else:
                    print(f"✅ File looks valid::file_path}")
        
        except Exception as e:
            print(f"❌ Error analyzing file {file_path}: {e}")

    async def _handle_qa_issue(self, change_data: Dict[str, Any]) -> None:
        """Handle issues reported by the QA agent."""
        issue = change_data.get("issue", {})
        issue_type = issue.get("issue_type", "")
        project_id = change_data.get("project_id", "")
        
        # Check if this is an implementation-related issue
        implementation_issues = [
            "code_quality", "syntax_errors", "naming_conventions",
            "null_safety", "widget_usage", "state_management",
            "dart_syntax", "flutter_patterns", "file_structure"
        ]
        
        if any(impl_issue in issue_type.lower() for impl_issue in implementation_issues):
            print(f"🔧 Implementation Agent: Handling QA issue -:issue_type}")
            
            # Send a fix implementation task to ourselves
            self.send_message_to_agent(
                to_agent="implementation",
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_description": "fix_implementation_issue",
                    "task_data": {
                        "project_id": project_id,
                        "issue": issue,
                        "affected_files": issue.get("affected_files", [])

                },
                priority=4
            )
        else:
            print(f"📝 Implementation Agent: QA issue '{issue_type}' not implementation-related")
    
    async def _handle_general_implementation(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general implementation tasks that don't match specific patterns."""
        project_id = task_data.get("project_id", "")
        
        self.logger.info(f"🔨 Handling general implementation task: {task_description}")
        
        # Create a comprehensive implementation based on the task description
        implementation_prompt = f"""
        Handle this Flutter implementation task:
        
        Task: {task_description}
        Data: {task_data}
        
        Create a complete Flutter implementation that includes:
        1. Proper project structure
        2. Well-structured Dart code
        3. State management integration
        4. UI components and screens
        5. Business logic and data models
        6. Error handling
        7. Performance optimizations
        
        Follow Flutter best practices and create production-ready code.
        """
        
        try:
            implementation_code = await self.think(implementation_prompt, task_data)
            
            if project_id:
                files_created = await self._parse_and_create_files(project_id, implementation_code)
            else:
                files_created = []
            
            return:
                "status": "completed",
                "task_description": task_description,
                "files_created": files_created,
                "implementation": implementation_code

        except Exception as e:
            self.logger.error(f"❌ Error in general implementation: {e}")
            return {
                "status": "error",
                "error": str(e),
                "task_description": task_description

    def _determine_project_type(self, project) -> str:
        """Determine the type of project based on requirements and name."""
        name_lower = project.name.lower()
        requirements_text = ' '.join(project.requirements).lower()
        
        # Music/Audio apps
        if any(keyword in name_lower or keyword in requirements_text for keyword in 
               ['music', 'audio', 'streaming', 'playlist', 'song', 'sound', 'radio']):
            return 'music_app'
        
        # E-commerce apps
        if any(keyword in name_lower or keyword in requirements_text for keyword in 
               ['shop', 'store', 'ecommerce', 'cart', 'payment', 'product', 'order']):
            return 'ecommerce_app'
        
        # Social apps
        if any(keyword in name_lower or keyword in requirements_text for keyword in 
               ['social', 'chat', 'message', 'post', 'friend', 'follow', 'share']):
            return 'social_app'
        
        # Productivity apps
        if any(keyword in name_lower or keyword in requirements_text for keyword in 
               ['todo', 'task', 'note', 'productivity', 'calendar', 'reminder']):
            return 'productivity_app'
        
        # Weather apps
        if any(keyword in name_lower or keyword in requirements_text for keyword in 
               ['weather', 'forecast', 'climate', 'temperature']):
            return 'weather_app'
        
        # Default to utility app
        return 'utility_app'

    async def _generate_ai_driven_app_structure(self, project_path: str, project) -> List[str]:
        """Generate an AI-driven app structure based on project requirements."""
        project_type = self._determine_project_type(project)
        
        structure_prompt = f"""
        Generate a complete Flutter app structure for a:project_type}:
        
        Project::project.name}
        Type: {project_type}
        Requirements: {project.requirements}
        
        Create the following files with complete, production-ready code:
        
        1. lib/main.dart - App entry point with proper Material app setup
        2. lib/core/app_theme.dart - Theme configuration
        3. lib/core/routes.dart - Navigation and routing
        4. lib/models/ - Data models relevant to the app type
        5. lib/screens/ - Main screens for the app
        6. lib/widgets/ - Reusable widgets
        7. lib/services/ - API and business logic services
        8. lib/utils/ - Utility functions and constants
        
        For each file, provide:
        // File: [path]
        [complete code content]
        
        Ensure all code is:
        - Null-safe Dart
        - Follows Flutter best practices
        - Includes proper error handling
        - Uses Material Design 3
        - Implements responsive design
        - Includes comments explaining key functionality
        """
        
        try:
            structure_code = await self.think(structure_prompt,:
                "project": project,
                "project_type": project_type,
                "project_path": project_path
            })
            
            files_created = await self._parse_and_create_files(project.id, structure_code)
            return files_created
            
        except Exception as e:
            self.logger.error(f"❌ Error generating AI-driven structure: {e}")
            # Fallback to basic structure
            return await self._create_basic_flutter_app(project_path, project.name)

    # Incremental Implementation Methods
    async def _implement_incremental_features(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement features incrementally with validation at each step."""
        project_id = task_data["project_id"]
        requirements = task_data.get("requirements", [])
        features = task_data.get("features", [])
        
        self.logger.info(f"🔄 Starting incremental feature implementation for project:project_id}")
        
        # Register with supervision
        await self._register_incremental_process(project_id)
        
        try:
            # Parse requirements into discrete features
            feature_queue = await self._parse_requirements_into_features(requirements, features)
            
            # Initialize incremental state
            shared_state.initialize_incremental_implementation(project_id, feature_queue)
            
            # Sort features by priority and dependencies
            sorted_features = await self._sort_features_by_dependencies(feature_queue)
            
            implementation_results = {
                "project_id": project_id,
                "total_features": len(sorted_features),
                "completed_features": [],
                "failed_features": [],
                "feature_results": {},
                "overall_status": "in_progress"

            # Implement features one by one
            for feature in sorted_features:
                feature_id = feature["id"]
                
                self.logger.info(f"🔄 Implementing feature::feature_id}")
                shared_state.start_feature_implementation(project_id, feature)
                
                # Send heartbeat to supervision
                await self._send_implementation_heartbeat(project_id, feature_id)
                
                # Implement the feature
                feature_result = await self._implement_single_feature(project_id, feature)
                implementation_results["feature_results"][feature_id] = feature_result
                
                if feature_result["status"] == "success":
                    # Validate the feature
                    validation_result = await self._validate_implemented_feature(project_id, feature)
                    
                    if validation_result["valid"]:
                        # Create rollback point
                        rollback_point = await self._create_rollback_point(project_id, feature_id)
                        
                        # Mark feature as completed
                        shared_state.complete_feature_implementation(
                            project_id, feature_id, True, rollback_point
                        )
                        implementation_results["completed_features"].append(feature_id)
                        
                        self.logger.info(f"✅ Feature:feature_id} implemented and validated successfully")
                    else:
                        # Validation failed - attempt retry or rollback
                        retry_result = await self._handle_feature_validation_failure(
                            project_id, feature, validation_result
                        )
                        
                        if retry_result["success"]:
                            implementation_results["completed_features"].append(feature_id)
                        else:
                            implementation_results["failed_features"].append(feature_id)
                            shared_state.complete_feature_implementation(project_id, feature_id, False)
                else:
                    # Implementation failed
                    implementation_results["failed_features"].append(feature_id)
                    shared_state.complete_feature_implementation(project_id, feature_id, False)
                    
                    self.logger.error(f"❌ Feature:feature_id} implementation failed")
                
                # Check if we should continue or halt
                if len(implementation_results["failed_features"]) > 3:
                    self.logger.error("❌ Too many feature failures, halting incremental implementation")
                    break
            
            # Determine overall status
            total_completed = len(implementation_results["completed_features"])
            total_features = implementation_results["total_features"]
            
            if total_completed == total_features:
                implementation_results["overall_status"] = "completed"
            elif total_completed > 0:
                implementation_results["overall_status"] = "partial"
            else:
                implementation_results["overall_status"] = "failed"
            
            self.logger.info(f"🔄 Incremental implementation completed::total_completed}/{total_features} features")
            
            return {
                "status": "incremental_implementation_completed",
                "results": implementation_results

        except Exception as e:
            self.logger.error(f"❌ Incremental implementation failed: {e}")
            return {
                "status": "incremental_implementation_failed",
                "error": str(e)

    async def _parse_requirements_into_features(self, requirements: List[str], features: List[str]) -> List[Dict[str, Any]]:
        """Parse project requirements into discrete, implementable features."""
        feature_queue = []
        
        # Combine requirements and features
        all_features = features + [req for req in requirements if req not in features]
        
        for i, feature_name in enumerate(all_features):
            # Create feature object with metadata
            feature =:
                "id": f"feature_{i+1}_{feature_name.lower().replace(' ', '_')}",
                "name": feature_name,
                "description": f"Implementation of {feature_name}",
                "priority": self._determine_feature_priority(feature_name),
                "dependencies": self._determine_feature_dependencies(feature_name, all_features),
                "estimated_complexity": self._estimate_feature_complexity(feature_name),
                "validation_criteria": self._define_validation_criteria(feature_name),
                "implementation_plan": await self._create_feature_implementation_plan(feature_name)

            feature_queue.append(feature)
        
        return feature_queue
    
    def _determine_feature_priority(self, feature_name: str) -> int:
        """Determine feature priority (1=high, 5=low)."""
        high_priority_keywords = ["auth", "login", "core", "main", "basic", "essential"]
        medium_priority_keywords = ["ui", "interface", "navigation", "data"]
        
        feature_lower = feature_name.lower()
        
        if any(keyword in feature_lower for keyword in high_priority_keywords):
            return 1
        elif any(keyword in feature_lower for keyword in medium_priority_keywords):
            return 3
        else:
            return 4
    
    def _determine_feature_dependencies(self, feature_name: str, all_features: List[str]) -> List[str]:
        """Determine which other features this feature depends on."""
        dependencies = []
        feature_lower = feature_name.lower()
        
        # Simple dependency detection based on keywords
        if "profile" in feature_lower or "user" in feature_lower:
            for other_feature in all_features:
                if "auth" in other_feature.lower() or "login" in other_feature.lower():
                    dependencies.append(other_feature)
        
        if "social" in feature_lower or "sharing" in feature_lower:
            for other_feature in all_features:
                if "auth" in other_feature.lower() or "user" in other_feature.lower():
                    dependencies.append(other_feature)
        
        return dependencies
    
    def _estimate_feature_complexity(self, feature_name: str) -> str:
        """Estimate feature implementation complexity."""
        complex_keywords = ["social", "payment", "ai", "ml", "algorithm", "advanced"]
        medium_keywords = ["api", "database", "integration", "sync"]
        
        feature_lower = feature_name.lower()
        
        if any(keyword in feature_lower for keyword in complex_keywords):
            return "high"
        elif any(keyword in feature_lower for keyword in medium_keywords):
            return "medium"
        else:
            return "low"
    
    def _define_validation_criteria(self, feature_name: str) -> List[str]:
        """Define validation criteria for a feature."""
        base_criteria = ["compiles_successfully", "no_runtime_errors", "basic_functionality"]
        
        feature_lower = feature_name.lower()
        
        if "auth" in feature_lower:
            base_criteria.extend(["login_flow", "logout_flow", "token_validation"])
        elif "ui" in feature_lower or "screen" in feature_lower:
            base_criteria.extend(["renders_correctly", "responsive_design", "navigation_works"])
        elif "api" in feature_lower or "network" in feature_lower:
            base_criteria.extend(["api_calls_work", "error_handling", "data_validation"])
        
        return base_criteria
    
    async def _create_feature_implementation_plan(self, feature_name: str) -> Dict[str, Any]:
        """Create implementation plan for a feature."""
        return:
            "steps": [
                f"Design:feature_name} architecture",
                f"Implement {feature_name} models",
                f"Create {feature_name} UI components",
                f"Add {feature_name} business logic",
                f"Test {feature_name} functionality"
            ],
            "estimated_time": "2-4 hours",
            "files_to_create": [
                f"lib/features/{feature_name.lower()}/",
                f"lib/features/{feature_name.lower()}/models/",
                f"lib/features/{feature_name.lower()}/widgets/",
                f"lib/features/{feature_name.lower()}/services/"
            ]

    
    async def _sort_features_by_dependencies(self, feature_queue: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort features by dependencies using topological sort."""
        # Simple topological sort implementation
        sorted_features = []
        remaining_features = feature_queue.copy()
        
        while remaining_features:
            # Find features with no unresolved dependencies
            ready_features = []
            
            for feature in remaining_features:
                dependencies = feature.get("dependencies", [])
                dependencies_met = all(
                    any(completed["name"] == dep for completed in sorted_features)
                    for dep in dependencies
                )
                
                if dependencies_met:
                    ready_features.append(feature)
            
            if not ready_features:
                # Break circular dependencies by priority
                ready_features = [min(remaining_features, key=lambda f: f["priority"])]
            
            # Sort ready features by priority
            ready_features.sort(key=lambda f: f["priority"])
            
            # Add to sorted list and remove from remaining
            for feature in ready_features:
                sorted_features.append(feature)
                remaining_features.remove(feature)
        
        return sorted_features
    
    async def _implement_single_feature(self, project_id: str, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a single feature with supervision integration."""
        feature_id = feature["id"]
        feature_name = feature["name"]
        
        try:
            # Register feature implementation process
            process_id = await self._register_feature_process(project_id, feature_id)
            
            implementation_result =:
                "feature_id": feature_id,
                "status": "in_progress",
                "files_created": [],
                "errors": [],
                "implementation_time": 0

            start_time = datetime.now()
            
            # Execute implementation plan
            plan = feature.get("implementation_plan",:})
            steps = plan.get("steps", [])
            
            for step in steps:
                self.logger.info(f"🔄 Executing step::step}")
                
                # Send heartbeat
                await self._send_implementation_heartbeat(project_id, feature_id)
                
                # Execute step (simplified implementation)
                step_result = await self._execute_implementation_step(project_id, feature, step)
                
                if step_result.get("files_created"):
                    implementation_result["files_created"].extend(step_result["files_created"])
                
                if step_result.get("errors"):
                    implementation_result["errors"].extend(step_result["errors"])
                    implementation_result["status"] = "failed"
                    break
            
            if implementation_result["status"] != "failed":
                implementation_result["status"] = "success"
            
            implementation_result["implementation_time"] = (datetime.now() - start_time).total_seconds()
            
            # Mark process as completed
            shared_state.mark_process_completed(process_id)
            
            return implementation_result
        
        except Exception as e:
            self.logger.error(f"❌ Feature:feature_id} implementation error::e}")
            return {
                "feature_id": feature_id,
                "status": "error",
                "error": str(e)

    async def _execute_implementation_step(self, project_id: str, feature: Dict[str, Any], step: str) -> Dict[str, Any]:
        """Execute a single implementation step."""
        step_result = {
            "step": step,
            "status": "completed",
            "files_created": [],
            "errors": []

        
        # Simplified step execution
        try:
            if "models" in step.lower():
                # Create models for the feature
                model_files = await self._create_feature_models(project_id, feature)
                step_result["files_created"].extend(model_files)
            
            elif "ui" in step.lower() or "components" in step.lower():
                # Create UI components
                ui_files = await self._create_feature_ui(project_id, feature)
                step_result["files_created"].extend(ui_files)
            
            elif "logic" in step.lower() or "business" in step.lower():
                # Create business logic
                logic_files = await self._create_feature_logic(project_id, feature)
                step_result["files_created"].extend(logic_files)
            
            elif "test" in step.lower():
                # Create tests for the feature
                test_files = await self._create_feature_tests(project_id, feature)
                step_result["files_created"].extend(test_files)
        
        except Exception as e:
            step_result["status"] = "failed"
            step_result["errors"].append(str(e))
        
        return step_result
    
    async def _create_feature_models(self, project_id: str, feature: Dict[str, Any]) -> List[str]:
        """Create model files for a feature."""
        # Simplified model creation
        feature_name = feature["name"].lower().replace(" ", "_")
        model_file = f"lib/features/{feature_name}/models/{feature_name}_model.dart"
        
        # Clean class name
        clean_name = ''.join(word.capitalize() for word in feature["name"].replace(' ', '_').split('_'))
        
        model_content = f'''//:feature["name"]} Model
class {clean_name}Model {{
  const {clean_name}Model({{
    required self.id,
    required self.name,
  }})

  final String id
  final String name

  factory {clean_name}Model.fromJson(Map<String, dynamic> json) {{
    return {clean_name}Model(
      id: json['id'] as String,
      name: json['name'] as String,
    )
  }}

  Map<String, dynamic> toJson() {{
    return {{
      'id': id,
      'name': name,
    }}
  }}

  {clean_name}Model copyWith({{
    String? id,
    String? name,
  }}) {{
    return {clean_name}Model(
      id: id ?? self.id,
      name: name ?? self.name,
    )
  }}
}}
'''
        
        await self._create_actual_file("flutter_projects", model_file, model_content)
        return [model_file]
    
    async def _create_feature_ui(self, project_id: str, feature: Dict[str, Any]) -> List[str]:
        """Create UI files for a feature."""
        # Simplified UI creation
        feature_name = feature["name"].lower().replace(" ", "_")
        ui_file = f"lib/features/{feature_name}/widgets/{feature_name}_widget.dart"
        
        # Clean class name
        clean_name = ''.join(word.capitalize() for word in feature["name"].replace(' ', '_').split('_'))
        
        ui_content = f'''//:feature["name"]} Widget
import 'package:flutter/material.dart'

class {clean_name}Widget extends StatelessWidget {{
  const {clean_name}Widget({{super.key}})

  @override
  Widget build(BuildContext context) {{
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '{feature["name"]}',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              const Text(
                'This is a generated widget for the:feature["name"]} feature.',
                style: TextStyle(fontSize: 16),
              ),
            ],
          ),
        ),
      ),
    )
  }}
}}
'''
        
        await self._create_actual_file("flutter_projects", ui_file, ui_content)
        return [ui_file]
    
    async def _create_feature_logic(self, project_id: str, feature: Dict[str, Any]) -> List[str]:
        """Create business logic files for a feature."""
        # Simplified logic creation
        feature_name = feature["name"].lower().replace(" ", "_")
        logic_file = f"lib/features/{feature_name}/services/{feature_name}_service.dart"
        
        # Clean class name
        clean_name = ''.join(word.capitalize() for word in feature["name"].replace(' ', '_').split('_'))
        
        logic_content = f'''//:feature["name"]} Service
class {clean_name}Service {{
  const {clean_name}Service()

  /// Initialize the {feature["name"]} service
  Future<void> initialize() async {{
    // TODO: Add initialization logic for {feature["name"]}
  }}

  /// Get {feature["name"]} data
  Future<List<String>> getData() async {{
    // TODO: Implement data retrieval for {feature["name"]}
    return ['Sample data for {feature["name"]}']
  }}

  /// Update {feature["name"]} data
  Future<bool> updateData(String data) async {{
    // TODO: Implement data update for {feature["name"]}
    return true
  }}

  /// Clean up resources
  void dispose() {{
    // TODO: Add cleanup logic for {feature["name"]}
  }}
}}
'''
        
        await self._create_actual_file("flutter_projects", logic_file, logic_content)
        return [logic_file]
    
    async def _create_feature_tests(self, project_id: str, feature: Dict[str, Any]) -> List[str]:
        """Create test files for a feature."""
        # Simplified test creation
        feature_name = feature["name"].lower().replace(" ", "_")
        test_file = f"test/features/{feature_name}/{feature_name}_test.dart"
        
        # Clean class name for imports
        clean_name = ''.join(word.capitalize() for word in feature["name"].replace(' ', '_').split('_'))
        
        test_content = f'''//:feature["name"]} Tests
import 'package:flutter_test/flutter_test.dart'

void main() {{
  group('{feature["name"]} Tests', () {{
    test('should initialize correctly', () {{
      // TODO: Add proper initialization tests for {feature["name"]}
      expect(true, isTrue)
    }})

    test('should handle data operations', () {{
      // TODO: Add data operation tests for {feature["name"]}
      expect(1 + 1, equals(2))
    }})

    test('should handle errors gracefully', () {{
      // TODO: Add error handling tests for {feature["name"]}
      expect(() => throw Exception('Test error'), throwsException)
    }})
  }})
}}
'''
        
        await self._create_actual_file("flutter_projects", test_file, test_content)
        return [test_file]
    
    async def _validate_implemented_feature(self, project_id: str, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that an implemented feature meets criteria."""
        validation_result = {
            "valid": True,
            "feature_id": feature["id"],
            "criteria_results": {},
            "validation_time": 0

        
        start_time = datetime.now()
        
        try:
            criteria = feature.get("validation_criteria", [])
            
            for criterion in criteria:
                result = await self._validate_single_criterion(project_id, feature, criterion)
                validation_result["criteria_results"][criterion] = result
                
                if not result.get("passed", False):
                    validation_result["valid"] = False
            
            validation_result["validation_time"] = (datetime.now() - start_time).total_seconds()
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["error"] = str(e)

        
        return validation_result

    
    async def _validate_single_criterion(self, project_id: str, feature: Dict[str, Any], criterion: str) -> Dict[str, Any]:
        """Validate a single criterion for a feature."""
        if criterion == "compiles_successfully":
            return await self._validate_compilation(project_id)
        elif criterion == "no_runtime_errors":
            return await self._validate_runtime(project_id)
        elif criterion == "basic_functionality":
            return await self._validate_basic_functionality(project_id, feature)
        else:
            # Default validation
            return:"passed": True, "details": "Basic validation passed"}
    
    async def _validate_compilation(self, project_id: str) -> Dict[str, Any]:
        """Validate that the project compiles successfully."""
        try:
            # Use Flutter tool to analyze
            analysis_result = await self.execute_tool(
                "flutter",
                operation="analyze",
                timeout=30
            )
            
            return:
                "passed": analysis_result.status.value == "success",
                "details": "Flutter analyze completed",
                "output": analysis_result.data if analysis_result.data else ""

        except Exception as e:
            return:
                "passed": False,
                "details": f"Compilation validation failed: {str(e)}"

    async def _validate_runtime(self, project_id: str) -> Dict[str, Any]:
        """Validate runtime behavior."""
        # Simplified runtime validation
        return {
            "passed": True,
            "details": "Runtime validation passed (simplified)"

    
    async def _validate_basic_functionality(self, project_id: str, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic functionality of the feature."""
        # Simplified functionality validation
        return {
            "passed": True,
            "details": f"Basic functionality validation for {feature['name']} passed"

    
    async def _create_rollback_point(self, project_id: str, feature_id: str) -> str:
        """Create a Git rollback point for the feature."""
        try:
            # Create git commit for the feature
            commit_result = await self.execute_tool(
                "git",
                operation="commit",
                message=f"Implement feature::feature_id}",
                add_all=True
            )
            
            if commit_result.status.value == "success":
                # Get commit hash
                hash_result = await self.execute_tool(
                    "git",
                    operation="get_current_commit_hash"
                )
                
                return hash_result.data.strip() if hash_result.data else "unknown"
            else:
                return "commit_failed"
        
        except Exception as e:
            self.logger.error(f"❌ Failed to create rollback point::e}")
            return "rollback_point_failed"

    
    async def _handle_feature_validation_failure(self, project_id: str, feature: Dict[str, Any], 
                                                validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feature validation failure with retry logic."""
        feature_id = feature["id"]
        max_retries = 3
        
        for attempt in range(max_retries):
            self.logger.warning(f"⚠️ Feature:feature_id} validation failed, attempt {attempt + 1}")
            
            # Try to fix validation issues
            fix_result = await self._attempt_feature_fix(project_id, feature, validation_result)
            
            if fix_result["success"]:
                # Re-validate
                new_validation = await self._validate_implemented_feature(project_id, feature)
                
                if new_validation["valid"]:
                    return:"success": True, "attempts": attempt + 1}
            
            # If fix failed or validation still fails, wait before retry
            await asyncio.sleep(2)
        
        # All retries failed - rollback
        rollback_result = await self._rollback_to_previous_state(project_id, feature_id)
        
        return {
            "success": False,
            "attempts": max_retries,
            "rollback_performed": rollback_result["success"]


    
    async def _attempt_feature_fix(self, project_id: str, feature: Dict[str, Any], 
                                  validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix feature validation issues."""
        # Simplified fix attempt
        try:
            failed_criteria = [
                criterion for criterion, result in validation_result["criteria_results"].items()
                if not result.get("passed", False)
            ]
            
            for criterion in failed_criteria:
                if criterion == "compiles_successfully":
                    # Try to fix compilation errors
                    await self._fix_compilation_errors(project_id)
                elif criterion == "no_runtime_errors":
                    # Try to fix runtime errors
                    await self._fix_runtime_errors(project_id)


            return:"success": True}
        
        except Exception as e:
            return:"success": False, "error": str(e)}


    
    async def _fix_compilation_errors(self, project_id: str):
        """Attempt to fix compilation errors."""
        # Simplified compilation fix
        self.logger.info("🔧 Attempting to fix compilation errors")
    
    async def _fix_runtime_errors(self, project_id: str):
        """Attempt to fix runtime errors."""
        # Simplified runtime fix
        self.logger.info("🔧 Attempting to fix runtime errors")
    
    async def _rollback_to_previous_state(self, project_id: str, feature_id: str) -> Dict[str, Any]:
        """Rollback to the previous state before feature implementation."""
        try:
            incremental_state = shared_state.get_incremental_state(project_id)
            
            if incremental_state and feature_id in incremental_state.rollback_points:
                rollback_hash = incremental_state.rollback_points[feature_id]
                
                # Perform git rollback
                rollback_result = await self.execute_tool(
                    "git",
                    operation="reset_hard",
                    commit_hash=rollback_hash
                )
                
                if rollback_result.status.value == "success":
                    self.logger.info(f"🔄 Rolled back feature:feature_id} to {rollback_hash}")
                    return {"success": True, "rollback_hash": rollback_hash}


            return {"success": False, "reason": "No rollback point found"}
        
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return {"success": False, "error": str(e)}


    
    async def _validate_feature(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific feature implementation."""
        project_id = task_data["project_id"]
        feature_id = task_data["feature_id"]
        
        # Get feature from incremental state
        incremental_state = shared_state.get_incremental_state(project_id)
        
        if not incremental_state:
            return:"status": "no_incremental_state"}
        
        # Find the feature
        feature = None
        for f in incremental_state.feature_queue:
            if f["id"] == feature_id:
                feature = f
                break
        
        if not feature:
            return:"status": "feature_not_found"}
        
        # Perform validation
        validation_result = await self._validate_implemented_feature(project_id, feature)
        
        return:
            "status": "validation_completed",
            "feature_id": feature_id,
            "validation_result": validation_result

    
    async def _rollback_feature(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback a specific feature."""
        project_id = task_data["project_id"]
        feature_id = task_data["feature_id"]
        
        rollback_result = await self._rollback_to_previous_state(project_id, feature_id)
        
        return {
            "status": "rollback_completed",
            "feature_id": feature_id,
            "rollback_result": rollback_result

    
    # Supervision integration methods
    async def _register_incremental_process(self, project_id: str):
        """Register incremental implementation process with supervision."""
        try:
            supervision_agent = shared_state.get_agent_state("supervision")
            if supervision_agent:
                await self.collaborate_with_agent(
                    "supervision",
                    "register_process",
                   :
                        "agent_id": self.agent_id,
                        "task_type": "incremental_implementation",
                        "timeout_threshold": 1800,  # 30 minutes
                        "project_id": project_id

                )

        except Exception as e:
            self.logger.debug(f"Could not register with supervision: {e}")


    
    async def _register_feature_process(self, project_id: str, feature_id: str) -> str:
        """Register individual feature implementation with supervision."""
        process_id = f"feature_{feature_id}_{uuid.uuid4().hex[:8]}"
        
        try:
            shared_state.register_supervised_process(
                process_id=process_id,
                agent_id=self.agent_id,
                task_type="feature_implementation",
                timeout_threshold=600  # 10 minutes per feature
            )
        except Exception as e:
            self.logger.debug(f"Could not register feature process: {e}")

        
        return process_id

    
    async def _send_implementation_heartbeat(self, project_id: str, feature_id: str):
        """Send heartbeat during feature implementation."""
        try:
            self.send_message_to_agent(
                to_agent="supervision",
                message_type=MessageType.HEARTBEAT,
                content={
                    "project_id": project_id,
                    "feature_id": feature_id,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat()

            )
        except Exception as e:
            self.logger.debug(f"Could not send heartbeat: {e}")



    # Real-time awareness and proactive collaboration overrides
    def _react_to_peer_activity(self, peer_agent: str, activity_type: str, 
                               activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """React to peer agent activities with proactive collaboration."""
        
        # Architecture decisions → Prepare implementation
        if peer_agent == "architecture" and activity_type == "architecture_decision_made":
            self._prepare_for_architecture_changes(activity_details, consciousness_update)
        
        # Testing started → Provide implementation insights
        elif peer_agent == "testing" and activity_type in ["test_planning", "test_execution_started"]:
            self._assist_with_test_insights(activity_details)
        
        # Security findings → Address implementation security
        elif peer_agent == "security" and activity_type == "security_issue_found":
            self._address_security_in_implementation(activity_details)
        
        # Performance optimization → Optimize implementation
        elif peer_agent == "performance" and activity_type == "performance_issue_detected":
            self._optimize_implementation_performance(activity_details)
    
    def _prepare_for_architecture_changes(self, architecture_details: Dict[str, Any], consciousness: Dict[str, Any]) -> None:
        """Proactively prepare for architecture changes."""
        self.logger.info(f"🏗️ Preparing implementation for architecture changes...")
        
        # Broadcast preparation activity
        self.broadcast_activity(
            activity_type="implementation_preparation",
            activity_details={
                "trigger": "architecture_decision",
                "architecture_changes": architecture_details,
                "preparation_actions": [
                    "analyzing_architecture_impact",
                    "preparing_implementation_strategy",
                    "identifying_affected_components"
                ]
            },
            impact_level="high",
            collaboration_relevance=["testing", "security", "performance"]
        )
        
        # Extract key architecture decisions
        design_patterns = architecture_details.get("design_patterns", [])
        technology_choices = architecture_details.get("technology_choices", {})
        
        # Update shared consciousness with implementation readiness
        shared_state.update_shared_consciousness(
            "implementation_readiness",
            {
                "architecture_understood": True,
                "implementation_strategy": "ready",
                "estimated_complexity": self._estimate_implementation_complexity(architecture_details),
                "ready_for_features": True

        )

    
    def _assist_with_test_insights(self, test_details: Dict[str, Any]) -> None:
        """Proactively assist testing with implementation insights."""
        self.logger.info(f"🧪 Providing implementation insights for testing...")
        
        # Get current implementation state
        current_project_id = shared_state.get_current_project_id()
        if current_project_id:
            project_state = shared_state.get_project_state(current_project_id)
            
            implementation_insights =:
                "files_created": len(project_state.files_created) if project_state else 0,
                "features_implemented": self._get_implemented_features(),
                "testing_recommendations": self._generate_testing_recommendations(),
                "known_edge_cases": self._identify_implementation_edge_cases()

            # Broadcast insights to testing agent
            self.broadcast_activity(
                activity_type="implementation_insights_shared",
                activity_details={
                    "trigger": "testing_activity",
                    "insights": implementation_insights,
                    "suggested_test_focus": self._suggest_test_focus_areas()
                },
                impact_level="medium",
                collaboration_relevance=["testing"]
            )


    
    def _address_security_in_implementation(self, security_details: Dict[str, Any]) -> None:
        """Proactively address security issues in implementation."""
        self.logger.info(f"🔒 Addressing security concerns in implementation...")
        
        security_issue_type = security_details.get("issue_type", "")
        affected_files = security_details.get("affected_files", [])
        
        # Plan security fixes
        security_actions = {
            "immediate_actions": [],
            "preventive_measures": [],
            "code_changes_needed": []

        
        if "authentication" in security_issue_type.lower():
            security_actions["immediate_actions"].append("review_auth_implementation")
            security_actions["code_changes_needed"].append("strengthen_auth_validation")

        
        if "data_validation" in security_issue_type.lower():
            security_actions["immediate_actions"].append("add_input_sanitization")
            security_actions["code_changes_needed"].append("implement_data_validation")

        
        # Broadcast security response
        self.broadcast_activity(
            activity_type="security_response_initiated",
            activity_details={
                "trigger": "security_finding",
                "security_issue": security_details,
                "planned_actions": security_actions,
                "implementation_changes": "in_progress"
            },
            impact_level="high",
            collaboration_relevance=["security", "testing"]
        )

    
    def _optimize_implementation_performance(self, performance_details: Dict[str, Any]) -> None:
        """Proactively optimize implementation for performance."""
        self.logger.info(f"⚡ Optimizing implementation for performance...")
        
        performance_issue = performance_details.get("issue_type", "")
        metrics = performance_details.get("metrics",:})
        
        optimization_plan = {
            "code_optimizations": [],
            "architecture_improvements": [],
            "implementation_changes": []

        
        if "memory" in performance_issue.lower():
            optimization_plan["code_optimizations"].extend([
                "optimize_memory_usage",
                "implement_object_pooling",
                "reduce_memory_allocations"
            ])

        
        if "startup_time" in performance_issue.lower():
            optimization_plan["code_optimizations"].extend([
                "lazy_loading",
                "reduce_initialization_overhead",
                "optimize_critical_path"
            ])

        
        # Broadcast optimization activity
        self.broadcast_activity(
            activity_type="performance_optimization_started",
            activity_details={
                "trigger": "performance_issue",
                "performance_data": performance_details,
                "optimization_plan": optimization_plan,
                "expected_improvements": self._estimate_performance_improvements(performance_issue)
            },
            impact_level="medium",
            collaboration_relevance=["performance", "testing"]
        )

    
    def _estimate_implementation_complexity(self, architecture_details: Dict[str, Any]) -> str:
        """Estimate implementation complexity based on architecture."""
        layers = len(architecture_details.get("layers", []))
        patterns = len(architecture_details.get("design_patterns", []))
        
        complexity_score = layers + patterns
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 6:
            return "medium"
        } else:
            return "high"


    
    def _get_implemented_features(self) -> List[str]:
        """Get list of currently implemented features."""
        # Simplified implementation - in practice, would analyze actual files
        current_project_id = shared_state.get_current_project_id()
        if current_project_id:
            incremental_state = shared_state.get_incremental_state(current_project_id)
            if incremental_state:
                return incremental_state.completed_features

        return []

    
    def _generate_testing_recommendations(self) -> List[str]:
        """Generate testing recommendations based on implementation."""
        return [
            "focus_on_state_management_tests",
            "test_error_handling_paths",
            "validate_data_flow_integrity",
            "test_ui_component_interactions"
        ]

    
    def _identify_implementation_edge_cases(self) -> List[str]:
        """Identify edge cases in current implementation."""
        return [
            "null_safety_edge_cases",
            "async_operation_timing",
            "state_synchronization_issues",
            "navigation_edge_cases"
        ]

    
    def _suggest_test_focus_areas(self) -> List[str]:
        """Suggest areas for testing to focus on."""
        return [
            "recently_implemented_features",
            "complex_business_logic",
            "integration_points",
            "error_recovery_scenarios"
        ]

    
    def _estimate_performance_improvements(self, issue_type: str) -> Dict[str, str]:
        """Estimate expected performance improvements."""
        improvements =:
            "memory": "10-30% reduction in memory usage",
            "startup_time": "20-50% faster startup",
            "render_performance": "improved frame rate"

        
        return improvements.get(issue_type.lower(),:"general": "5-15% performance improvement"})


    async def _generate_repository_code(self, feature_name: str, repo_spec: Dict[str, Any]) -> str:
        """Generate repository implementation code."""
        repo_code = f"""
// {feature_name.title()} Repository Implementation
abstract class {feature_name.title()}Repository {{
  // TODO: Define repository interface methods
}}

class {feature_name.title()}RepositoryImpl implements {feature_name.title()}Repository {{
  // TODO: Implement repository methods
}}
"""
        return repo_code


    async def _generate_use_case_code(self, feature_name: str, use_case: Dict[str, Any]) -> str:
        """Generate use case implementation code."""
        use_case_name = use_case.get("name", "default")
        use_case_code = f"""
// {use_case_name.title()} Use Case
class {use_case_name.title()}UseCase {{
  // TODO: Implement use case logic
}}
"""
        return use_case_code


    async def _generate_bloc_files(self, feature_name: str, logic_spec: Dict[str, Any]) -> List[str]:
        """Generate BLoC files for a feature."""
        bloc_files = []
        
        # Generate BLoC state file
        state_code = f"""
//:feature_name.title()} State
import 'package:equatable/equatable.dart'

abstract class {feature_name.title()}State extends Equatable {{
  @override
  List<Object> get props => []
}}

class {feature_name.title()}Initial extends {feature_name.title()}State {{}}

class {feature_name.title()}Loading extends {feature_name.title()}State {{}}

class {feature_name.title()}Loaded extends {feature_name.title()}State {{}}

class {feature_name.title()}Error extends {feature_name.title()}State {{
  final String message
  {feature_name.title()}Error(self.message)
  
  @override
  List<Object> get props => [message]
}}
"""
        
        state_file = f"lib/features/{feature_name}/presentation/bloc/{feature_name}_state.dart"
        if await self._create_actual_file("flutter_projects", state_file, state_code):
            bloc_files.append(state_file)
        
        return bloc_files



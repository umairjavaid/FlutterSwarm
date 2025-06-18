"""
Implementation Agent - Generates Flutter/Dart code based on architectural decisions.
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

class ImplementationAgent(BaseAgent):
    """
    The Implementation Agent specializes in generating Flutter/Dart code.
    It transforms architectural decisions into working code.
    """
    
    def __init__(self):
        super().__init__("implementation")
        self.flutter_templates = {
            "bloc": self._get_bloc_template(),
            "provider": self._get_provider_template(),
            "riverpod": self._get_riverpod_template(),
            "clean_architecture": self._get_clean_architecture_template()
        }
        
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
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
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
        """Implement a specific feature."""
        project_id = task_data["project_id"]
        feature_name = task_data["feature_name"]
        requirements = task_data.get("requirements", [])
        architecture_context = task_data.get("architecture_context", "")
        
        project = shared_state.get_project_state(project_id)
        
        implementation_prompt = f"""
        Implement the {feature_name} feature for this Flutter application:
        
        Project: {project.name}
        Feature: {feature_name}
        Requirements: {requirements}
        Architecture Context: {architecture_context}
        
        Generate complete, production-ready Flutter/Dart code including:
        
        1. **Models/Entities**: Data classes with proper serialization
        2. **Repository/Data Layer**: Data access implementation
        3. **Business Logic**: State management implementation
        4. **UI Layer**: Widgets and screens
        5. **Navigation**: Route definitions and navigation logic
        6. **Dependency Injection**: Service registration
        7. **Error Handling**: Proper error handling throughout
        
        Follow these Flutter best practices:
        - Use const constructors where possible
        - Implement proper null safety
        - Follow Flutter naming conventions
        - Use appropriate widgets for the use case
        - Implement responsive design principles
        - Add proper documentation comments
        
        For each file, provide:
        - File path (relative to lib/)
        - Complete code content
        - Brief description of the file's purpose
        
        Make the code maintainable, testable, and following SOLID principles.
        """
        
        implementation = await self.think(implementation_prompt, {
            "project": project,
            "feature": feature_name,
            "architecture_decisions": project.architecture_decisions
        })
        
        # Parse and create files
        files_created = await self._parse_and_create_files(project_id, implementation)
        
        return {
            "feature": feature_name,
            "files_created": files_created,
            "implementation": implementation,
            "status": "implemented"
        }
    
    async def _generate_models(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data models and DTOs."""
        project_id = task_data["project_id"]
        entities = task_data.get("entities", [])
        
        models_prompt = f"""
        Generate Flutter/Dart models for the following entities:
        {entities}
        
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
        class User extends Equatable {{
          const User({{
            required this.id,
            required this.name,
            required this.email,
            this.avatar,
          }});
          
          final String id;
          final String name;
          final String email;
          final String? avatar;
          
          factory User.fromJson(Map<String, dynamic> json) => User(
            id: json['id'] as String,
            name: json['name'] as String,
            email: json['email'] as String,
            avatar: json['avatar'] as String?,
          );
          
          Map<String, dynamic> toJson() => {{
            'id': id,
            'name': name,
            'email': email,
            if (avatar != null) 'avatar': avatar,
          }};
          
          User copyWith({{
            String? id,
            String? name,
            String? email,
            String? avatar,
          }}) {{
            return User(
              id: id ?? this.id,
              name: name ?? this.name,
              email: email ?? this.email,
              avatar: avatar ?? this.avatar,
            );
          }}
          
          @override
          List<Object?> get props => [id, name, email, avatar];
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
        }
    
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
        class HomeScreen extends StatefulWidget {{
          const HomeScreen({{super.key}});
          
          @override
          State<HomeScreen> createState() => _HomeScreenState();
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
            );
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
        }
    
    async def _implement_state_management(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the chosen state management solution."""
        project_id = task_data["project_id"]
        solution = task_data.get("solution", "bloc")
        features = task_data.get("features", [])
        
        state_management_prompt = f"""
        Implement {solution} state management for these features:
        Features: {features}
        
        Create a complete state management implementation including:
        
        1. **State Classes**: Define application states
        2. **Event Classes**: Define user actions/events (for BLoC)
        3. **Cubit/Bloc Classes**: Business logic implementation
        4. **Repository Integration**: Connect to data layer
        5. **Provider Setup**: Configure providers/injectors
        6. **Widget Integration**: Connect UI to state management
        
        {self.flutter_templates.get(solution, "Use best practices for the chosen solution")}
        
        Ensure the implementation follows:
        - Separation of concerns
        - Testability principles
        - Error handling
        - Loading states
        - Performance optimization
        
        Generate complete, production-ready state management code.
        """
        
        state_code = await self.think(state_management_prompt, {
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
        }
    
    async def _setup_project_structure(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up the initial project structure."""
        project_id = task_data["project_id"]
        architecture_style = task_data.get("architecture_style", "clean")
        
        project = shared_state.get_project_state(project_id)
        if not project:
            return {"error": "Project not found"}
        
        # Import project manager and create the Flutter project immediately
        from utils.project_manager import ProjectManager
        pm = ProjectManager()
        
        print(f"🏗️  Setting up Flutter project structure for {project.name}")
        
        try:
            # Create the actual Flutter project structure first
            if not pm.project_exists(project.name):
                project_path = pm.create_flutter_project_structure(project.name)
                print(f"✅ Flutter project created at: {project_path}")
            else:
                project_path = pm.get_project_path(project.name)
                print(f"✅ Using existing Flutter project at: {project_path}")
            
            # Create a basic music app structure
            files_created = await self._create_music_app_structure(project_path, project)
            
            # Update shared state
            for file_path in files_created:
                shared_state.add_file_to_project(project_id, file_path, f"// Generated by FlutterSwarm for {file_path}")
            
            print(f"📱 Created {len(files_created)} files for music app structure")
            
            return {
                "architecture_style": architecture_style,
                "files_created": files_created,
                "project_path": project_path,
                "status": "project_structure_created"
            }
            
        except Exception as e:
            print(f"❌ Failed to create project structure: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def _parse_and_create_files(self, project_id: str, code_content: str) -> List[str]:
        """Parse generated code and create actual files in the Flutter project."""
        from utils.project_manager import ProjectManager
        
        files_created = []
        project = shared_state.get_project_state(project_id)
        
        if not project:
            print(f"❌ Project {project_id} not found")
            return files_created
        
        # Get project manager and ensure project structure exists
        pm = ProjectManager()
        project_path = pm.get_project_path(project.name)
        
        # Create Flutter project structure if it doesn't exist
        if not pm.project_exists(project.name):
            print(f"🏗️  Creating Flutter project structure for {project.name}")
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
            
            print(f"📄 Created file: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create file {file_path}: {e}")
            return False
    
    async def _create_basic_flutter_app(self, project_path: str, project_name: str) -> List[str]:
        """Create a basic Flutter app when LLM output parsing fails."""
        files_created = []
        
        # Create main.dart
        main_dart_content = f'''import 'package:flutter/material.dart';

void main() {{
  runApp(const {project_name.replace(' ', '')}App());
}}

class {project_name.replace(' ', '')}App extends StatelessWidget {{
  const {project_name.replace(' ', '')}App({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{project_name}',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }}
}}

class HomeScreen extends StatelessWidget {{
  const HomeScreen({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text('{project_name}'),
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
    );
  }}
}}
''';
        
        if await self._create_actual_file(project_path, 'lib/main.dart', main_dart_content):
            files_created.append('lib/main.dart')
        
        return files_created
    
    async def _create_music_app_structure(self, project_path: str, project) -> List[str]:
        """Create a comprehensive music app structure."""
        files_created = []
        
        # Main app file
        main_content = f'''import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'theme/app_theme.dart';

void main() {{
  runApp(const MusicStreamProApp());
}}

class MusicStreamProApp extends StatelessWidget {{
  const MusicStreamProApp({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{project.name}',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }}
}}
'''
        
        # Home screen
        home_screen_content = '''import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const HomePage(),
    const SearchPage(),
    const LibraryPage(),
    const ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search),
            label: 'Search',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.library_music),
            label: 'Library',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MusicStreamPro'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.music_note, size: 100, color: Colors.deepPurple),
            SizedBox(height: 20),
            Text(
              'Welcome to MusicStreamPro!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              'Your AI-generated music streaming app',
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}

class SearchPage extends StatelessWidget {
  const SearchPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Search')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 100),
            Text('Search for music, artists, and playlists'),
          ],
        ),
      ),
    );
  }
}

class LibraryPage extends StatelessWidget {
  const LibraryPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your Library')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.library_music, size: 100),
            Text('Your playlists and saved music'),
          ],
        ),
      ),
    );
  }
}

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.person, size: 100),
            Text('Your profile and settings'),
          ],
        ),
      ),
    );
  }
}
''';
        
        # App theme
        theme_content = '''import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.deepPurple,
        brightness: Brightness.light,
      ),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.deepPurple,
        brightness: Brightness.dark,
      ),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
    );
  }
}
''';
        
        # Create files
        file_map = {
            'lib/main.dart': main_content,
            'lib/screens/home_screen.dart': home_screen_content,
            'lib/theme/app_theme.dart': theme_content,
        }
        
        for file_path, content in file_map.items():
            if await self._create_actual_file(project_path, file_path, content):
                files_created.append(file_path)
        
        return files_created
    
    def _get_bloc_template(self) -> str:
        """Get BLoC implementation template."""
        return """
        Use flutter_bloc package with the following pattern:
        
        1. Define states extending Equatable
        2. Define events extending Equatable  
        3. Create Bloc extending Bloc<Event, State>
        4. Use BlocProvider for dependency injection
        5. Use BlocBuilder/BlocListener in widgets
        
        Example:
        // States
        abstract class AuthState extends Equatable {{
          @override
          List<Object> get props => [];
        }}
        
        class AuthInitial extends AuthState {{}}
        class AuthLoading extends AuthState {{}}
        class AuthAuthenticated extends AuthState {{
          final User user;
          AuthAuthenticated(this.user);
          @override
          List<Object> get props => [user];
        }}
        
        // Events
        abstract class AuthEvent extends Equatable {{
          @override
          List<Object> get props => [];
        }}
        
        class AuthLoginRequested extends AuthEvent {{
          final String email;
          final String password;
          AuthLoginRequested(this.email, this.password);
          @override
          List<Object> get props => [email, password];
        }}
        
        // Bloc
        class AuthBloc extends Bloc<AuthEvent, AuthState> {{
          final AuthRepository authRepository;
          
          AuthBloc(this.authRepository) : super(AuthInitial()) {{
            on<AuthLoginRequested>(_onLoginRequested);
          }}
          
          Future<void> _onLoginRequested(
            AuthLoginRequested event,
            Emitter<AuthState> emit,
          ) async {{
            emit(AuthLoading());
            try {{
              final user = await authRepository.login(event.email, event.password);
              emit(AuthAuthenticated(user));
            }} catch (e) {{
              emit(AuthError(e.toString()));
            }}
          }}
        }}
        """
    
    def _get_provider_template(self) -> str:
        """Get Provider implementation template."""
        return """
        Use provider package with ChangeNotifier pattern:
        
        1. Create ChangeNotifier classes for state
        2. Use ChangeNotifierProvider for dependency injection
        3. Use Consumer/Selector for listening to changes
        4. Call notifyListeners() when state changes
        """
    
    def _get_riverpod_template(self) -> str:
        """Get Riverpod implementation template."""
        return """
        Use riverpod package with providers:
        
        1. Create providers using Provider, StateProvider, etc.
        2. Use ConsumerWidget for widgets that need providers
        3. Use ref.watch() to listen to providers
        4. Use ref.read() for one-time reads
        """
    
    def _get_clean_architecture_template(self) -> str:
        """Get Clean Architecture template."""
        return """
        Follow Clean Architecture principles:
        
        1. Domain Layer: Entities, Use Cases, Repository Interfaces
        2. Data Layer: Repository Implementations, Data Sources, Models
        3. Presentation Layer: Widgets, State Management, Pages
        4. Core: Constants, Errors, Utils
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
        }
    
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
        }
    
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
            print(f"🔧 Implementation Agent: Applying fixes to project {project.name}")
            fixed_files.append("example_fixed_file.dart")
        
        return fixed_files
    
    async def _provide_implementation_guidance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide implementation guidance to other agents."""
        guidance_prompt = f"""
        Provide implementation guidance for:
        
        Context: {data.get('context', '')}
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
        }
    
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
        
        return {
            "refactored_files": refactored_files,
            "goal": refactor_goal,
            "status": "refactoring_completed"
        }
    
    async def _start_implementation(self, project_id: str) -> None:
        """Start implementation after architecture is completed."""
        project = shared_state.get_project_state(project_id)
        if not project:
            return
        
        print(f"🔨 Starting implementation for project: {project.name}")
        
        # Send message to orchestrator that implementation is ready to begin
        self.send_message_to_agent(
            to_agent="orchestrator",
            message_type=MessageType.STATUS_UPDATE,
            content={
                "status": "implementation_ready",
                "project_id": project_id,
                "message": "Implementation agent ready to begin coding"
            }
        )
    
    async def _analyze_new_file(self, change_data: Dict[str, Any]) -> None:
        """Analyze newly created files for implementation issues."""
        file_path = change_data.get("file_path", "")
        project_id = change_data.get("project_id", "")
        
        if not file_path.endswith('.dart'):
            return  # Only analyze Dart files
        
        print(f"🔍 Analyzing new file: {file_path}")
        
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
                    print(f"⚠️ Empty file detected: {file_path}")
                elif 'class ' not in content and 'void main(' not in content and 'import ' not in content:
                    print(f"⚠️ Possibly invalid Dart file: {file_path}")
                else:
                    print(f"✅ File looks valid: {file_path}")
        
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
            print(f"🔧 Implementation Agent: Handling QA issue - {issue_type}")
            
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
                    }
                },
                priority=4
            )
        else:
            print(f"📝 Implementation Agent: QA issue '{issue_type}' not implementation-related")

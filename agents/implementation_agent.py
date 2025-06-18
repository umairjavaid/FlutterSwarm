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
        
        structure_prompt = f"""
        Create a complete Flutter project structure following {architecture_style} architecture:
        
        Generate the following files and directories:
        
        1. **Core Files**:
           - lib/main.dart
           - lib/app.dart
           - lib/core/constants/
           - lib/core/errors/
           - lib/core/utils/
           - lib/core/themes/
        
        2. **Feature Structure** (for each feature):
           - lib/features/[feature]/data/
           - lib/features/[feature]/domain/
           - lib/features/[feature]/presentation/
        
        3. **Shared Components**:
           - lib/shared/widgets/
           - lib/shared/utils/
           - lib/shared/constants/
        
        4. **Configuration Files**:
           - pubspec.yaml with all necessary dependencies
           - analysis_options.yaml
           - .gitignore
        
        Provide complete file contents for each file, following best practices.
        Include proper imports, exports, and package dependencies.
        """
        
        structure_code = await self.think(structure_prompt, {
            "architecture": architecture_style,
            "project": shared_state.get_project_state(project_id)
        })
        
        files_created = await self._parse_and_create_files(project_id, structure_code)
        
        return {
            "architecture_style": architecture_style,
            "files_created": files_created,
            "structure": structure_code
        }
    
    async def _parse_and_create_files(self, project_id: str, code_content: str) -> List[str]:
        """Parse generated code and create files in the project."""
        files_created = []
        
        # This is a simplified implementation
        # In a real scenario, you'd parse the LLM output to extract file paths and contents
        
        # For now, we'll simulate file creation by adding to shared state
        lines = code_content.split('\n')
        current_file = None
        current_content = []
        
        for line in lines:
            if line.startswith('// File:') or line.startswith('# File:'):
                if current_file and current_content:
                    # Save previous file
                    shared_state.add_file_to_project(
                        project_id, 
                        current_file, 
                        '\n'.join(current_content)
                    )
                    files_created.append(current_file)
                
                # Start new file
                current_file = line.split(':', 1)[1].strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            shared_state.add_file_to_project(
                project_id, 
                current_file, 
                '\n'.join(current_content)
            )
            files_created.append(current_file)
        
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
    
    async def _handle_general_implementation(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general implementation tasks."""
        response = await self.think(f"Implement: {task_description}", task_data)
        return {"response": response, "task": task_description}

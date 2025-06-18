"""
Code generation tool for Flutter/Dart development.
"""

import asyncio
import os
import json
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .file_tool import FileTool

class CodeGenerationTool(BaseTool):
    """
    Tool for generating Flutter/Dart code components.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="code_generation",
            description="Generate Flutter/Dart code components",
            timeout=60
        )
        self.project_directory = project_directory or os.getcwd()
        self.file_tool = FileTool(project_directory)
        
        # Code templates
        self.templates = {
            "bloc": self._get_bloc_template,
            "cubit": self._get_cubit_template,
            "provider": self._get_provider_template,
            "riverpod": self._get_riverpod_template,
            "widget": self._get_widget_template,
            "model": self._get_model_template,
            "service": self._get_service_template,
            "repository": self._get_repository_template,
            "screen": self._get_screen_template,
            "api_client": self._get_api_client_template
        }
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute code generation operations.
        
        Args:
            operation: Operation to perform (generate, scaffold, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        if operation == "generate":
            return await self._generate_component(**kwargs)
        elif operation == "scaffold":
            return await self._scaffold_feature(**kwargs)
        elif operation == "model_from_json":
            return await self._generate_model_from_json(**kwargs)
        elif operation == "crud_operations":
            return await self._generate_crud_operations(**kwargs)
        elif operation == "clean_architecture":
            return await self._generate_clean_architecture(**kwargs)
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown operation: {operation}"
            )
    
    async def _generate_component(self, **kwargs) -> ToolResult:
        """Generate a specific code component."""
        component_type = kwargs.get("component_type")
        name = kwargs.get("name")
        options = kwargs.get("options", {})
        
        if not component_type or not name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="component_type and name are required"
            )
        
        if component_type not in self.templates:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown component type: {component_type}"
            )
        
        # Generate code using template
        template_func = self.templates[component_type]
        generated_code = template_func(name, options)
        
        # Determine file path
        file_path = self._get_component_file_path(component_type, name, options)
        
        # Create directories if needed
        dir_path = os.path.dirname(os.path.join(self.project_directory, file_path))
        os.makedirs(dir_path, exist_ok=True)
        
        # Write file
        write_result = await self.file_tool.execute(
            "write",
            file_path=file_path,
            content=generated_code
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"{component_type.title()} '{name}' generated at {file_path}",
                data={
                    "component_type": component_type,
                    "name": name,
                    "file_path": file_path
                }
            )
        
        return write_result
    
    async def _scaffold_feature(self, **kwargs) -> ToolResult:
        """Scaffold a complete feature with multiple components."""
        feature_name = kwargs.get("feature_name")
        architecture = kwargs.get("architecture", "bloc")  # bloc, provider, riverpod
        include_components = kwargs.get("include_components", ["model", "repository", "bloc", "screen"])
        
        if not feature_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="feature_name is required"
            )
        
        generated_files = []
        
        # Generate each component
        for component in include_components:
            if component in self.templates:
                options = {
                    "feature_name": feature_name,
                    "architecture": architecture
                }
                
                result = await self._generate_component(
                    component_type=component,
                    name=feature_name,
                    options=options
                )
                
                if result.status == ToolStatus.SUCCESS:
                    generated_files.append(result.data["file_path"])
        
        # Generate barrel file (index.dart)
        barrel_content = self._generate_barrel_file(feature_name, generated_files)
        barrel_path = f"lib/features/{feature_name.lower()}/{feature_name.lower()}.dart"
        
        await self.file_tool.execute(
            "write",
            file_path=barrel_path,
            content=barrel_content
        )
        
        generated_files.append(barrel_path)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Feature '{feature_name}' scaffolded with {len(generated_files)} files",
            data={
                "feature_name": feature_name,
                "architecture": architecture,
                "generated_files": generated_files
            }
        )
    
    async def _generate_model_from_json(self, **kwargs) -> ToolResult:
        """Generate Dart model from JSON data."""
        model_name = kwargs.get("model_name")
        json_data = kwargs.get("json_data")
        
        if not model_name or not json_data:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="model_name and json_data are required"
            )
        
        try:
            # Parse JSON if it's a string
            if isinstance(json_data, str):
                json_data = json.loads(json_data)
            
            # Generate model code
            model_code = self._generate_model_from_json_data(model_name, json_data)
            
            # Write model file
            file_path = f"lib/models/{model_name.lower()}.dart"
            
            write_result = await self.file_tool.execute(
                "write",
                file_path=file_path,
                content=model_code
            )
            
            if write_result.status == ToolStatus.SUCCESS:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output=f"Model '{model_name}' generated from JSON",
                    data={
                        "model_name": model_name,
                        "file_path": file_path
                    }
                )
            
            return write_result
            
        except json.JSONDecodeError as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Invalid JSON data: {str(e)}"
            )
    
    async def _generate_crud_operations(self, **kwargs) -> ToolResult:
        """Generate CRUD operations for a model."""
        model_name = kwargs.get("model_name")
        fields = kwargs.get("fields", [])
        
        if not model_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="model_name is required"
            )
        
        generated_files = []
        
        # Generate repository
        repository_code = self._generate_crud_repository(model_name, fields)
        repository_path = f"lib/repositories/{model_name.lower()}_repository.dart"
        
        await self.file_tool.execute(
            "write",
            file_path=repository_path,
            content=repository_code
        )
        generated_files.append(repository_path)
        
        # Generate service
        service_code = self._generate_crud_service(model_name, fields)
        service_path = f"lib/services/{model_name.lower()}_service.dart"
        
        await self.file_tool.execute(
            "write",
            file_path=service_path,
            content=service_code
        )
        generated_files.append(service_path)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"CRUD operations generated for '{model_name}'",
            data={
                "model_name": model_name,
                "generated_files": generated_files
            }
        )
    
    async def _generate_clean_architecture(self, **kwargs) -> ToolResult:
        """Generate clean architecture folder structure and base files."""
        project_name = kwargs.get("project_name", "MyApp")
        
        # Create folder structure
        folders = [
            "lib/core/error",
            "lib/core/usecases",
            "lib/core/utils",
            "lib/data/datasources",
            "lib/data/models",
            "lib/data/repositories",
            "lib/domain/entities",
            "lib/domain/repositories",
            "lib/domain/usecases",
            "lib/presentation/bloc",
            "lib/presentation/pages",
            "lib/presentation/widgets"
        ]
        
        for folder in folders:
            full_path = os.path.join(self.project_directory, folder)
            os.makedirs(full_path, exist_ok=True)
        
        # Generate base files
        generated_files = []
        
        # Core files
        failure_code = self._generate_failure_class()
        await self.file_tool.execute("write", file_path="lib/core/error/failures.dart", content=failure_code)
        generated_files.append("lib/core/error/failures.dart")
        
        usecase_code = self._generate_usecase_base()
        await self.file_tool.execute("write", file_path="lib/core/usecases/usecase.dart", content=usecase_code)
        generated_files.append("lib/core/usecases/usecase.dart")
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Clean architecture structure created with {len(generated_files)} base files",
            data={
                "project_name": project_name,
                "folders_created": folders,
                "base_files": generated_files
            }
        )
    
    def _get_component_file_path(self, component_type: str, name: str, options: Dict) -> str:
        """Get the file path for a component."""
        feature_name = options.get("feature_name", name)
        
        path_map = {
            "bloc": f"lib/features/{feature_name.lower()}/presentation/bloc/{name.lower()}_bloc.dart",
            "cubit": f"lib/features/{feature_name.lower()}/presentation/cubit/{name.lower()}_cubit.dart",
            "provider": f"lib/providers/{name.lower()}_provider.dart",
            "riverpod": f"lib/providers/{name.lower()}_provider.dart",
            "widget": f"lib/widgets/{name.lower()}_widget.dart",
            "model": f"lib/models/{name.lower()}.dart",
            "service": f"lib/services/{name.lower()}_service.dart",
            "repository": f"lib/repositories/{name.lower()}_repository.dart",
            "screen": f"lib/screens/{name.lower()}_screen.dart",
            "api_client": f"lib/services/api/{name.lower()}_api_client.dart"
        }
        
        return path_map.get(component_type, f"lib/{component_type}/{name.lower()}.dart")
    
    def _get_bloc_template(self, name: str, options: Dict) -> str:
        """Generate BLoC template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';

part '{name.lower()}_event.dart';
part '{name.lower()}_state.dart';

class {class_name}Bloc extends Bloc<{class_name}Event, {class_name}State> {{
  {class_name}Bloc() : super({class_name}Initial()) {{
    on<{class_name}Event>((event, emit) {{
      // TODO: implement event handler
    }});
  }}
}}
'''
    
    def _get_cubit_template(self, name: str, options: Dict) -> str:
        """Generate Cubit template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';

part '{name.lower()}_state.dart';

class {class_name}Cubit extends Cubit<{class_name}State> {{
  {class_name}Cubit() : super({class_name}Initial());
  
  void someMethod() {{
    // TODO: implement method
    emit({class_name}Loading());
    // Perform operations
    emit({class_name}Success());
  }}
}}
'''
    
    def _get_provider_template(self, name: str, options: Dict) -> str:
        """Generate Provider template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:flutter/material.dart';

class {class_name}Provider with ChangeNotifier {{
  bool _isLoading = false;
  String? _error;
  
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  void setLoading(bool loading) {{
    _isLoading = loading;
    notifyListeners();
  }}
  
  void setError(String? error) {{
    _error = error;
    notifyListeners();
  }}
  
  Future<void> someAsyncMethod() async {{
    setLoading(true);
    setError(null);
    
    try {{
      // TODO: implement async operation
      await Future.delayed(Duration(seconds: 1));
    }} catch (e) {{
      setError(e.toString());
    }} finally {{
      setLoading(false);
    }}
  }}
}}
'''
    
    def _get_riverpod_template(self, name: str, options: Dict) -> str:
        """Generate Riverpod provider template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:flutter_riverpod/flutter_riverpod.dart';

// State class
class {class_name}State {{
  final bool isLoading;
  final String? error;
  final dynamic data;
  
  const {class_name}State({{
    this.isLoading = false,
    this.error,
    this.data,
  }});
  
  {class_name}State copyWith({{
    bool? isLoading,
    String? error,
    dynamic data,
  }}) {{
    return {class_name}State(
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      data: data ?? this.data,
    );
  }}
}}

// Notifier
class {class_name}Notifier extends StateNotifier<{class_name}State> {{
  {class_name}Notifier() : super(const {class_name}State());
  
  Future<void> someAsyncMethod() async {{
    state = state.copyWith(isLoading: true, error: null);
    
    try {{
      // TODO: implement async operation
      await Future.delayed(Duration(seconds: 1));
      state = state.copyWith(isLoading: false);
    }} catch (e) {{
      state = state.copyWith(isLoading: false, error: e.toString());
    }}
  }}
}}

// Provider
final {name.lower()}Provider = StateNotifierProvider<{class_name}Notifier, {class_name}State>(
  (ref) => {class_name}Notifier(),
);
'''
    
    def _get_widget_template(self, name: str, options: Dict) -> str:
        """Generate Widget template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:flutter/material.dart';

class {class_name}Widget extends StatelessWidget {{
  const {class_name}Widget({{Key? key}}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {{
    return Container(
      child: Text('{class_name}'),
    );
  }}
}}
'''
    
    def _get_model_template(self, name: str, options: Dict) -> str:
        """Generate Model template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:equatable/equatable.dart';

class {class_name} extends Equatable {{
  final String id;
  final String name;
  
  const {class_name}({{
    required this.id,
    required this.name,
  }});
  
  factory {class_name}.fromJson(Map<String, dynamic> json) {{
    return {class_name}(
      id: json['id'] as String,
      name: json['name'] as String,
    );
  }}
  
  Map<String, dynamic> toJson() {{
    return {{
      'id': id,
      'name': name,
    }};
  }}
  
  {class_name} copyWith({{
    String? id,
    String? name,
  }}) {{
    return {class_name}(
      id: id ?? this.id,
      name: name ?? this.name,
    );
  }}
  
  @override
  List<Object?> get props => [id, name];
}}
'''
    
    def _get_service_template(self, name: str, options: Dict) -> str:
        """Generate Service template."""
        class_name = self._to_pascal_case(name)
        
        return f'''class {class_name}Service {{
  static final {class_name}Service _instance = {class_name}Service._internal();
  factory {class_name}Service() => _instance;
  {class_name}Service._internal();
  
  Future<void> initialize() async {{
    // TODO: implement initialization
  }}
  
  Future<dynamic> someAsyncMethod() async {{
    // TODO: implement service method
    return Future.value();
  }}
  
  void dispose() {{
    // TODO: implement cleanup
  }}
}}
'''
    
    def _get_repository_template(self, name: str, options: Dict) -> str:
        """Generate Repository template."""
        class_name = self._to_pascal_case(name)
        
        return f'''abstract class {class_name}Repository {{
  Future<List<dynamic>> getAll();
  Future<dynamic> getById(String id);
  Future<dynamic> create(Map<String, dynamic> data);
  Future<dynamic> update(String id, Map<String, dynamic> data);
  Future<void> delete(String id);
}}

class {class_name}RepositoryImpl implements {class_name}Repository {{
  @override
  Future<List<dynamic>> getAll() async {{
    // TODO: implement getAll
    throw UnimplementedError();
  }}
  
  @override
  Future<dynamic> getById(String id) async {{
    // TODO: implement getById
    throw UnimplementedError();
  }}
  
  @override
  Future<dynamic> create(Map<String, dynamic> data) async {{
    // TODO: implement create
    throw UnimplementedError();
  }}
  
  @override
  Future<dynamic> update(String id, Map<String, dynamic> data) async {{
    // TODO: implement update
    throw UnimplementedError();
  }}
  
  @override
  Future<void> delete(String id) async {{
    // TODO: implement delete
    throw UnimplementedError();
  }}
}}
'''
    
    def _get_screen_template(self, name: str, options: Dict) -> str:
        """Generate Screen template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:flutter/material.dart';

class {class_name}Screen extends StatelessWidget {{
  const {class_name}Screen({{Key? key}}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{class_name}'),
      ),
      body: const Center(
        child: Text('{class_name} Screen'),
      ),
    );
  }}
}}
'''
    
    def _get_api_client_template(self, name: str, options: Dict) -> str:
        """Generate API Client template."""
        class_name = self._to_pascal_case(name)
        
        return f'''import 'package:dio/dio.dart';

class {class_name}ApiClient {{
  final Dio _dio;
  
  {class_name}ApiClient(this._dio);
  
  Future<Response> get(String endpoint) async {{
    try {{
      return await _dio.get(endpoint);
    }} catch (e) {{
      throw Exception('Failed to GET $endpoint: $e');
    }}
  }}
  
  Future<Response> post(String endpoint, Map<String, dynamic> data) async {{
    try {{
      return await _dio.post(endpoint, data: data);
    }} catch (e) {{
      throw Exception('Failed to POST $endpoint: $e');
    }}
  }}
  
  Future<Response> put(String endpoint, Map<String, dynamic> data) async {{
    try {{
      return await _dio.put(endpoint, data: data);
    }} catch (e) {{
      throw Exception('Failed to PUT $endpoint: $e');
    }}
  }}
  
  Future<Response> delete(String endpoint) async {{
    try {{
      return await _dio.delete(endpoint);
    }} catch (e) {{
      throw Exception('Failed to DELETE $endpoint: $e');
    }}
  }}
}}
'''
    
    def _generate_model_from_json_data(self, model_name: str, json_data: Dict) -> str:
        """Generate Dart model from JSON data."""
        class_name = self._to_pascal_case(model_name)
        
        # Generate fields
        fields = []
        constructor_params = []
        from_json_assignments = []
        to_json_assignments = []
        copy_with_params = []
        copy_with_assignments = []
        props = []
        
        for key, value in json_data.items():
            dart_type = self._get_dart_type(value)
            field_name = self._to_camel_case(key)
            
            fields.append(f"  final {dart_type} {field_name};")
            constructor_params.append(f"    required this.{field_name},")
            from_json_assignments.append(f"      {field_name}: json['{key}'] as {dart_type},")
            to_json_assignments.append(f"      '{key}': {field_name},")
            copy_with_params.append(f"    {dart_type}? {field_name},")
            copy_with_assignments.append(f"      {field_name}: {field_name} ?? this.{field_name},")
            props.append(field_name)
        
        return f'''import 'package:equatable/equatable.dart';

class {class_name} extends Equatable {{
{chr(10).join(fields)}
  
  const {class_name}({{
{chr(10).join(constructor_params)}
  }});
  
  factory {class_name}.fromJson(Map<String, dynamic> json) {{
    return {class_name}(
{chr(10).join(from_json_assignments)}
    );
  }}
  
  Map<String, dynamic> toJson() {{
    return {{
{chr(10).join(to_json_assignments)}
    }};
  }}
  
  {class_name} copyWith({{
{chr(10).join(copy_with_params)}
  }}) {{
    return {class_name}(
{chr(10).join(copy_with_assignments)}
    );
  }}
  
  @override
  List<Object?> get props => [{", ".join(props)}];
}}
'''
    
    def _generate_barrel_file(self, feature_name: str, file_paths: List[str]) -> str:
        """Generate barrel file for feature exports."""
        exports = []
        
        for file_path in file_paths:
            # Get relative path from feature directory
            if f"features/{feature_name.lower()}" in file_path:
                relative_path = file_path.split(f"features/{feature_name.lower()}/")[1]
                exports.append(f"export '{relative_path}';")
        
        return f'''// Barrel file for {feature_name} feature
{chr(10).join(exports)}
'''
    
    def _generate_crud_repository(self, model_name: str, fields: List[str]) -> str:
        """Generate CRUD repository for a model."""
        class_name = self._to_pascal_case(model_name)
        
        return f'''import '../models/{model_name.lower()}.dart';

abstract class {class_name}Repository {{
  Future<List<{class_name}>> getAll();
  Future<{class_name}?> getById(String id);
  Future<{class_name}> create({class_name} {model_name.lower()});
  Future<{class_name}> update(String id, {class_name} {model_name.lower()});
  Future<void> delete(String id);
}}

class {class_name}RepositoryImpl implements {class_name}Repository {{
  @override
  Future<List<{class_name}>> getAll() async {{
    // TODO: implement data source integration
    throw UnimplementedError();
  }}
  
  @override
  Future<{class_name}?> getById(String id) async {{
    // TODO: implement data source integration
    throw UnimplementedError();
  }}
  
  @override
  Future<{class_name}> create({class_name} {model_name.lower()}) async {{
    // TODO: implement data source integration
    throw UnimplementedError();
  }}
  
  @override
  Future<{class_name}> update(String id, {class_name} {model_name.lower()}) async {{
    // TODO: implement data source integration
    throw UnimplementedError();
  }}
  
  @override
  Future<void> delete(String id) async {{
    // TODO: implement data source integration
    throw UnimplementedError();
  }}
}}
'''
    
    def _generate_crud_service(self, model_name: str, fields: List[str]) -> str:
        """Generate CRUD service for a model."""
        class_name = self._to_pascal_case(model_name)
        
        return f'''import '../models/{model_name.lower()}.dart';
import '../repositories/{model_name.lower()}_repository.dart';

class {class_name}Service {{
  final {class_name}Repository _repository;
  
  {class_name}Service(this._repository);
  
  Future<List<{class_name}>> getAll{class_name}s() async {{
    return await _repository.getAll();
  }}
  
  Future<{class_name}?> get{class_name}ById(String id) async {{
    return await _repository.getById(id);
  }}
  
  Future<{class_name}> create{class_name}({class_name} {model_name.lower()}) async {{
    // Add validation logic here
    return await _repository.create({model_name.lower()});
  }}
  
  Future<{class_name}> update{class_name}(String id, {class_name} {model_name.lower()}) async {{
    // Add validation logic here
    return await _repository.update(id, {model_name.lower()});
  }}
  
  Future<void> delete{class_name}(String id) async {{
    await _repository.delete(id);
  }}
}}
'''
    
    def _generate_failure_class(self) -> str:
        """Generate failure class for clean architecture."""
        return '''import 'package:equatable/equatable.dart';

abstract class Failure extends Equatable {
  const Failure();
  
  @override
  List<Object> get props => [];
}

// General failures
class ServerFailure extends Failure {}

class CacheFailure extends Failure {}

class NetworkFailure extends Failure {}

class ValidationFailure extends Failure {
  final String message;
  
  const ValidationFailure(this.message);
  
  @override
  List<Object> get props => [message];
}
'''
    
    def _generate_usecase_base(self) -> str:
        """Generate base usecase class."""
        return '''import 'package:equatable/equatable.dart';
import 'package:dartz/dartz.dart';
import '../error/failures.dart';

abstract class UseCase<Type, Params> {
  Future<Either<Failure, Type>> call(Params params);
}

class NoParams extends Equatable {
  @override
  List<Object> get props => [];
}
'''
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        return ''.join(word.capitalize() for word in text.replace('_', ' ').split())
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = text.replace('_', ' ').split()
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _get_dart_type(self, value: Any) -> str:
        """Get Dart type from Python value."""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, str):
            return "String"
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                return "List<Map<String, dynamic>>"
            return "List<dynamic>"
        elif isinstance(value, dict):
            return "Map<String, dynamic>"
        else:
            return "dynamic"

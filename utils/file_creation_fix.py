"""
Comprehensive fix for Implementation Agent file creation issues.
This addresses path construction, file writing, and shared state management.
"""

import os
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import the enhanced parser from previous fix
from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser
from shared.state import shared_state
from tools.base_tool import ToolStatus


class FixedImplementationAgent:
    """
    Fixed implementation methods that properly handle file creation.
    """
    
    def __init__(self, original_agent):
        """Initialize with reference to original agent for access to its methods."""
        self.agent = original_agent
        self.logger = original_agent.logger
        
    async def setup_project_context(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure project context is properly set up before any file operations.
        
        Returns:
            Dict with project_id, project_name, and project_path
        """
        project_id = task_data.get("project_id")
        project_name = task_data.get("project_name", task_data.get("name", "flutter_app"))
        
        # Normalize project name for Flutter
        sanitized_name = self.agent._normalize_flutter_package_name(project_name)
        
        # Determine consistent project path
        project_path = os.path.join("flutter_projects", sanitized_name)
        absolute_project_path = os.path.abspath(project_path)
        
        # Update shared state with correct project path
        if project_id:
            project_state = shared_state.get_project_state(project_id)
            if project_state:
                # Update project path in shared state
                shared_state.update_project(
                    project_id,
                    project_path=absolute_project_path,
                    name=project_name,
                    sanitized_name=sanitized_name
                )
            else:
                # Create project in shared state if it doesn't exist
                shared_state.create_project(
                    project_id=project_id,
                    name=project_name,
                    project_path=absolute_project_path
                )
        
        # Store project context in agent for easy access
        self.agent._current_project_id = project_id
        self.agent._current_project_path = absolute_project_path
        
        return {
            "project_id": project_id,
            "project_name": project_name,
            "sanitized_name": sanitized_name,
            "project_path": project_path,
            "absolute_project_path": absolute_project_path
        }
    
    async def parse_and_create_files(self, project_id: str, llm_response: str) -> List[str]:
        """
        Enhanced parsing and file creation with proper path handling.
        """
        # Ensure project context is set
        if not hasattr(self.agent, '_current_project_path') or not self.agent._current_project_path:
            # Try to get from shared state
            project_state = shared_state.get_project_state(project_id)
            if project_state and hasattr(project_state, 'project_path'):
                self.agent._current_project_path = project_state.project_path
            else:
                self.logger.error("❌ No project path available - cannot create files")
                return []
        
        # Parse LLM response
        parser = EnhancedLLMResponseParser(self.logger)
        parsed_files, parse_error = parser.parse_llm_response(llm_response, {
            "project_id": project_id
        })
        
        # If parsing failed, try reformatting
        if not parsed_files and parse_error:
            self.logger.warning(f"⚠️ Initial parsing failed: {parse_error}")
            
            # Ask LLM to reformat
            reformat_prompt = """
Your previous response was not in the correct JSON format.

CRITICAL: Return ONLY a valid JSON object (no other text):
{
    "files": [
        {"path": "lib/file.dart", "content": "code here", "description": "desc"}
    ]
}

Extract the files from your previous response and format them correctly.
"""
            
            try:
                reformatted = await self.agent.think(reformat_prompt, {"previous_response": llm_response[:1000]})
                parsed_files, _ = parser.parse_llm_response(reformatted, {"project_id": project_id})
            except Exception as e:
                self.logger.error(f"❌ Reformatting failed: {e}")
        
        # Create files with simplified, reliable approach
        created_files = []
        for file_info in parsed_files:
            success, created_path = await self.create_single_file(
                file_info["path"],
                file_info["content"],
                project_id
            )
            if success:
                created_files.append(created_path)
        
        return created_files
    
    async def create_single_file(self, relative_path: str, content: str, project_id: str) -> Tuple[bool, str]:
        """
        Create a single file with proper error handling and path management.
        
        Returns:
            Tuple of (success, relative_path_created)
        """
        if not content or not content.strip():
            self.logger.error(f"❌ Empty content for {relative_path}")
            return False, ""
        
        try:
            # Get absolute project path
            project_path = self.agent._current_project_path
            if not project_path:
                self.logger.error("❌ No project path set")
                return False, ""
            
            # Construct full file path
            full_path = os.path.join(project_path, relative_path)
            
            self.logger.info(f"📝 Creating file: {relative_path}")
            self.logger.debug(f"   Full path: {full_path}")
            
            # Create directory if needed
            directory = os.path.dirname(full_path)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    self.logger.debug(f"📁 Created directory: {directory}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to create directory {directory}: {e}")
                    return False, ""
            
            # Write the file
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.debug(f"✍️ Wrote {len(content)} chars to {relative_path}")
            except Exception as e:
                self.logger.error(f"❌ Failed to write file {relative_path}: {e}")
                return False, ""
            
            # Verify file was created
            if not os.path.exists(full_path):
                self.logger.error(f"❌ File not found after creation: {full_path}")
                return False, ""
            
            # Verify content matches
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    written_content = f.read()
                if written_content != content:
                    self.logger.warning(f"⚠️ Content mismatch for {relative_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not verify content for {relative_path}: {e}")
            
            # Register in shared state
            if project_id:
                try:
                    shared_state.add_file_to_project(project_id, relative_path, content)
                    self.logger.debug(f"📋 Registered {relative_path} in shared state")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not register file in shared state: {e}")
            
            # Broadcast activity for important files
            if any(pattern in relative_path for pattern in ['.dart', 'pubspec.yaml', 'README.md']):
                try:
                    await self.agent.broadcast_activity(
                        activity_type="file_created",
                        activity_details={
                            "file_path": relative_path,
                            "project_id": project_id,
                            "file_type": "dart" if relative_path.endswith('.dart') else "other"
                        }
                    )
                except Exception as e:
                    self.logger.debug(f"Could not broadcast file creation: {e}")
            
            return True, relative_path
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error creating {relative_path}: {e}")
            self.logger.debug(traceback.format_exc())
            return False, ""
    
    async def ensure_flutter_project_exists(self, task_data: Dict[str, Any]) -> bool:
        """Ensure a Flutter project exists at the specified path."""
        try:
            project_path = self.agent._current_project_path
            if not project_path:
                self.logger.error("❌ No project path set")
                return False
            
            # Check if pubspec.yaml exists
            pubspec_path = os.path.join(project_path, "pubspec.yaml")
            if os.path.exists(pubspec_path):
                self.logger.debug(f"✅ Flutter project already exists at {project_path}")
                return True
            
            # Create basic Flutter project structure
            self.logger.info(f"🚀 Creating Flutter project at {project_path}")
            
            # Create basic directory structure
            directories = [
                "lib",
                "test",
                "android/app/src/main/kotlin",
                "ios/Runner",
                "web"
            ]
            
            for directory in directories:
                dir_path = os.path.join(project_path, directory)
                os.makedirs(dir_path, exist_ok=True)
            
            # Create basic pubspec.yaml
            project_name = task_data.get("project_name", "flutter_app")
            sanitized_name = self.agent._normalize_flutter_package_name(project_name)
            
            pubspec_content = f"""name: {sanitized_name}
description: A Flutter application

version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
"""
            
            with open(pubspec_path, 'w') as f:
                f.write(pubspec_content)
            
            # Create basic main.dart
            main_dart_path = os.path.join(project_path, "lib", "main.dart")
            main_dart_content = f"""import 'package:flutter/material.dart';

void main() {{
  runApp(const MyApp());
}}

class MyApp extends StatelessWidget {{
  const MyApp({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{project_name}',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: '{project_name}'),
    );
  }}
}}

class MyHomePage extends StatefulWidget {{
  const MyHomePage({{super.key, required this.title}});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}}

class _MyHomePageState extends State<MyHomePage> {{
  int _counter = 0;

  void _incrementCounter() {{
    setState(() {{
      _counter++;
    }});
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
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }}
}}
"""
            
            with open(main_dart_path, 'w') as f:
                f.write(main_dart_content)
            
            self.logger.info(f"✅ Basic Flutter project created at {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create Flutter project: {e}")
            return False
    
    async def implement_feature_with_fixes(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement a feature with all fixes applied.
        """
        # Setup project context first
        context = await self.setup_project_context(task_data)
        self.logger.info(f"📂 Project context: {context['absolute_project_path']}")
        
        # Ensure Flutter project exists
        if not await self.ensure_flutter_project_exists(task_data):
            return {"status": "failed", "error": "Could not initialize Flutter project"}
        
        results = {
            "project_id": context["project_id"],
            "project_path": context["project_path"],
            "completed_features": [],
            "failed_features": [],
            "files_created": []
        }
        
        # Process each feature
        for feature in task_data.get("specific_features", []):
            feature_name = feature["name"]
            self.logger.info(f"🔨 Implementing feature: {feature_name}")
            
            # Generate implementation with enhanced prompt
            prompt = f"""
Generate Flutter implementation for feature: {feature_name}

CRITICAL: Return ONLY valid JSON with complete file contents:
{{
    "files": [
        {{
            "path": "lib/features/{feature_name.lower()}/presentation/screens/{feature_name.lower()}_screen.dart",
            "content": "import 'package:flutter/material.dart';\\n\\nclass {feature_name}Screen extends StatelessWidget {{\\n  const {feature_name}Screen({{super.key}});\\n\\n  @override\\n  Widget build(BuildContext context) {{\\n    return Scaffold(\\n      appBar: AppBar(title: const Text('{feature_name}')),\\n      body: const Center(child: Text('TODO: Implement {feature_name}')),\\n    );\\n  }}\\n}}",
            "description": "Main screen for {feature_name}"
        }}
    ]
}}

Project: {context['project_name']}
Feature Description: {feature.get('description', '')}
Architecture: Clean Architecture

Generate complete, working Flutter code for all necessary files.
Include: screens, widgets, models, repositories, and services as needed.

REMEMBER: Return ONLY the JSON, no explanations!
"""
            
            try:
                # Generate code
                generated_code = await self.agent.think(prompt, {
                    "feature": feature,
                    "context": context
                })
                
                # Parse and create files
                if generated_code:
                    files_created = await self.parse_and_create_files(
                        context["project_id"],
                        generated_code
                    )
                    
                    if files_created:
                        results["files_created"].extend(files_created)
                        results["completed_features"].append({
                            "name": feature_name,
                            "files": files_created
                        })
                        self.logger.info(f"✅ Feature {feature_name}: {len(files_created)} files created")
                    else:
                        results["failed_features"].append({
                            "name": feature_name,
                            "reason": "No files created"
                        })
                        self.logger.error(f"❌ Feature {feature_name}: No files created")
                else:
                    results["failed_features"].append({
                        "name": feature_name,
                        "reason": "Empty LLM response"
                    })
                    
            except Exception as e:
                self.logger.error(f"❌ Error implementing {feature_name}: {e}")
                results["failed_features"].append({
                    "name": feature_name,
                    "reason": str(e)
                })
        
        # Format Dart files if any were created
        if results["files_created"]:
            try:
                format_cmd = f"dart format {context['absolute_project_path']}/lib/"
                format_result = await self.agent.run_command(format_cmd)
                if format_result.status == ToolStatus.SUCCESS:
                    self.logger.info("✅ Formatted Dart files")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not format files: {e}")
        
        return {
            "status": "completed" if results["completed_features"] else "failed",
            "results": results
        }


# Integration function to apply fixes to existing Implementation Agent
def apply_file_creation_fixes(implementation_agent):
    """
    Apply all file creation fixes to an existing Implementation Agent instance.
    
    Usage:
        from utils.file_creation_fix import apply_file_creation_fixes
        apply_file_creation_fixes(implementation_agent)
    """
    fixed_agent = FixedImplementationAgent(implementation_agent)
    
    # Replace methods with fixed versions
    implementation_agent._parse_and_create_files = fixed_agent.parse_and_create_files
    implementation_agent.implement_specific_features = fixed_agent.implement_feature_with_fixes
    implementation_agent._setup_project_context = fixed_agent.setup_project_context
    implementation_agent._create_single_file = fixed_agent.create_single_file
    
    # Ensure agent has required attributes
    if not hasattr(implementation_agent, '_current_project_id'):
        implementation_agent._current_project_id = None
    if not hasattr(implementation_agent, '_current_project_path'):
        implementation_agent._current_project_path = None
    
    return implementation_agent

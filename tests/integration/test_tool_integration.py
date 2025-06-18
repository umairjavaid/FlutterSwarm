"""
Integration tests for the tool system functionality.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from tools.tool_manager import ToolManager
from tools.base_tool import ToolStatus


@pytest.mark.integration
class TestToolSystemIntegration:
    """Test suite for tool system integration."""
    
    @pytest.mark.asyncio
    async def test_complete_file_workflow(self, temp_directory):
        """Test complete file operations workflow."""
        manager = ToolManager(temp_directory)
        
        # Create directory structure
        result = await manager.execute_tool(
            "file", 
            operation="create_directory",
            directory="lib/features/auth"
        )
        assert result.status == ToolStatus.SUCCESS
        
        # Write a Dart file
        dart_content = '''
import 'package:flutter/material.dart';

class AuthService {
  Future<bool> login(String email, String password) async {
    // Implementation here
    return true;
  }
}
'''
        result = await manager.execute_tool(
            "file",
            operation="write",
            file_path="lib/features/auth/auth_service.dart",
            content=dart_content
        )
        assert result.status == ToolStatus.SUCCESS
        
        # Read the file back
        result = await manager.execute_tool(
            "file",
            operation="read",
            file_path="lib/features/auth/auth_service.dart"
        )
        assert result.status == ToolStatus.SUCCESS
        assert "AuthService" in result.output
        
        # Search for Dart files
        result = await manager.execute_tool(
            "file",
            operation="search",
            pattern="*.dart"
        )
        assert result.status == ToolStatus.SUCCESS
        assert "auth_service.dart" in str(result.data["files"])
        
        # Check file exists
        result = await manager.execute_tool(
            "file",
            operation="exists",
            path="lib/features/auth/auth_service.dart"
        )
        assert result.status == ToolStatus.SUCCESS
        assert result.data["exists"] is True
    
    @pytest.mark.asyncio
    async def test_flutter_project_workflow(self, temp_directory):
        """Test Flutter project creation and management workflow."""
        manager = ToolManager(temp_directory)
        
        # Create Flutter project structure
        await manager.execute_tool(
            "file",
            operation="create_directory", 
            directory="lib"
        )
        
        # Create pubspec.yaml
        pubspec_content = '''
name: test_flutter_app
description: A test Flutter application
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
'''
        
        await manager.execute_tool(
            "file",
            operation="write",
            file_path="pubspec.yaml",
            content=pubspec_content
        )
        
        # Create main.dart
        main_dart_content = '''
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Test Flutter App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Test App'),
      ),
      body: Center(
        child: Text('Hello, Flutter!'),
      ),
    );
  }
}
'''
        
        await manager.execute_tool(
            "file",
            operation="write",
            file_path="lib/main.dart",
            content=main_dart_content
        )
        
        # Mock Flutter commands since we don't have Flutter SDK in tests
        with patch.object(manager.tools["flutter"].terminal, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.status = ToolStatus.SUCCESS
            mock_result.output = "Flutter analyze completed successfully"
            mock_execute.return_value = mock_result
            
            # Run Flutter analyze
            result = await manager.execute_tool("flutter", operation="analyze")
            assert result.status == ToolStatus.SUCCESS
            
        # Verify project structure
        result = await manager.execute_tool("file", operation="exists", path="pubspec.yaml")
        assert result.data["exists"] is True
        
        result = await manager.execute_tool("file", operation="exists", path="lib/main.dart")
        assert result.data["exists"] is True
    
    @pytest.mark.asyncio
    async def test_git_workflow(self, temp_directory):
        """Test Git workflow integration."""
        manager = ToolManager(temp_directory)
        
        # Mock Git commands
        with patch.object(manager.tools["git"].terminal, 'execute') as mock_execute:
            def mock_git_command(command, **kwargs):
                result = MagicMock()
                result.status = ToolStatus.SUCCESS
                
                if "git init" in command:
                    result.output = "Initialized empty Git repository"
                elif "git add" in command:
                    result.output = "Files added to staging"
                elif "git commit" in command:
                    result.output = "Commit created successfully"
                elif "git status" in command:
                    result.output = "On branch main\nnothing to commit, working tree clean"
                else:
                    result.output = f"Executed: {command}"
                
                return result
            
            mock_execute.side_effect = mock_git_command
            
            # Initialize repository
            result = await manager.execute_tool("git", operation="init")
            assert result.status == ToolStatus.SUCCESS
            assert "Initialized" in result.output
            
            # Create a file first
            await manager.execute_tool(
                "file",
                operation="write",
                file_path="README.md",
                content="# Test Project\n\nThis is a test project."
            )
            
            # Add files
            result = await manager.execute_tool(
                "git", 
                operation="add",
                files=["README.md"]
            )
            assert result.status == ToolStatus.SUCCESS
            
            # Commit changes
            result = await manager.execute_tool(
                "git",
                operation="commit",
                message="Initial commit"
            )
            assert result.status == ToolStatus.SUCCESS
            
            # Check status
            result = await manager.execute_tool("git", operation="status")
            assert result.status == ToolStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_multi_tool_coordination(self, temp_directory):
        """Test coordination between multiple tools."""
        manager = ToolManager(temp_directory)
        
        # Create a Flutter project structure
        directories = [
            "lib/models",
            "lib/services",
            "lib/screens",
            "test/unit",
            "test/widget"
        ]
        
        for directory in directories:
            result = await manager.execute_tool(
                "file",
                operation="create_directory",
                directory=directory
            )
            assert result.status == ToolStatus.SUCCESS
        
        # Create model file
        user_model = '''
class User {
  final String id;
  final String name;
  final String email;
  
  User({required this.id, required this.name, required this.email});
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
    };
  }
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }
}
'''
        
        await manager.execute_tool(
            "file",
            operation="write",
            file_path="lib/models/user.dart",
            content=user_model
        )
        
        # Create service file
        user_service = '''
import '../models/user.dart';

class UserService {
  Future<User?> getUser(String id) async {
    // Implementation would go here
    return User(id: id, name: 'Test User', email: 'test@example.com');
  }
  
  Future<bool> saveUser(User user) async {
    // Implementation would go here
    return true;
  }
}
'''
        
        await manager.execute_tool(
            "file",
            operation="write", 
            file_path="lib/services/user_service.dart",
            content=user_service
        )
        
        # Create test file
        user_test = '''
import 'package:flutter_test/flutter_test.dart';
import '../lib/models/user.dart';
import '../lib/services/user_service.dart';

void main() {
  group('User Model Tests', () {
    test('should create user from JSON', () {
      final json = {'id': '1', 'name': 'Test', 'email': 'test@example.com'};
      final user = User.fromJson(json);
      
      expect(user.id, '1');
      expect(user.name, 'Test');
      expect(user.email, 'test@example.com');
    });
  });
  
  group('User Service Tests', () {
    test('should return user', () async {
      final service = UserService();
      final user = await service.getUser('1');
      
      expect(user, isNotNull);
      expect(user!.id, '1');
    });
  });
}
'''
        
        await manager.execute_tool(
            "file",
            operation="write",
            file_path="test/unit/user_test.dart",
            content=user_test
        )
        
        # Verify all files were created
        files_to_check = [
            "lib/models/user.dart",
            "lib/services/user_service.dart", 
            "test/unit/user_test.dart"
        ]
        
        for file_path in files_to_check:
            result = await manager.execute_tool(
                "file",
                operation="exists",
                path=file_path
            )
            assert result.status == ToolStatus.SUCCESS
            assert result.data["exists"] is True
        
        # Search for all Dart files
        result = await manager.execute_tool(
            "file",
            operation="search",
            pattern="**/*.dart"
        )
        assert result.status == ToolStatus.SUCCESS
        dart_files = result.data["files"]
        assert len(dart_files) >= 3
    
    @pytest.mark.asyncio
    async def test_error_handling_across_tools(self, temp_directory):
        """Test error handling when using multiple tools."""
        manager = ToolManager(temp_directory)
        
        # Try to read non-existent file
        result = await manager.execute_tool(
            "file",
            operation="read",
            file_path="nonexistent.dart"
        )
        assert result.status in [ToolStatus.ERROR, ToolStatus.WARNING]
        
        # Try to execute invalid command
        result = await manager.execute_command("invalid_command_that_does_not_exist")
        assert result.status == ToolStatus.ERROR
        
        # Try to use non-existent tool
        result = await manager.execute_tool("nonexistent_tool")
        assert result.status == ToolStatus.ERROR
        assert "not found" in result.error
        
        # Test recovery - create the file and try again
        await manager.execute_tool(
            "file",
            operation="write",
            file_path="test.dart",
            content="// Test content"
        )
        
        result = await manager.execute_tool(
            "file",
            operation="read",
            file_path="test.dart"
        )
        assert result.status == ToolStatus.SUCCESS
        assert "Test content" in result.output
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_operations(self, temp_directory):
        """Test concurrent tool operations."""
        manager = ToolManager(temp_directory)
        
        # Create multiple files concurrently
        async def create_file(filename, content):
            return await manager.execute_tool(
                "file",
                operation="write",
                file_path=filename,
                content=content
            )
        
        # Create tasks for concurrent file creation
        tasks = []
        for i in range(5):
            task = asyncio.create_task(
                create_file(f"file_{i}.dart", f"// Content for file {i}")
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all operations succeeded
        for result in results:
            assert result.status == ToolStatus.SUCCESS
        
        # Verify all files exist
        for i in range(5):
            result = await manager.execute_tool(
                "file",
                operation="exists",
                path=f"file_{i}.dart"
            )
            assert result.status == ToolStatus.SUCCESS
            assert result.data["exists"] is True
    
    @pytest.mark.asyncio
    async def test_analysis_tool_integration(self, temp_directory):
        """Test analysis tool integration with other tools."""
        manager = ToolManager(temp_directory)
        
        # Create a Dart file with potential issues
        problematic_dart = '''
import 'dart:io';

class BadPracticeExample {
  var _unsafeVariable;
  
  void riskyMethod(dynamic input) {
    print(input);
    // This is a comment about unsafe operations
    var result = input.toString();
  }
  
  void unusedMethod() {
    // This method is never called
  }
}
'''
        
        await manager.execute_tool(
            "file",
            operation="write",
            file_path="lib/bad_example.dart",
            content=problematic_dart
        )
        
        # Mock analysis results
        with patch.object(manager.tools["analysis"].terminal, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.status = ToolStatus.SUCCESS
            mock_result.output = "Analysis complete"
            mock_result.data = {
                "issues": [
                    {
                        "type": "warning",
                        "message": "Unused method detected",
                        "file": "lib/bad_example.dart",
                        "line": 12
                    }
                ]
            }
            mock_execute.return_value = mock_result
            
            # Run analysis
            result = await manager.execute_tool("analysis", operation="dart_analyze")
            assert result.status == ToolStatus.SUCCESS
        
        # Verify file was analyzed
        result = await manager.execute_tool(
            "file",
            operation="read",
            file_path="lib/bad_example.dart"
        )
        assert result.status == ToolStatus.SUCCESS
        assert "BadPracticeExample" in result.output

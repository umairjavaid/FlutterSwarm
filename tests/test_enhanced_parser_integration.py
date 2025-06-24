"""
Test suite for Enhanced LLM Response Parser integration with agents.
"""

import asyncio
import sys
import os
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser, parse_llm_response_for_agent


class MockAgent:
    """Mock agent for testing purposes."""
    
    def __init__(self):
        self.logger = logging.getLogger("MockAgent")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


def test_json_parsing():
    """Test JSON parsing strategy."""
    print("\n=== Testing JSON Parsing ===")
    
    agent = MockAgent()
    parser = EnhancedLLMResponseParser(agent.logger)
    
    # Test clean JSON
    json_response = """{
        "files": [
            {
                "path": "lib/main.dart",
                "content": "import 'package:flutter/material.dart';\\n\\nvoid main() {\\n  runApp(MyApp());\\n}",
                "description": "Main application entry point"
            }
        ]
    }"""
    
    parsed_files, error = parser.parse_llm_response(json_response, {"agent": agent})
    
    assert parsed_files, f"Failed to parse JSON: {error}"
    assert len(parsed_files) == 1, f"Expected 1 file, got {len(parsed_files)}"
    assert parsed_files[0]["path"] == "lib/main.dart", "Incorrect file path"
    print("✅ JSON parsing test passed")


def test_code_block_parsing():
    """Test code block parsing strategy."""
    print("\n=== Testing Code Block Parsing ===")
    
    agent = MockAgent()
    parser = EnhancedLLMResponseParser(agent.logger)
    
    # Test code block format
    code_block_response = '''
    Here are the Flutter files:
    
    ```dart:lib/main.dart
    import 'package:flutter/material.dart';
    
    void main() {
      runApp(MyApp());
    }
    
    class MyApp extends StatelessWidget {
      @override
      Widget build(BuildContext context) {
        return MaterialApp(
          title: 'Flutter Demo',
          home: HomePage(),
        );
      }
    }
    ```
    
    ```dart:lib/pages/home_page.dart
    import 'package:flutter/material.dart';
    
    class HomePage extends StatelessWidget {
      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: Text('Home')),
          body: Center(child: Text('Hello World')),
        );
      }
    }
    ```
    '''
    
    parsed_files, error = parser.parse_llm_response(code_block_response, {"agent": agent})
    
    assert parsed_files, f"Failed to parse code blocks: {error}"
    assert len(parsed_files) == 2, f"Expected 2 files, got {len(parsed_files)}"
    assert any("lib/main.dart" in f["path"] for f in parsed_files), "main.dart not found"
    assert any("home_page.dart" in f["path"] for f in parsed_files), "home_page.dart not found"
    print("✅ Code block parsing test passed")


def test_convenience_function():
    """Test the convenience function for agent integration."""
    print("\n=== Testing Convenience Function ===")
    
    agent = MockAgent()
    
    json_response = """{
        "files": [
            {
                "path": "lib/models/user.dart",
                "content": "class User {\\n  final String id;\\n  final String name;\\n  \\n  User({required this.id, required this.name});\\n}",
                "description": "User model class"
            }
        ]
    }"""
    
    parsed_files, error = parse_llm_response_for_agent(agent, json_response, {
        "project_id": "test_project"
    })
    
    assert parsed_files, f"Failed with convenience function: {error}"
    assert len(parsed_files) == 1, f"Expected 1 file, got {len(parsed_files)}"
    assert "User" in parsed_files[0]["content"], "User class not found in content"
    print("✅ Convenience function test passed")


def test_malformed_json_recovery():
    """Test recovery from malformed JSON."""
    print("\n=== Testing Malformed JSON Recovery ===")
    
    agent = MockAgent()
    parser = EnhancedLLMResponseParser(agent.logger)
    
    # Test JSON with extra text
    malformed_response = """Here's the JSON response you requested:
    
    {
        "files": [
            {
                "path": "lib/services/api_service.dart",
                "content": "class ApiService {\\n  // API implementation\\n}",
                "description": "API service class"
            }
        ]
    }
    
    This should work for your Flutter project!"""
    
    parsed_files, error = parser.parse_llm_response(malformed_response, {"agent": agent})
    
    assert parsed_files, f"Failed to parse malformed JSON: {error}"
    assert len(parsed_files) == 1, f"Expected 1 file, got {len(parsed_files)}"
    assert "ApiService" in parsed_files[0]["content"], "ApiService class not found"
    print("✅ Malformed JSON recovery test passed")


def test_structured_text_parsing():
    """Test structured text parsing strategy."""
    print("\n=== Testing Structured Text Parsing ===")
    
    agent = MockAgent()
    parser = EnhancedLLMResponseParser(agent.logger)
    
    # Test structured text format
    structured_response = '''
    File: lib/constants/app_constants.dart
    class AppConstants {
      static const String appName = 'My Flutter App';
      static const String version = '1.0.0';
    }
    
    File: lib/utils/helpers.dart
    class Helpers {
      static String formatDate(DateTime date) {
        return date.toString();
      }
    }
    '''
    
    parsed_files, error = parser.parse_llm_response(structured_response, {"agent": agent})
    
    assert parsed_files, f"Failed to parse structured text: {error}"
    assert len(parsed_files) >= 1, f"Expected at least 1 file, got {len(parsed_files)}"
    assert any("app_constants.dart" in f["path"] or "helpers.dart" in f["path"] for f in parsed_files), "Neither expected file found"
    print("✅ Structured text parsing test passed")


def run_all_tests():
    """Run all parser integration tests."""
    print("🧪 Running Enhanced LLM Response Parser Integration Tests")
    print("=" * 60)
    
    try:
        test_json_parsing()
        test_code_block_parsing()
        test_convenience_function()
        test_malformed_json_recovery()
        test_structured_text_parsing()
        
        print("\n" + "=" * 60)
        print("🎉 All Enhanced Parser Integration Tests Passed!")
        print("The enhanced parser is ready for use across the codebase.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

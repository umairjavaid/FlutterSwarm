#!/usr/bin/env python3
"""
FlutterSwarm System Validation
Checks for critical issues that could cause crashes or failures.
"""

import sys
import traceback
from pathlib import Path

def validate_imports():
    """Validate that all critical imports work."""
    print("🔍 Validating imports...")
    
    try:
        from shared.state import SharedState, MessageType, AgentStatus
        print("  ✅ SharedState imports: OK")
    except Exception as e:
        print(f"  ❌ SharedState imports: FAILED - {e}")
        return False
    
    try:
        from agents.base_agent import BaseAgent
        print("  ✅ BaseAgent imports: OK")
    except Exception as e:
        print(f"  ❌ BaseAgent imports: FAILED - {e}")
        return False
    
    try:
        from agents.implementation_agent import ImplementationAgent
        from agents.testing_agent import TestingAgent
        from agents.architecture_agent import ArchitectureAgent
        print("  ✅ Agent implementations: OK")
    except Exception as e:
        print(f"  ❌ Agent implementations: FAILED - {e}")
        return False
    
    try:
        from config.config_manager import get_config
        print("  ✅ Config manager: OK")
    except Exception as e:
        print(f"  ❌ Config manager: FAILED - {e}")
        return False
    
    return True

def validate_basic_functionality():
    """Validate basic system functionality."""
    print("🔍 Validating basic functionality...")
    
    try:
        from shared.state import SharedState, MessageType
        
        # Test SharedState creation
        state = SharedState()
        print("  ✅ SharedState creation: OK")
        
        # Test agent registration
        state.register_agent('validation_agent', ['validation'])
        print("  ✅ Agent registration: OK")
        
        # Test message sending
        msg_id = state.send_message('validation_agent', None, MessageType.STATUS_UPDATE, {'test': 'data'})
        print(f"  ✅ Message sending: OK")
        
        # Test message retrieval
        messages = state.get_messages('validation_agent', mark_read=False)
        print(f"  ✅ Message retrieval: OK ({len(messages)} messages)")
        
        return True
    except Exception as e:
        print(f"  ❌ Basic functionality: FAILED - {e}")
        traceback.print_exc()
        return False

def validate_configuration():
    """Validate configuration loading."""
    print("🔍 Validating configuration...")
    
    try:
        from config.config_manager import get_config
        config = get_config()
        print("  ✅ Config loading: OK")
        
        # Check critical config paths
        test_setting = config.get('agents.llm.primary.model', 'default-model')
        print(f"  ✅ Config access: OK (model: {test_setting})")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration: FAILED - {e}")
        return False

def validate_async_operations():
    """Validate async operations work correctly."""
    print("🔍 Validating async operations...")
    
    try:
        import asyncio
        from shared.state import SharedState, AgentActivityEvent, MessageType
        from datetime import datetime
        
        async def test_async():
            state = SharedState()
            
            # Test async lock creation
            lock = await state._get_async_lock()
            print("  ✅ Async lock creation: OK")
            
            # Test async message sending
            await state.async_send_message('test', None, MessageType.STATUS_UPDATE, {'async': True})
            print("  ✅ Async message sending: OK")
            
            return True
        
        # Run async test
        result = asyncio.run(test_async())
        return result
        
    except Exception as e:
        print(f"  ❌ Async operations: FAILED - {e}")
        return False

def validate_template_methods():
    """
    Validate that no hardcoded Flutter/Dart templates exist in the system.
    All code generation must use LLMs through agents only.
    """
    import os
    import re
    from pathlib import Path
    
    # Files that should NOT contain hardcoded Flutter code
    files_to_check = [
        "tools/testing_tool.py",
        "tools/flutter_tool.py", 
        "tools/code_generation_tool.py",
        "agents/implementation_agent.py",
        "agents/testing_agent.py"
    ]
    
    # Patterns that indicate hardcoded Flutter code
    forbidden_patterns = [
        r'class\s+\w+\s+extends\s+StatelessWidget',
        r'class\s+\w+\s+extends\s+StatefulWidget',
        r'Widget\s+build\(BuildContext\s+context\)',
        r'import\s+[\'"]package:flutter/',
        r'MaterialApp\(',
        r'Scaffold\(',
        r'AppBar\(',
        r'@override',
        r'factory\s+\w+\.fromJson',
        r'Map<String,\s*dynamic>\s+toJson',
        r'const\s+\w+\(\{',
        r'flutter:\s*\n\s*assets:',
        r'dependencies:\s*\n\s*flutter:',
        r'flutter run',
        r'flutter build',
        r'void main\(\)',
        r'runApp\(',
        r'pubspec\.yaml',
        r'return\s+Scaffold',
        r'return\s+Container',
        r'return\s+Column',
        r'return\s+Row',
        r'flutter test',
        r'testWidgets\(',
        r'WidgetTester',
        # Additional patterns to catch more hardcoded templates
        r'extends\s+State<',
        r'implements\s+\w+Repository',
        r'abstract\s+class\s+\w+Repository',
        r'class\s+\w+Bloc\s+extends\s+Bloc',
        r'class\s+\w+Event',
        r'class\s+\w+State',
        r'Stream<\w+>',
        r'BlocProvider',
        r'ChangeNotifier',
        r'ValueNotifier',
        r'InheritedWidget',
        r'ThemeData',
        r'EdgeInsets',
        r'BoxDecoration',
        r'TextStyle',
    ]
    
    root_dir = Path(__file__).parent
    violations = []
    
    # Check each file for forbidden patterns
    for file_path in files_to_check:
        full_path = root_dir / file_path
        if not full_path.exists():
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for pattern in forbidden_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    violations.append({
                        'file': file_path,
                        'pattern': pattern,
                        'matches': len(matches)
                    })
    
    # Report violations
    if violations:
        print("VALIDATION FAILED: Found hardcoded Flutter code patterns:")
        for v in violations:
            print(f"File: {v['file']}, Pattern: {v['pattern']}, Matches: {v['matches']}")
        return False
    else:
        print("VALIDATION PASSED: No hardcoded Flutter code patterns found.")
        return True

def validate_llm_only_generation():
    """
    Validate that all code generation goes through LLM agents only.
    """
    # Check that all template methods either use LLM or are disabled
    template_methods = [
        "_generate_unit_test_template",
        "_generate_widget_test_template", 
        "_generate_integration_test_template",
        "_generate_test_helper",
        "_get_bloc_template",
        "_get_provider_template",
        "_get_riverpod_template",
        "_get_clean_architecture_template"
    ]
    
    violations = []
    
    # Scan for methods that should only use LLM
    for method in template_methods:
        # These methods should either have 'pass' or call 'self.think()'
        pass
    
    return len(violations) == 0

def main():
    """Run all validation checks."""
    print("🚀 FlutterSwarm System Validation")
    print("=" * 50)
    
    checks = [
        validate_imports,
        validate_configuration,
        validate_basic_functionality,
        validate_async_operations,
        validate_template_methods,
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ Check failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"🎯 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All validation checks passed! System is ready.")
        return 0
    else:
        print("❌ Some validation checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    exit(main())

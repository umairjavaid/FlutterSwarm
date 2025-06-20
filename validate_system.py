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
    """Validate that template methods are implemented."""
    print("🔍 Validating template methods...")
    
    try:
        # Set dummy API key to avoid config issues
        import os
        original_key = os.environ.get('ANTHROPIC_API_KEY')
        os.environ['ANTHROPIC_API_KEY'] = 'test-key-for-validation'
        
        # Import and test just the template methods without full agent initialization
        from agents.implementation_agent import ImplementationAgent
        
        # Create an instance - this may trigger the event loop issue
        agent = ImplementationAgent()
        
        # Access the template methods through the property
        templates = agent.flutter_templates
        
        # Check that templates exist and contain expected content
        assert "bloc" in templates
        assert "provider" in templates  
        assert "riverpod" in templates
        assert "clean_architecture" in templates
        
        bloc_template = templates["bloc"]
        assert isinstance(bloc_template, str) and "Bloc" in bloc_template
        
        print("  ✅ Template methods: OK")
        
        # Restore original API key
        if original_key:
            os.environ['ANTHROPIC_API_KEY'] = original_key
        elif 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
            
        return True
        
    except Exception as e:
        print(f"  ❌ Template methods: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

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

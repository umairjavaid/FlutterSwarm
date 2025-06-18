#!/usr/bin/env python3
"""
Test script to verify ImplementationAgent fix
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agents.implementation_agent import ImplementationAgent
    print("✅ Successfully imported ImplementationAgent")
    
    # Create an instance
    agent = ImplementationAgent()
    print("✅ Successfully created ImplementationAgent instance")
    
    # Check for the previously missing methods
    required_methods = [
        '_analyze_new_file',
        '_handle_qa_issue', 
        '_provide_implementation_guidance',
        '_handle_refactor_request',
        '_start_implementation'
    ]
    
    missing_methods = []
    for method in required_methods:
        if hasattr(agent, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ Method {method} missing")
            missing_methods.append(method)
    
    if not missing_methods:
        print("\n🎉 ALL METHODS FIXED SUCCESSFULLY!")
        print("The ImplementationAgent errors should be resolved.")
    else:
        print(f"\n❌ Still missing methods: {missing_methods}")
        
except Exception as e:
    print(f"❌ Error testing ImplementationAgent: {e}")
    import traceback
    traceback.print_exc()

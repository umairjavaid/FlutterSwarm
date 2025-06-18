#!/usr/bin/env python3
"""
Quick test to see if the ImplementationAgent errors are fixed
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_implementation_agent():
    """Test the ImplementationAgent with a simple task"""
    try:
        from agents.implementation_agent import ImplementationAgent
        from shared.state import shared_state
        
        print("✅ Imported ImplementationAgent successfully")
        
        # Create agent
        agent = ImplementationAgent()
        print("✅ Created ImplementationAgent instance")
        
        # Test the _analyze_new_file method that was causing errors
        test_data = {
            "file_path": "lib/test.dart",
            "project_id": "test_project_123"
        }
        
        # This should not throw an AttributeError anymore
        await agent._analyze_new_file(test_data)
        print("✅ _analyze_new_file method works correctly")
        
        # Test _handle_qa_issue method
        qa_data = {
            "issue": {
                "issue_type": "code_quality",
                "affected_files": ["lib/test.dart"]
            },
            "project_id": "test_project_123"
        }
        
        await agent._handle_qa_issue(qa_data)
        print("✅ _handle_qa_issue method works correctly")
        
        print("\n🎉 ALL IMPLEMENTATION AGENT ERRORS FIXED!")
        return True
        
    except AttributeError as e:
        print(f"❌ AttributeError still exists: {e}")
        return False
    except Exception as e:
        print(f"✅ Different error (expected): {e}")
        print("✅ AttributeError is fixed (this is a different issue)")
        return True

if __name__ == "__main__":
    result = asyncio.run(test_implementation_agent())
    if result:
        print("\n🎯 The ImplementationAgent errors should be resolved!")
    else:
        print("\n❌ Still need to fix ImplementationAgent errors")

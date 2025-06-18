#!/usr/bin/env python3
"""
Simple test script to debug FlutterSwarm issues
"""

import sys
import os
sys.path.insert(0, '/workspaces/FlutterSwarm')

print("Starting debug test...")

try:
    print("1. Testing basic imports...")
    from dotenv import load_dotenv
    print("✅ dotenv imported")
    
    print("2. Loading environment...")
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"✅ API key loaded: {len(api_key) if api_key else 0} chars")
    
    print("3. Testing langchain-anthropic...")
    from langchain_anthropic import ChatAnthropic
    print("✅ ChatAnthropic imported")
    
    print("4. Testing shared state...")
    from shared.state import shared_state
    print("✅ shared_state imported")
    
    print("5. Testing base agent import...")
    from agents.base_agent import BaseAgent
    print("✅ BaseAgent imported")
    
    print("6. Testing orchestrator agent...")
    # Don't initialize yet, just import
    from agents.orchestrator_agent import OrchestratorAgent
    print("✅ OrchestratorAgent imported")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()

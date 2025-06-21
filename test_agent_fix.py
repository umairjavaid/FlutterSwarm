#!/usr/bin/env python3
"""
Quick test to verify agent initialization fix.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/home/umair/Desktop/FlutterSwarm')

# Import agent_logger for error logging
try:
    from monitoring.agent_logger import agent_logger
except ImportError:
    agent_logger = None

try:
    print("🧪 Testing agent creation fix...")
    
    from agents.testing_agent import TestingAgent
    print("✅ TestingAgent import successful")
    
    print("Creating TestingAgent instance...")
    agent = TestingAgent()
    print("✅ TestingAgent created successfully!")
    
    print(f"Agent ID: {agent.agent_id}")
    print(f"Monitoring task initialized: {hasattr(agent, '_monitoring_task')}")
    print(f"Monitoring enabled: {getattr(agent, '_monitoring_enabled', False)}")
    
    # Test other agents too
    from agents.architecture_agent import ArchitectureAgent
    arch_agent = ArchitectureAgent()
    print("✅ ArchitectureAgent created successfully!")
    
    from agents.implementation_agent import ImplementationAgent  
    impl_agent = ImplementationAgent()
    print("✅ ImplementationAgent created successfully!")
    
    print("\n🎉 All agents created successfully - fix worked!")
    
except Exception as e:
    if agent_logger:
        agent_logger.log_error(
            agent_id="system", 
            error_type="TestAgentFixError", 
            error_message=str(e), 
            context={"file": __file__}, 
            exception=e
        )
    import traceback
    traceback.print_exc()
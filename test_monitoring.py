#!/usr/bin/env python3
"""
Quick test script for FlutterSwarm monitoring system.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from monitoring import agent_logger, live_display, build_monitor
from shared.state import AgentStatus, MessageType

def test_monitoring_components():
    """Test the monitoring components independently."""
    print("🧪 Testing FlutterSwarm Monitoring Components\n")
    
    # Test 1: Agent Logger
    print("1️⃣ Testing Agent Logger...")
    agent_logger.log_agent_status_change(
        "test_agent", AgentStatus.IDLE, AgentStatus.WORKING, "Creating test files"
    )
    agent_logger.log_tool_usage(
        "test_agent", "flutter", "create", "success", 2.5,
        {"project_name": "test_app"}, {"output": "Project created"}, None
    )
    agent_logger.log_project_event(
        "test_project", "build_start", "Starting test build"
    )
    print("   ✅ Agent logger working correctly")
    
    # Test 2: Live Display
    print("\n2️⃣ Testing Live Display...")
    live_display.log_agent_activity("test_agent", "Creating project structure")
    live_display.log_tool_usage("test_agent", "flutter", "create", "success")
    live_display.log_message("test_agent", "orchestrator", "STATUS_UPDATE", {"status": "working"})
    print("   ✅ Live display data logged")
    
    # Test 3: Build Monitor (without starting monitoring loop)
    print("\n3️⃣ Testing Build Monitor...")
    # Test individual logging methods without starting the full monitoring
    build_monitor.log_agent_status_change(
        "test_agent", AgentStatus.IDLE, AgentStatus.WORKING, "Building app"
    )
    build_monitor.log_tool_usage(
        "test_agent", "flutter", "build", "success", 5.2
    )
    print("   ✅ Build monitor logging functions working")
    
    # Test 4: Export functionality
    print("\n4️⃣ Testing Export Functionality...")
    log_file = agent_logger.export_logs_to_json("test_logs.json")
    print(f"   ✅ Logs exported to: {log_file}")
    
    print("\n🎉 All monitoring components working correctly!")
    print("💡 You can now use the monitoring system during Flutter builds.")

def test_live_display_demo():
    """Run a short live display demo."""
    print("\n🔍 Starting 5-second live display demo...")
    print("💡 This shows what you'll see during Flutter builds:\n")
    
    # Start live display
    live_display.start()
    
    # Simulate some agent activities
    import time
    import threading
    
    def simulate_activities():
        activities = [
            ("orchestrator", "Planning project structure"),
            ("architecture", "Designing Flutter architecture"),
            ("implementation", "Generating main.dart"),
            ("implementation", "Creating feature modules"),
            ("testing", "Writing unit tests"),
            ("security", "Scanning for vulnerabilities"),
            ("devops", "Setting up CI/CD pipeline"),
        ]
        
        tools = [
            ("orchestrator", "analysis", "project_structure", "success"),
            ("architecture", "flutter", "create", "success"),
            ("implementation", "file", "write", "success"),
            ("testing", "flutter", "test", "success"),
            ("security", "analysis", "security_scan", "success"),
        ]
        
        for i, (agent, activity) in enumerate(activities):
            time.sleep(0.7)
            live_display.log_agent_activity(agent, activity)
            
            # Add tool usage occasionally
            if i < len(tools):
                tool_agent, tool_name, operation, status = tools[i]
                live_display.log_tool_usage(tool_agent, tool_name, operation, status)
            
            # Add some messages
            if i % 2 == 0:
                live_display.log_message(agent, "orchestrator", "STATUS_UPDATE", activity)
    
    # Run simulation in background
    simulation_thread = threading.Thread(target=simulate_activities, daemon=True)
    simulation_thread.start()
    
    # Let it run for 5 seconds
    time.sleep(5)
    
    # Stop live display
    live_display.stop()
    
    print("\n✅ Live display demo completed!")
    print("🔧 This is what you'll see when building Flutter apps with FlutterSwarm.")

if __name__ == "__main__":
    try:
        # Run basic component tests
        test_monitoring_components()
        
        # Ask user if they want to see live display demo
        response = input("\n❓ Would you like to see a live display demo? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            test_live_display_demo()
        
        print("\n🚀 Monitoring system is ready!")
        print("💡 Run 'python demo_live_monitoring.py' for a full demo with Flutter build")
        
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

"""
FlutterSwarm - Multi-Agent Flutter Development System
Now powered by LangGraph for better orchestration and state management.
"""

# Initialize comprehensive logging first
from utils.comprehensive_logging import setup_comprehensive_logging, log_startup_banner

# Import the new LangGraph-based implementation
from langgraph_swarm import FlutterSwarmGovernance, run_flutter_swarm_governance

# For backward compatibility, alias the classes
FlutterSwarm = FlutterSwarmGovernance
LangGraphFlutterSwarm = FlutterSwarmGovernance

# Alias the run function
run_flutter_swarm = run_flutter_swarm_governance

# Export main functionality
__all__ = ['FlutterSwarm', 'LangGraphFlutterSwarm', 'run_flutter_swarm']

if __name__ == "__main__":
    # Example usage with the new LangGraph system
    import asyncio
    
    async def main():
        # Initialize comprehensive logging
        try:
            setup_info = setup_comprehensive_logging()
            log_startup_banner()
            print(f"✅ Comprehensive logging initialized - Session ID: {setup_info['session_id']}")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize comprehensive logging: {e}")
        
        # Create LangGraph FlutterSwarm instance
        swarm = FlutterSwarm()
        
        # Build a sample project (creation is handled automatically)
        result = await swarm.build_project(
            name="TodoApp",
            description="A Flutter todo application with user authentication",
            requirements=[
                "User authentication",
                "Todo CRUD operations", 
                "Offline synchronization",
                "Push notifications",
                "Dark mode support"
            ],
            features=["auth", "crud", "offline_sync", "notifications"],
            platforms=["android", "ios", "web"]
        )
        
        print(f"🎉 Build result: {result}")
    
    asyncio.run(main())

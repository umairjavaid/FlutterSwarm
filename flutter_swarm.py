"""
FlutterSwarm - Multi-Agent Flutter Development System
Now powered by LangGraph for better orchestration and state management.
"""

# Import the new LangGraph-based implementation
from langgraph_swarm import LangGraphFlutterSwarm, run_flutter_swarm

# For backward compatibility, alias the classes
FlutterSwarm = LangGraphFlutterSwarm

# Export main functionality
__all__ = ['FlutterSwarm', 'run_flutter_swarm']

if __name__ == "__main__":
    # Example usage with the new LangGraph system
    import asyncio
    
    async def main():
        # Create LangGraph FlutterSwarm instance
        swarm = FlutterSwarm()
        
        # Create a sample project
        project_id = swarm.create_project(
            name="TodoApp",
            description="A Flutter todo application with user authentication",
            requirements=[
                "User authentication",
                "Todo CRUD operations", 
                "Offline synchronization",
                "Push notifications",
                "Dark mode support"
            ],
            features=["auth", "crud", "offline_sync", "notifications"]
        )
        
        # Build the project using LangGraph workflow
        result = await swarm.build_project(
            project_id=project_id,
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

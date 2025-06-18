#!/usr/bin/env python3
"""
Example usage of FlutterSwarm.
Demonstrates how to create and build Flutter projects using the multi-agent system.
"""

import asyncio
import time
from flutter_swarm import FlutterSwarm

async def example_todo_app():
    """Example: Create a Todo app with authentication."""
    print("🐝 FlutterSwarm Example: Todo App with Authentication")
    print("=" * 60)
    
    # Create FlutterSwarm instance
    swarm = FlutterSwarm()
    
    # Create a todo app project
    project_id = swarm.create_project(
        name="TodoMaster",
        description="A comprehensive todo application with user authentication, offline sync, and collaboration features",
        requirements=[
            "User registration and authentication",
            "Todo CRUD operations with categories",
            "Offline synchronization", 
            "Real-time collaboration",
            "Push notifications",
            "Dark/light theme support",
            "Export/import functionality",
            "Search and filtering",
            "Due date reminders",
            "Attachment support"
        ],
        features=[
            "auth", "crud", "offline_sync", "notifications", 
            "theming", "collaboration", "search", "export"
        ]
    )
    
    print(f"\n📋 Project created with ID: {project_id}")
    
    # Start the swarm (in a real app, you might want to handle this differently)
    print("\n🚀 Starting agent swarm...")
    
    # Create tasks to run swarm and build project concurrently
    swarm_task = asyncio.create_task(swarm.start())
    
    # Give agents time to start
    await asyncio.sleep(2)
    
    # Start building the project
    print("\n🏗️  Starting build process...")
    
    try:
        result = await asyncio.wait_for(
            swarm.build_project(
                project_id, 
                platforms=["android", "ios", "web"],
                ci_system="github_actions"
            ),
            timeout=300  # 5 minutes timeout for demo
        )
        
        print("\n🎉 Build completed successfully!")
        print_build_results(result)
        
    except asyncio.TimeoutError:
        print("\n⏰ Build timeout reached (this is expected in demo mode)")
        print("📊 Showing current progress...")
        
        # Show current status
        status = swarm.get_project_status(project_id)
        print_project_status(status)
    
    finally:
        print("\n🛑 Stopping swarm...")
        await swarm.stop()

async def example_ecommerce_app():
    """Example: Create an e-commerce app."""
    print("\n\n🐝 FlutterSwarm Example: E-commerce App")
    print("=" * 60)
    
    swarm = FlutterSwarm()
    
    project_id = swarm.create_project(
        name="ShopifyMobile",
        description="A full-featured e-commerce mobile application with advanced features",
        requirements=[
            "Product catalog with search and filtering",
            "Shopping cart and checkout process",
            "User accounts and profiles",
            "Payment integration (Stripe, PayPal)",
            "Order tracking and history",
            "Push notifications for offers",
            "Wishlist and favorites",
            "Product reviews and ratings",
            "Social sharing",
            "Multi-language support",
            "Admin panel integration"
        ],
        features=[
            "catalog", "cart", "checkout", "payments", "orders", 
            "notifications", "reviews", "social", "i18n", "admin"
        ]
    )
    
    print(f"📋 E-commerce project created: {project_id}")
    
    # Show how to monitor specific agents
    print("\n👀 Monitoring agent activity...")
    
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(2)
    
    # Monitor for 30 seconds
    for i in range(6):
        await asyncio.sleep(5)
        agent_status = swarm.get_agent_status()
        print(f"\n📊 Status update {i+1}/6:")
        
        for agent_id, status in agent_status.items():
            status_emoji = {
                'idle': '💤',
                'working': '🔄',
                'waiting': '⏳', 
                'completed': '✅',
                'error': '❌'
            }.get(status['status'], '❓')
            
            task_info = f" - {status['current_task']}" if status['current_task'] else ""
            print(f"  {agent_id}: {status_emoji} {status['status']}{task_info}")
    
    await swarm.stop()

def print_build_results(result):
    """Print formatted build results."""
    print("\n📋 Build Summary:")
    print(f"  • Status: {result.get('status', 'Unknown')}")
    print(f"  • Files Created: {result.get('files_created', 0)}")
    print(f"  • Architecture Decisions: {result.get('architecture_decisions', 0)}")
    print(f"  • Security Findings: {len(result.get('security_findings', []))}")
    print(f"  • Documentation Files: {len(result.get('documentation', []))}")
    
    if result.get('test_results'):
        print("\n🧪 Test Results:")
        for test_type, results in result['test_results'].items():
            print(f"  • {test_type}: {results.get('status', 'Unknown')}")
    
    if result.get('deployment_config'):
        print(f"\n🚀 Deployment: {result['deployment_config'].get('status', 'Not configured')}")

def print_project_status(status):
    """Print formatted project status."""
    if 'error' in status:
        print(f"❌ Error: {status['error']}")
        return
    
    project = status['project']
    print(f"\n📋 Project: {project['name']}")
    print(f"  • Phase: {project['current_phase']}")
    print(f"  • Progress: {project['progress']:.1%}")
    print(f"  • Files: {project['files_created']}")
    
    print("\n🤖 Agent Status:")
    for agent_id, agent_info in status['agents'].items():
        status_emoji = {
            'idle': '💤',
            'working': '🔄',
            'waiting': '⏳',
            'completed': '✅', 
            'error': '❌'
        }.get(agent_info['status'], '❓')
        
        task_info = f" ({agent_info['current_task']})" if agent_info['current_task'] else ""
        print(f"  • {agent_id}: {status_emoji} {agent_info['status']}{task_info}")

async def main():
    """Run all examples."""
    print("🐝 Welcome to FlutterSwarm Examples!")
    print("This demonstrates the multi-agent Flutter development system.\n")
    
    try:
        # Run todo app example
        await example_todo_app()
        
        # Add delay between examples
        await asyncio.sleep(3)
        
        # Run e-commerce app example  
        await example_ecommerce_app()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
    
    print("\n✨ Thanks for trying FlutterSwarm!")
    print("🔗 Visit https://github.com/yourorg/flutterswarm for more information")

if __name__ == "__main__":
    asyncio.run(main())

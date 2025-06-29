#!/usr/bin/env python3
"""
Example usage of FlutterSwarm.
Demonstrates how to create and build Flutter projects using the multi-agent system.
ALL CODE IS GENERATED BY LLM AGENTS - ZERO HARDCODED TEMPLATES.
"""

import asyncio
import time

# Initialize comprehensive logging first
from utils.comprehensive_logging import setup_comprehensive_logging, log_startup_banner

from flutter_swarm import FlutterSwarm
from config.config_manager import get_config

async def example_todo_app():
    """Example: Create a Todo app with authentication - 100% LLM-generated."""
    # Get configuration
    config = get_config()
    messages = config.get_messages_config()
    
    welcome_msg = messages.get('welcome', '🐝 Welcome to FlutterSwarm!')
    print(welcome_msg.replace('Welcome to FlutterSwarm!', 'FlutterSwarm Example: Todo App with Authentication (100% LLM-Generated)'))
    
    # Get console width from config
    console_width = config.get_cli_setting('console_width') or 60
    print("=" * console_width)
    
    # Create FlutterSwarm instance
    swarm = FlutterSwarm()
    
    # Build the todo app project (creation is handled automatically)
    print("\n🏗️  Starting build process...")
    
    default_timeout = config.get_examples_config().get('default_timeout', 300)
    
    try:
        result = await asyncio.wait_for(
            swarm.build_project(
                name="TodoMaster",
                description="A comprehensive todo application with user authentication, offline sync, and collaboration features - ALL CODE GENERATED BY AI AGENTS USING LLMs",
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
                ],
                platforms=["android", "ios", "web"],
                ci_system="github_actions"
            ),
            timeout=default_timeout  # Configurable timeout
        )
        print("\n🎉 Build completed successfully!")
        print_build_results(result)
        print(f"\n📋 Project ID: {result.get('project_id', 'unknown')}")
    except asyncio.TimeoutError:
        print("\n⏰ Build timeout reached (this is expected in demo mode)")
        print("📊 Showing current progress...")
        # Show current status (if available)
        # status = swarm.get_project_status(project_id)  # Not needed anymore
        # print_project_status(status)
    finally:
        print("\n🛑 Stopping swarm...")
        await swarm.stop()

async def example_ecommerce_app():
    """Example: Create an e-commerce app - 100% LLM-generated."""
    # Get configuration
    config = get_config()
    messages = config.get_messages_config()
    
    welcome_msg = messages.get('welcome', '🐝 Welcome to FlutterSwarm!')
    print(welcome_msg.replace('Welcome to FlutterSwarm!', 'FlutterSwarm Example: E-commerce App (100% LLM-Generated)'))
    
    # Get console width from config
    console_width = config.get_cli_setting('console_width') or 60
    print("=" * console_width)
    
    swarm = FlutterSwarm()
    
    result = await swarm.build_project(
        name="ShopifyMobile",
        description="A full-featured e-commerce mobile application with advanced features - ALL CODE GENERATED BY AI AGENTS USING LLMs",
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
    
    project_id = result.get('project_id')
    
    print(f"📋 E-commerce project created: {project_id}")
    print("🎯 ALL Flutter/Dart code will be generated by LLM agents")
    print("🚫 ZERO hardcoded templates will be used")
    
    # Show how to monitor specific agents
    print("\n👀 Monitoring agent activity...")
    
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(2)
    
    # Get monitoring settings from config
    monitoring_config = config.get_monitoring_config()
    monitoring_rounds = monitoring_config.get('thresholds', {}).get('max_monitoring_rounds', 5)
    sleep_interval = config.get_interval_setting('status_update')
    
    # Monitor for configured duration
    for i in range(monitoring_rounds + 1):  # +1 to match original 6 rounds with default of 5
        await asyncio.sleep(sleep_interval)
        agent_status = swarm.get_agent_status()
        print(f"\n📊 Status update {i+1}/{monitoring_rounds + 1}:")
        
        # Get status icons from config
        display_config = config.get_display_config()
        status_icons = display_config.get('status_icons', {})
        
        for agent_id, status in agent_status.items():
            status_emoji = status_icons.get(status.get('status', 'unknown'), '❓')
            
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
    # Initialize comprehensive logging
    try:
        setup_info = setup_comprehensive_logging()
        log_startup_banner()
        print(f"✅ Comprehensive logging initialized - Session ID: {setup_info['session_id']}")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize comprehensive logging: {e}")
    
    print("🐝 Welcome to FlutterSwarm Examples!")
    print("This demonstrates the multi-agent Flutter development system.")
    print("🎯 ALL CODE IS GENERATED BY LLM AGENTS - ZERO HARDCODED TEMPLATES")
    print("🚫 NO FLUTTER/DART CODE IS HARDCODED ANYWHERE IN THE SYSTEM\n")
    
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
    print("🎯 Remember: ALL code generation is handled by LLM agents")
    print("🔗 Visit https://github.com/yourorg/flutterswarm for more information")

if __name__ == "__main__":
    asyncio.run(main())

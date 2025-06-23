#!/usr/bin/env python3
"""
Advanced FlutterSwarm examples demonstrating complex scenarios.
"""

import asyncio

# Initialize comprehensive logging first
from utils.comprehensive_logging import setup_comprehensive_logging, log_startup_banner

from flutter_swarm import FlutterSwarm

async def example_enterprise_app():
    """Example: Enterprise application with complex requirements."""
    print("🏢 FlutterSwarm Advanced Example: Enterprise Application")
    print("=" * 70)
    
    swarm = FlutterSwarm()
    
    # Complex enterprise app
    result = await swarm.build_project(
        name="EnterpriseHub",
        description="Enterprise-grade application with microservices architecture, advanced security, and scalability",
        requirements=[
            "Microservices architecture integration",
            "SSO authentication with SAML/OAuth2",
            "Role-based access control (RBAC)",
            "Real-time data synchronization",
            "Offline-first architecture",
            "End-to-end encryption",
            "Audit logging and compliance",
            "Multi-tenant support",
            "Advanced analytics and reporting",
            "API rate limiting and throttling",
            "Automated testing and CI/CD",
            "Performance monitoring and alerting",
            "Disaster recovery capabilities",
            "Internationalization (i18n)",
            "Accessibility compliance (WCAG 2.1)"
        ],
        features=[
            "microservices", "sso", "rbac", "realtime", "offline", 
            "encryption", "audit", "multitenancy", "analytics", 
            "rate_limiting", "cicd", "monitoring", "disaster_recovery",
            "i18n", "accessibility"
        ],
        platforms=["android", "ios", "web"]
    )
    project_id = result.get('project_id', 'unknown')
    print(f"📋 Enterprise project created: {project_id}")
    
    # Start swarm
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(3)
    
    # Monitor detailed progress
    print("\n📊 Monitoring detailed agent collaboration...")
    
    for round_num in range(5):
        print(f"\n🔄 Monitoring Round {round_num + 1}/5")
        
        # Get detailed status
        status = swarm.get_project_status(project_id)
        
        if 'project' in status:
            project = status['project'] 
            print(f"  📋 Project Phase: {project['current_phase']} ({project['progress']:.1%})")
            
            # Show active collaborations
            active_agents = [
                agent_id for agent_id, agent_info in status['agents'].items()
                if agent_info['status'] == 'working'
            ]
            
            if active_agents:
                print(f"  🤝 Active Collaborations: {', '.join(active_agents)}")
            
            # Show completed work
            print(f"  📁 Files Created: {project['files_created']}")
            print(f"  🏗️  Architecture Decisions: {project['architecture_decisions']}")
            print(f"  🔒 Security Findings: {project['security_findings']}")
        
        await asyncio.sleep(8)
    
    await swarm.stop()

async def example_gaming_app():
    """Example: Gaming application with real-time features."""
    print("\n\n🎮 FlutterSwarm Advanced Example: Gaming Application")
    print("=" * 70)
    
    swarm = FlutterSwarm()
    
    result = await swarm.build_project(
        name="MultiplayerArena",
        description="Real-time multiplayer gaming application with advanced graphics and social features",
        requirements=[
            "Real-time multiplayer networking",
            "WebSocket/Socket.IO integration",
            "Game state synchronization",
            "Custom game engine integration",
            "3D graphics and animations",
            "Physics simulation",
            "In-app purchases and monetization",
            "Player matchmaking system",
            "Leaderboards and achievements",
            "Chat and voice communication",
            "Replay system",
            "Anti-cheat mechanisms",
            "Cloud save synchronization",
            "Social media integration",
            "Tournament and event system"
        ],
        features=[
            "multiplayer", "websockets", "game_engine", "3d_graphics",
            "physics", "iap", "matchmaking", "leaderboards", "chat",
            "voice", "replay", "anticheat", "cloud_save", "social",
            "tournaments"
        ],
        platforms=["android", "ios", "web"]
    )
    project_id = result.get('project_id', 'unknown')
    print(f"🎮 Gaming project created: {project_id}")
    
    # Demonstrate agent specialization
    print("\n🎯 Demonstrating Agent Specialization...")
    
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(2)
    
    # Show how different agents handle gaming-specific challenges
    specializations = {
        "architecture": "Designing real-time networking architecture",
        "implementation": "Creating game engine integration",
        "performance": "Optimizing frame rates and memory usage",
        "security": "Implementing anti-cheat mechanisms",
        "testing": "Creating automated gameplay testing",
        "devops": "Setting up game server deployment",
        "documentation": "Creating player and developer guides"
    }
    
    for i in range(7):
        await asyncio.sleep(5)
        agent_status = swarm.get_agent_status()
        
        print(f"\n🔍 Agent Specialization Check {i+1}/7:")
        
        for agent_id, specialization in specializations.items():
            if agent_id in agent_status:
                status_info = agent_status[agent_id]
                status_emoji = {
                    'idle': '💤',
                    'working': '🔄',
                    'waiting': '⏳',
                    'completed': '✅',
                    'error': '❌'
                }.get(status_info['status'], '❓')
                
                print(f"  {agent_id}: {status_emoji} {specialization}")
    
    await swarm.stop()

async def example_healthcare_app():
    """Example: Healthcare application with strict compliance requirements."""
    print("\n\n🏥 FlutterSwarm Advanced Example: Healthcare Application")
    print("=" * 70)
    
    swarm = FlutterSwarm()
    
    result = await swarm.build_project(
        name="HealthVault",
        description="HIPAA-compliant healthcare application with telemedicine and patient management features",
        requirements=[
            "HIPAA compliance and audit trails",
            "End-to-end encryption for PHI",
            "Secure authentication and authorization",
            "Telemedicine video calling",
            "Electronic Health Records (EHR) integration",
            "Prescription management",
            "Appointment scheduling",
            "Patient portal features",
            "Provider dashboard",
            "Medical device integration",
            "Clinical decision support",
            "Billing and insurance integration",
            "Regulatory reporting",
            "Data backup and recovery",
            "Emergency access protocols"
        ],
        features=[
            "hipaa", "encryption", "telemedicine", "ehr", "prescriptions",
            "scheduling", "patient_portal", "provider_dashboard", 
            "medical_devices", "clinical_support", "billing", 
            "reporting", "backup", "emergency_access"
        ],
        platforms=["android", "ios", "web"]
    )
    project_id = result.get('project_id', 'unknown')
    print(f"🏥 Healthcare project created: {project_id}")
    
    # Focus on security and compliance
    print("\n🔒 Monitoring Security and Compliance Focus...")
    
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(3)
    
    # Track security-specific progress
    for i in range(6):
        await asyncio.sleep(6)
        status = swarm.get_project_status(project_id)
        
        print(f"\n🛡️  Security & Compliance Check {i+1}/6:")
        
        if 'project' in status:
            project = status['project']
            print(f"  📋 Current Phase: {project['current_phase']}")
            
            # Highlight security-focused agents
            security_agents = ['security', 'testing', 'devops', 'documentation']
            
            for agent_id in security_agents:
                if agent_id in status['agents']:
                    agent_info = status['agents'][agent_id]
                    task_info = agent_info.get('current_task', 'Idle')
                    
                    if 'security' in task_info.lower() or 'compliance' in task_info.lower():
                        print(f"  🔒 {agent_id}: Working on {task_info}")
                    elif agent_info['status'] == 'working':
                        print(f"  🔄 {agent_id}: {task_info}")
    
    await swarm.stop()

async def example_performance_optimization():
    """Example: Demonstrating performance optimization workflow."""
    print("\n\n⚡ FlutterSwarm Advanced Example: Performance Optimization")
    print("=" * 70)
    
    swarm = FlutterSwarm()
    
    # Create a performance-critical app
    result = await swarm.build_project(
        name="HighPerformanceApp",
        description="Performance-critical application requiring 60fps, low memory usage, and fast startup",
        requirements=[
            "60fps guarantee on all devices",
            "Sub-2-second app startup time",
            "Memory usage under 150MB",
            "Smooth animations and transitions",
            "Optimized image loading and caching",
            "Efficient list scrolling (10k+ items)",
            "Background processing optimization",
            "Battery usage optimization",
            "Network request optimization",
            "Code splitting and lazy loading",
            "Asset optimization and compression",
            "Platform-specific optimizations"
        ],
        features=[
            "performance", "optimization", "animations", "image_caching",
            "list_optimization", "background_processing", "battery_optimization",
            "network_optimization", "code_splitting", "asset_optimization"
        ],
        platforms=["android", "ios", "web"]
    )
    project_id = result.get('project_id', 'unknown')
    print(f"⚡ Performance-focused project created: {project_id}")
    
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(2)
    
    # Monitor performance optimization workflow
    print("\n📈 Monitoring Performance Optimization Workflow...")
    
    performance_metrics = []
    
    for i in range(8):
        await asyncio.sleep(4)
        
        # Get performance agent status specifically
        agent_status = swarm.get_agent_status('performance')
        
        if agent_status and 'error' not in agent_status:
            task = agent_status.get('current_task', 'Idle')
            progress = agent_status.get('progress', 0)
            
            performance_metrics.append({
                'round': i + 1,
                'task': task,
                'progress': progress
            })
            
            print(f"\n⚡ Performance Round {i+1}/8:")
            print(f"  🎯 Task: {task}")
            print(f"  📊 Progress: {progress:.1%}")
            
            # Simulate performance findings
            if i >= 2:
                findings = [
                    "Widget rebuild optimization needed",
                    "Image caching improvements identified", 
                    "List scrolling performance enhanced",
                    "Memory leak prevention implemented",
                    "Animation performance optimized"
                ]
                
                if i < len(findings) + 2:
                    print(f"  🔍 Finding: {findings[i-2]}")
    
    # Show performance summary
    print("\n📊 Performance Optimization Summary:")
    for metric in performance_metrics[-3:]:  # Show last 3 rounds
        print(f"  Round {metric['round']}: {metric['task']} ({metric['progress']:.1%})")
    
    await swarm.stop()

async def main():
    """Run advanced examples."""
    # Initialize comprehensive logging
    try:
        setup_info = setup_comprehensive_logging()
        log_startup_banner()
        print(f"✅ Comprehensive logging initialized - Session ID: {setup_info['session_id']}")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize comprehensive logging: {e}")
    
    print("🚀 FlutterSwarm Advanced Examples")
    print("These examples demonstrate complex, real-world scenarios.\n")
    
    try:
        # Run enterprise example
        await example_enterprise_app()
        
        await asyncio.sleep(2)
        
        # Run gaming example
        await example_gaming_app()
        
        await asyncio.sleep(2)
        
        # Run healthcare example  
        await example_healthcare_app()
        
        await asyncio.sleep(2)
        
        # Run performance optimization example
        await example_performance_optimization()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Advanced examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running advanced examples: {e}")
    
    print("\n✨ Advanced Examples Complete!")
    print("🎯 These examples showcase FlutterSwarm's ability to handle complex, real-world scenarios")
    print("🔗 For more examples, visit: https://github.com/yourorg/flutterswarm/examples")

if __name__ == "__main__":
    asyncio.run(main())

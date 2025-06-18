#!/usr/bin/env python3
"""
Create a Music App using FlutterSwarm with Quality Assurance
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flutter_swarm import FlutterSwarm
from config.config_manager import get_config

async def create_music_app():
    """Create a comprehensive music streaming application using FlutterSwarm."""
    # Get configuration
    config = get_config()
    app_config = config.get_application_config()
    music_config = app_config.get('examples', {}).get('music_app', {})
    messages = config.get_messages_config()
    
    welcome_msg = messages.get('welcome', '🎵 Welcome to FlutterSwarm!')
    print(welcome_msg.replace('FlutterSwarm!', 'FlutterSwarm Music App Creation'))
    
    # Get console width from config
    console_width = config.get_cli_setting('console_width') or 60
    print("=" * console_width)
    
    # Create FlutterSwarm instance
    swarm = FlutterSwarm()
    
    # Get music app specific config
    streaming_quality = music_config.get('streaming_quality', ['FLAC', '320kbps MP3'])
    max_playlist_size = music_config.get('max_playlist_size', 1000)
    offline_storage = music_config.get('offline_storage_limit', '10GB')
    
    # Create a comprehensive music app project
    project_id = swarm.create_project(
        name="MusicStreamPro",
        description="A comprehensive music streaming application with playlists, offline downloads, social features, and advanced audio controls",
        requirements=[
            "Music streaming from online sources",
            "Local music library management", 
            "Playlist creation and management",
            "Offline music downloads and caching",
            "Audio controls with equalizer",
            "User authentication and profiles",
            "Social features - sharing and following",
            "Music discovery and recommendations",
            "Search functionality with filters",
            "Background playback support",
            "Lyrics display integration",
            "Podcast support",
            "Sleep timer and alarm integration",
            "Cross-device synchronization",
            f"High-quality audio streaming ({', '.join(streaming_quality)})",
            "Dark/light theme with custom colors",
            "Accessibility features for visually impaired",
            "Gesture controls and voice commands",
            "Integration with external services (Spotify, Apple Music APIs)",
            "Push notifications for new releases and recommendations",
            f"Playlist size limit: {max_playlist_size} songs",
            f"Offline storage limit: {offline_storage}"
        ],
        features=[
            "music_streaming", "playlist_management", "offline_downloads", 
            "audio_controls", "user_authentication", "social_features",
            "music_discovery", "search", "background_playback", "lyrics",
            "podcasts", "sleep_timer", "sync", "high_quality_audio",
            "theming", "accessibility", "gesture_controls", "voice_commands",
            "external_apis", "push_notifications"
        ]
    )
    
    print(f"\n📋 Music app project created with ID: {project_id}")
    
    # Start the swarm system with QA monitoring
    print("\n🚀 Starting FlutterSwarm agent system with Quality Assurance...")
    
    # Create a task to run the swarm
    swarm_task = asyncio.create_task(swarm.start())
    
    # Give agents time to initialize
    await asyncio.sleep(5)
    
    # Start building the project with continuous QA monitoring
    print("\n🏗️  Starting music app build process with quality monitoring...")
    print("📱 Target platforms: Android, iOS, Web, Desktop")
    
    try:
        # Build the project with QA validation
        print("🔍 Quality Assurance Agent will monitor all outputs...")
        
        # Request QA validation throughout the build
        qa_agent = swarm.agents["quality_assurance"]
        
        # Start monitoring task
        monitoring_task = asyncio.create_task(
            monitor_build_quality(swarm, project_id, qa_agent)
        )
        
        # Build the project with extended timeout for complex music app
        result = await asyncio.wait_for(
            swarm.build_project(
                project_id, 
                platforms=["android", "ios", "web", "desktop"],
                ci_system="github_actions"
            ),
            timeout=900  # 15 minutes timeout for complex app
        )
        
        print("\n✅ Music app build completed!")
        await print_build_results_with_qa(result, qa_agent, project_id)
        
        # Cancel monitoring
        monitoring_task.cancel()
        
    except asyncio.TimeoutError:
        print("\n⏰ Build process timed out, but agents are still working...")
        print("🔍 Performing final quality assessment...")
        
        # Perform final QA validation
        await perform_final_qa_check(swarm, project_id)
        
    except Exception as e:
        print(f"\n❌ Error during build process: {e}")
        
        # Get QA assessment of the error
        await analyze_build_error(swarm, project_id, str(e))
    
    finally:
        print("\n🛑 Stopping FlutterSwarm...")
        await swarm.stop()

async def monitor_build_quality(swarm, project_id, qa_agent):
    """Continuously monitor build quality during development."""
    print("👁️  Starting continuous quality monitoring...")
    
    # Get monitoring interval from config
    config = get_config()
    monitoring_interval = config.get_interval_setting('qa_monitoring')
    
    while True:
        try:
            await asyncio.sleep(monitoring_interval)
            
            # Request QA validation
            qa_result = await qa_agent.execute_task(
                "validate_project", 
                {"project_id": project_id}
            )
            
            if qa_result.get("issues_found", 0) > 0:
                print(f"🔍 QA: Found {qa_result['issues_found']} issues, coordinating fixes...")
                
                # Coordinate fixes
                await qa_agent.execute_task(
                    "fix_issues",
                    {
                        "project_id": project_id,
                        "issues": qa_result.get("issues", [])
                    }
                )
            else:
                print("✅ QA: No issues detected, build quality looks good")
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"⚠️  QA monitoring error: {e}")
            await asyncio.sleep(monitoring_interval)

async def perform_final_qa_check(swarm, project_id):
    """Perform comprehensive final quality check."""
    print("\n🔍 Performing final quality assurance check...")
    
    qa_agent = swarm.agents["quality_assurance"]
    
    # Comprehensive validation
    final_qa = await qa_agent.execute_task(
        "validate_project",
        {"project_id": project_id}
    )
    
    print(f"\n📊 Final QA Report:")
    print(f"  • Total Issues Found: {final_qa.get('issues_found', 0)}")
    print(f"  • Critical Issues: {final_qa.get('critical_issues', 0)}")
    
    if final_qa.get("recommendations"):
        print(f"\n💡 QA Recommendations:")
        for rec in final_qa["recommendations"]:
            print(f"  • {rec}")

async def analyze_build_error(swarm, project_id, error_message):
    """Analyze build errors using QA agent."""
    print(f"\n🔍 QA analyzing build error: {error_message}")
    
    qa_agent = swarm.agents["quality_assurance"]
    
    error_analysis = await qa_agent.execute_task(
        "analyze_build_error",
        {
            "project_id": project_id,
            "error_message": error_message
        }
    )
    
    print(f"📋 Error Analysis: {error_analysis}")

async def print_build_results_with_qa(result, qa_agent, project_id):
    """Print build results with QA insights."""
    print("\n📋 Music App Build Summary:")
    print(f"  • Status: {result.get('status', 'Unknown')}")
    print(f"  • Files Created: {result.get('files_created', 0)}")
    print(f"  • Architecture Decisions: {result.get('architecture_decisions', 0)}")
    print(f"  • Security Findings: {len(result.get('security_findings', []))}")
    print(f"  • Documentation Files: {len(result.get('documentation', []))}")
    
    # Get QA metrics
    qa_metrics = await qa_agent.execute_task(
        "quality_metrics",
        {"project_id": project_id}
    )
    
    if qa_metrics:
        print(f"\n🎯 Quality Metrics:")
        print(f"  • Code Quality Score: {qa_metrics.get('quality_score', 'N/A')}")
        print(f"  • Issues Resolved: {qa_metrics.get('issues_resolved', 0)}")
        print(f"  • Test Coverage: {qa_metrics.get('test_coverage', 'N/A')}%")
    
    if result.get('test_results'):
        tests = result['test_results']
        print(f"  • Tests Passed: {tests.get('passed', 0)}")
        print(f"  • Tests Failed: {tests.get('failed', 0)}")
    
    if result.get('deployment_config'):
        print(f"  • CI/CD Configured: ✅")
        platforms = result['deployment_config'].get('platforms', [])
        print(f"  • Target Platforms: {', '.join(platforms)}")

def print_project_status(status):
    """Print formatted project status."""
    if 'error' in status:
        print(f"❌ Error getting project status: {status['error']}")
        return
    
    project = status.get('project', {})
    print(f"\n📋 Music App Project Status:")
    print(f"  • Project: {project.get('name', 'Unknown')}")
    print(f"  • Phase: {project.get('current_phase', 'Unknown')}")
    print(f"  • Progress: {project.get('progress', 0):.1%}")
    print(f"  • Files Created: {project.get('files_created', 0)}")
    
    agents = status.get('agents', {})
    if agents:
        print("\n🤖 Agent Status:")
        for agent_id, agent_info in agents.items():
            status_icon = "🟢" if agent_info.get('status') == 'idle' else "🔵" if agent_info.get('status') == 'working' else "🔴"
            task = agent_info.get('current_task', 'No active task')
            print(f"  • {agent_id}: {status_icon} {agent_info.get('status', 'unknown')} - {task}")

async def main():
    """Main function to run the music app creation."""
    print("🎵 Welcome to FlutterSwarm Music App Creator!")
    print("This will create a comprehensive music streaming application using AI agents with quality assurance.\n")
    
    try:
        await create_music_app()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Music app creation interrupted by user")
        
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Thanks for using FlutterSwarm!")
    print("🔗 Check the flutter_projects/ directory for your generated music app")
    print("🎵 Remember: All Flutter code was generated by AI agents - no manual edits!")

if __name__ == "__main__":
    asyncio.run(main())

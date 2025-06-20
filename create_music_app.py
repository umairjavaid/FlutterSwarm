#!/usr/bin/env python3
"""
Create a Music App using Swarm with Quality Assurance
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flutter_swarm import FlutterSwarm as Swarm
from config.config_manager import get_config

async def create_music_app():
    """Create a comprehensive music streaming application using Swarm."""
    print("🔍 DEBUG: Starting create_music_app function")
    
    # Get configuration
    print("🔍 DEBUG: Getting configuration...")
    config = get_config()
    app_config = config.get_application_config()
    music_config = app_config.get('examples', {}).get('music_app', {})
    messages = config.get_messages_config()
    
    print("🔍 DEBUG: Configuration loaded successfully")
    
    welcome_msg = messages.get('welcome', '🎵 Welcome to Swarm!')
    print(welcome_msg.replace('Swarm!', 'Swarm Music App Creation'))
    
    # Get console width from config
    console_width = config.get_cli_setting('console_width') or 60
    print("=" * console_width)
    
    print("🔍 DEBUG: Creating Swarm instance...")
    # Create Swarm instance
    swarm = Swarm()
    print("🔍 DEBUG: Swarm instance created")
    
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
    print("\n🚀 Starting Swarm agent system with Quality Assurance...")
    
    # Start building the project with continuous QA monitoring
    print("\n🏗️  Starting music app build process with quality monitoring...")
    print("📱 Target platforms: Android, iOS, Web, Desktop")
    
    try:
        # Build the project with QA validation
        print("🔍 Quality Assurance will monitor all outputs throughout the build...")
        
        # Build the project with extended timeout for complex music app
        result = await asyncio.wait_for(
            swarm.build_project(
                project_id=project_id,
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
                ],
                platforms=["android", "ios", "web", "desktop"],
                ci_system="github_actions"
            ),
            timeout=900  # 15 minutes timeout for complex app
        )
        
        print("\n✅ Music app build completed!")
        await print_build_results_with_qa(result)
        
    except asyncio.TimeoutError:
        print("\n⏰ Build process timed out, but workflow may still be running...")
        print("🔍 Build process exceeded 15 minute timeout for complex app")
        
    except Exception as e:
        print(f"\n❌ Error during build process: {e}")
        await analyze_build_error(swarm, project_id, str(e))
    
    finally:
        print("\n✅ Music app build process completed")
        print("📋 Check the flutter_projects directory for generated files")

async def analyze_build_error(swarm, project_id, error_message):
    """Analyze build errors (simplified for LangGraph implementation)."""
    print(f"\n🔍 Analyzing build error: {error_message}")
    print(f"� Error occurred in project: {project_id}")
    print(f"� Suggestion: Check the logs directory for detailed error information")

async def print_build_results_with_qa(result):
    """Print build results with QA insights."""
    print("\n📋 Music App Build Summary:")
    print(f"  • Status: {result.get('status', 'Unknown')}")
    print(f"  • Files Created: {result.get('files_created', 0)}")
    print(f"  • Architecture Decisions: {result.get('architecture_decisions', 0)}")
    print(f"  • Security Findings: {len(result.get('security_findings', []))}")
    print(f"  • Documentation Files: {len(result.get('documentation', []))}")
    
    # Print test results if available
    test_results = result.get('test_results', {})
    if test_results:
        print(f"\n🧪 Test Results:")
        print(f"  • Tests Passed: {test_results.get('passed', 0)}")
        print(f"  • Tests Failed: {test_results.get('failed', 0)}")
        if test_results.get('coverage'):
            print(f"  • Test Coverage: {test_results['coverage']:.1%}")
    
    # Print performance metrics
    performance = result.get('performance_metrics', {})
    if performance:
        print(f"\n⚡ Performance:")
        print(f"  • Optimizations Applied: ✅")
    
    # Print quality assessment if available
    quality = result.get('quality_assessment', {})
    if quality:
        print(f"\n🔍 Quality Assessment:")
        print(f"  • Overall Score: {quality.get('score', 'N/A')}")
        print(f"  • Issues Found: {len(quality.get('issues', []))}")
    
    print(f"\n🎵 Music app build complete!")
    
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
    print("🎵 Welcome to Swarm Music App Creator!")
    print("This will create a comprehensive music streaming application using AI agents with quality assurance.\n")
    
    print("🔍 DEBUG: Starting main function...")
    
    try:
        print("🔍 DEBUG: About to call create_music_app()...")
        await create_music_app()
        print("🔍 DEBUG: create_music_app() completed successfully")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Music app creation interrupted by user")
        
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Thanks for using Swarm!")
    print("🔗 Check the flutter_projects/ directory for your generated music app")
    print("🎵 Remember: All code was generated by AI agents - no manual edits!")

if __name__ == "__main__":
    asyncio.run(main())

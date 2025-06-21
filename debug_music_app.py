#!/usr/bin/env python3
"""
Debug script to show LLM conversations and file creation in real-time.
This script demonstrates the fixed FlutterSwarm system with full visibility.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flutter_swarm import FlutterSwarm
from utils.llm_logger import llm_logger
from utils.file_monitor import file_monitor


async def main():
    """Run a test music app creation with full visibility."""
    
    print("🎵 FlutterSwarm Debug Test - Music App Creation")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now()}")
    print()
    
    # Initialize the swarm
    print("🤖 Initializing FlutterSwarm...")
    swarm = FlutterSwarm()
    
    # Create the music app
    project_name = "debug_music_app"
    description = "A simple music streaming app with playlists"
    requirements = [
        "Music streaming from online sources",
        "Local music library management", 
        "Playlist creation and management",
        "Search functionality with filters"
    ]
    features = [
        "music_streaming",
        "playlist_management", 
        "search_functionality"
    ]
    
    print(f"🎵 Creating project: {project_name}")
    print(f"📝 Description: {description}")
    print(f"📋 Requirements: {', '.join(requirements)}")
    print(f"🚀 Features: {', '.join(features)}")
    print()
    
    try:
        # Create the project 
        project = swarm.create_project(
            name=project_name,
            description=description,
            requirements=requirements,
            features=features
        )
        
        print(f"✅ Project created: {project}")
        print()
        
        # Build the project
        print("🏗️ Building project with agents...")
        result = await swarm.build_project(
            project_id=project,
            name=project_name,
            description=description,
            requirements=requirements,
            features=features,
            platforms=["android", "ios", "web"]
        )
        
        print(f"✅ Build completed: {result}")
        print()
        
        # Show file creation summary
        print("📁 File Creation Monitor Summary:")
        file_monitor.print_summary()
        
        # Show LLM session summary
        print("🧠 LLM Session Summary:")
        print("-" * 40)
        summary = llm_logger.get_session_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        print()
        
        # List created files in directory (backup check)
        print("� Files in project directory:")
        print("-" * 40)
        project_path = f"flutter_projects/{project_name}"
        if os.path.exists(project_path):
            file_count = 0
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith(('.dart', '.yaml', '.json')):
                        rel_path = os.path.relpath(os.path.join(root, file), project_path)
                        size = os.path.getsize(os.path.join(root, file))
                        print(f"  📄 {rel_path} ({size} bytes)")
                        file_count += 1
            
            if file_count == 0:
                print("  ❌ No Flutter files found in project directory")
        else:
            print(f"  ❌ Project directory not found: {project_path}")
        print()
        
        # Export detailed LLM logs
        log_file = llm_logger.export_interactions_to_json()
        print(f"📊 Detailed LLM logs exported to: {log_file}")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🏁 Debug test completed!")
    print(f"🕐 Finished at: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())

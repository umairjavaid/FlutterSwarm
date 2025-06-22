#!/usr/bin/env python3
"""
Run the create_music_app function with a 5-minute timeout to prevent infinite loops.
"""
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_music_app import create_music_app

async def main():
    try:
        # 5 minutes timeout (300 seconds)
        await asyncio.wait_for(create_music_app(), timeout=300)
        print("✅ Music app creation completed within time limit.")
    except asyncio.TimeoutError:
        print("⏰ Timeout: Music app creation did not finish within 5 minutes. Possible infinite loop prevented.")
    except Exception as e:
        print(f"❌ Error during music app creation: {e}")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3

import sys
import os
import json
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing Enhanced LLM Response Parser")
print("=" * 40)

# Test basic JSON parsing
test_json = """
{
    "files": [
        {
            "path": "lib/main.dart",
            "content": "import 'package:flutter/material.dart';",
            "description": "Main app"
        }
    ]
}
"""

print("1. Testing basic JSON parsing...")
try:
    data = json.loads(test_json)
    print(f"✅ Basic JSON parsing works: {len(data.get('files', []))} files")
except Exception as e:
    print(f"❌ Basic JSON parsing failed: {e}")
    sys.exit(1)

# Test parser import
print("\n2. Testing parser import...")
try:
    from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser
    print("✅ Parser import successful")
except Exception as e:
    print(f"❌ Parser import failed: {e}")
    sys.exit(1)

# Test parser creation
print("\n3. Testing parser creation...")
try:
    # Create a simple logger
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    
    parser = EnhancedLLMResponseParser(logger)
    print("✅ Parser creation successful")
except Exception as e:
    print(f"❌ Parser creation failed: {e}")
    sys.exit(1)

# Test JSON strategy directly
print("\n4. Testing JSON parsing strategy...")
try:
    parsed_files, error = parser._parse_json_strategy(test_json.strip())
    if parsed_files:
        print(f"✅ JSON strategy works: {len(parsed_files)} files parsed")
        print(f"   First file: {parsed_files[0]['path']}")
    else:
        print(f"❌ JSON strategy failed: {error}")
except Exception as e:
    print(f"❌ JSON strategy error: {e}")

# Test full parser
print("\n5. Testing full parser...")
try:
    parsed_files, error = parser.parse_llm_response(test_json.strip(), {"test": True})
    if parsed_files:
        print(f"✅ Full parser works: {len(parsed_files)} files parsed")
        print(f"   First file: {parsed_files[0]['path']}")
    else:
        print(f"❌ Full parser failed: {error}")
except Exception as e:
    print(f"❌ Full parser error: {e}")

print("\n" + "=" * 40)
print("Debug test completed")

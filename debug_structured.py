#!/usr/bin/env python3

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser

# Create logger
logger = logging.getLogger("debug")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

parser = EnhancedLLMResponseParser(logger)

# Test structured text format
structured_response = '''
File: lib/constants/app_constants.dart
class AppConstants {
  static const String appName = 'My Flutter App';
  static const String version = '1.0.0';
}

File: lib/utils/helpers.dart
class Helpers {
  static String formatDate(DateTime date) {
    return date.toString();
  }
}
'''

print("Testing structured text parsing...")
print("Original response:")
print(repr(structured_response))
print("\n" + "="*50 + "\n")

# Test the strategy directly
parsed_files, error = parser._parse_structured_text_strategy(structured_response)

print(f"Parsed files: {len(parsed_files)}")
print(f"Error: {error}")

for i, file_info in enumerate(parsed_files):
    print(f"\nFile {i+1}:")
    print(f"  Path: {file_info['path']}")
    print(f"  Content (first 100 chars): {file_info['content'][:100]}...")

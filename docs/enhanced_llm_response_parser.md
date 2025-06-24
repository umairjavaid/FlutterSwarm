# Enhanced LLM Response Parser

The Enhanced LLM Response Parser provides robust parsing of LLM responses with multiple fallback strategies and better error handling. This replaces the previous ad-hoc JSON parsing logic throughout the codebase.

## Features

- **Multiple Parsing Strategies**: JSON extraction, code block parsing, structured text patterns, and LLM reformat fallback
- **Robust Error Handling**: Graceful degradation through multiple strategies
- **Consistent Interface**: Standardized parsing across all agents
- **Detailed Logging**: Comprehensive logging for debugging and monitoring
- **Retry Logic**: Automatic reformatting when initial parsing fails

## Usage

### Basic Usage in Agents

```python
from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser

class YourAgent(BaseAgent):
    async def parse_llm_response(self, llm_response: str):
        parser = EnhancedLLMResponseParser(self.logger)
        
        parsed_files, error = parser.parse_llm_response(llm_response, {
            "project_id": "your_project_id",
            "agent": self
        })
        
        if parsed_files:
            self.logger.info(f"✅ Successfully parsed {len(parsed_files)} files")
            return parsed_files
        else:
            self.logger.error(f"❌ Parsing failed: {error}")
            return []
```

### Using Convenience Functions

```python
from utils.enhancedLLMResponseParser import parse_llm_response_for_agent

class YourAgent(BaseAgent):
    async def process_llm_response(self, llm_response: str):
        # Easy one-liner parsing
        parsed_files, error = parse_llm_response_for_agent(self, llm_response, {
            "project_id": "your_project_id"
        })
        
        if not parsed_files:
            self.logger.error(f"Failed to parse response: {error}")
            return []
        
        return parsed_files
```

### Complete File Creation Example

```python
from utils.enhancedLLMResponseParser import parse_llm_response_for_agent

class ImplementationAgent(BaseAgent):
    async def create_files_from_llm(self, llm_response: str, project_id: str):
        # Parse the response
        parsed_files, error = parse_llm_response_for_agent(self, llm_response, {
            "project_id": project_id
        })
        
        if not parsed_files:
            # Try LLM reformatting
            reformat_prompt = f"""
Your previous response was not in the correct format. Please reformat it as valid JSON.

Previous response: {llm_response[:500]}...

Return ONLY valid JSON:
{{
    "files": [
        {{
            "path": "lib/path/file.dart",
            "content": "complete file content",
            "description": "file description"
        }}
    ]
}}
"""
            reformatted = await self.think(reformat_prompt)
            parsed_files, error = parse_llm_response_for_agent(self, reformatted, {
                "project_id": project_id
            })
        
        # Create the files
        created_files = []
        project_state = shared_state.get_project_state(project_id)
        project_path = project_state.project_path if project_state else f"flutter_projects/project_{project_id[:8]}"
        
        for file_info in parsed_files:
            file_path = file_info["path"]
            file_content = file_info["content"]
            
            success = await self._create_actual_file(project_path, file_path, file_content, project_id)
            if success:
                created_files.append(file_path)
        
        return created_files
```

## Parsing Strategies

### 1. JSON Strategy
Extracts clean JSON from LLM responses, handling:
- JSON code blocks (`json`)
- Generic code blocks
- Raw JSON objects
- Malformed JSON with common prefixes

### 2. Code Blocks Strategy
Parses code blocks with file paths:
- `dart:lib/path/file.dart` format
- `// lib/path/file.dart` comments
- `File: lib/path/file.dart` headers
- `**lib/path/file.dart**` markdown

### 3. Structured Text Strategy
Handles structured text patterns:
- Section-based file definitions
- Path/content pairs
- Various delimiters

### 4. LLM Reformat Strategy
Asks the LLM to reformat its response when other strategies fail.

## Expected Input Formats

### JSON Format (Preferred)
```json
{
    "files": [
        {
            "path": "lib/features/auth/auth_service.dart",
            "content": "import 'package:flutter/material.dart';\n\nclass AuthService {\n  // Implementation\n}",
            "description": "Authentication service implementation"
        }
    ]
}
```

### Code Block Format
```
```dart:lib/main.dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}
```

### Structured Text Format
```
File: lib/main.dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

File: lib/models/user.dart
class User {
  final String id;
  final String name;
  
  User({required this.id, required this.name});
}
```

## Migration Guide

### From Old JSON Parsing

**Before:**
```python
async def _extract_json_from_response(self, response: str) -> dict:
    import json
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Complex fallback logic...
```

**After:**
```python
from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser

async def parse_response(self, response: str) -> List[Dict[str, Any]]:
    parser = EnhancedLLMResponseParser(self.logger)
    parsed_files, error = parser.parse_llm_response(response, {"agent": self})
    return parsed_files if parsed_files else []
```

### Integration Checklist

- [ ] Import `EnhancedLLMResponseParser`
- [ ] Replace manual JSON parsing with parser
- [ ] Update error handling to use parser results
- [ ] Add context information for better parsing
- [ ] Test with existing LLM responses
- [ ] Remove old parsing methods

## Best Practices

1. **Always provide context** when calling the parser
2. **Use the convenience functions** for simple cases
3. **Handle both success and failure cases** explicitly
4. **Log parsing results** for debugging
5. **Consider LLM reformatting** for critical operations
6. **Validate file contents** before creation
7. **Register created files** in shared state

## Troubleshooting

### Common Issues

1. **Empty parsed_files**: Check if LLM response format matches expected patterns
2. **Parsing errors**: Enable debug logging to see which strategies are failing
3. **File creation failures**: Verify project paths and permissions
4. **Missing context**: Ensure agent and project_id are provided in context

### Debug Logging

Enable detailed logging to troubleshoot parsing issues:

```python
parser = EnhancedLLMResponseParser(self.logger)
# The parser will log which strategy succeeded/failed
parsed_files, error = parser.parse_llm_response(response, context)
```

### Error Recovery

The parser includes automatic error recovery:
1. If JSON parsing fails, try code block extraction
2. If code blocks fail, try structured text patterns
3. If all fail, the calling code can ask LLM to reformat
4. Graceful degradation ensures no crashes

## Performance Considerations

- **Caching**: Parser instances can be reused for performance
- **Large responses**: Parser handles large responses efficiently
- **Multiple files**: Batch file creation for better performance
- **Memory usage**: Parser processes responses in chunks when possible
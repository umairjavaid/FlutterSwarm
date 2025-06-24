import re
import json
from typing import List, Dict, Any, Tuple
import logging

class EnhancedLLMResponseParser:
    """Enhanced parser for LLM responses with robust error handling and multiple parsing strategies."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def parse_llm_response(self, response: str, context: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
        """
        Parse LLM response with multiple strategies and error recovery.
        
        Returns:
            Tuple of (parsed_files, error_message)
        """
        if not response or not response.strip():
            return [], "Empty response from LLM"
        
        # Strategy 1: Try to extract and parse clean JSON
        files, error = self._parse_json_strategy(response)
        if files:
            self.logger.info(f"✅ Successfully parsed {len(files)} files using JSON strategy")
            return files, ""
        
        # Strategy 2: Try to extract code blocks with file paths
        files, error = self._parse_code_blocks_strategy(response)
        if files:
            self.logger.info(f"✅ Successfully parsed {len(files)} files using code blocks strategy")
            return files, ""
        
        # Strategy 3: Try to extract files from structured text patterns
        files, error = self._parse_structured_text_strategy(response)
        if files:
            self.logger.info(f"✅ Successfully parsed {len(files)} files using structured text strategy")
            return files, ""
        
        # Strategy 4: Use LLM to reformat the response
        files, error = self._llm_reformat_strategy(response, context)
        if files:
            self.logger.info(f"✅ Successfully parsed {len(files)} files using LLM reformat strategy")
            return files, ""
        
        return [], f"Failed to parse response after all strategies. Last error: {error}"
    
    def _parse_json_strategy(self, response: str) -> Tuple[List[Dict[str, Any]], str]:
        """Strategy 1: Extract and parse JSON from response."""
        try:
            # First try to parse the response directly as JSON
            try:
                data = json.loads(response.strip())
                if isinstance(data, dict) and "files" in data:
                    return self._validate_files_structure(data["files"]), ""
            except json.JSONDecodeError:
                pass
            
            # Clean the response
            cleaned = self._clean_response_for_json(response)
            
            # Try to find JSON blocks
            json_patterns = [
                r'```json\s*(.*?)\s*```',  # JSON in code blocks
                r'```\s*(.*?)\s*```',       # Generic code blocks
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, cleaned, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        # Extract just the JSON part if there's extra text
                        json_str = self._extract_json_from_text(match if isinstance(match, str) else match[0])
                        data = json.loads(json_str)
                        
                        if isinstance(data, dict) and "files" in data:
                            return self._validate_files_structure(data["files"]), ""
                    except json.JSONDecodeError:
                        continue
            
            # Try to extract JSON object from anywhere in the response
            json_str = self._extract_json_from_text(cleaned)
            if json_str:
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict) and "files" in data:
                        return self._validate_files_structure(data["files"]), ""
                except json.JSONDecodeError:
                    pass
            
            return [], "No valid JSON found in response"
            
        except Exception as e:
            return [], f"JSON parsing error: {str(e)}"
    
    def _parse_code_blocks_strategy(self, response: str) -> Tuple[List[Dict[str, Any]], str]:
        """Strategy 2: Extract code blocks with file paths."""
        try:
            files = []
            
            # Patterns for code blocks with file paths
            patterns = [
                # Pattern: ```dart:lib/path/file.dart\ncode\n```
                r'```(?:dart|yaml|json):?\s*([^\n]+)\n(.*?)```',
                # Pattern: // lib/path/file.dart\ncode
                r'//\s*(lib/[^\n]+\.(?:dart|yaml|json))\s*\n((?:.*\n)*?)(?=//\s*lib/|$)',
                # Pattern: File: lib/path/file.dart\ncode
                r'File:\s*([^\n]+\.(?:dart|yaml|json))\s*\n((?:.*\n)*?)(?=File:|$)',
                # Pattern: **lib/path/file.dart**\ncode
                r'\*\*([^\n]+\.(?:dart|yaml|json))\*\*\s*\n((?:.*\n)*?)(?=\*\*|$)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
                for filepath, content in matches:
                    filepath = filepath.strip()
                    content = content.strip()
                    
                    if filepath and content:
                        files.append({
                            "path": filepath,
                            "content": content,
                            "description": f"File extracted from code block"
                        })
            
            return files, "" if files else "No code blocks with file paths found"
            
        except Exception as e:
            return [], f"Code block parsing error: {str(e)}"
    
    def _parse_structured_text_strategy(self, response: str) -> Tuple[List[Dict[str, Any]], str]:
        """Strategy 3: Parse structured text patterns."""
        try:
            files = []
            
            # Look for file patterns in the response
            # Pattern: "File: path/to/file.ext" followed by content
            file_pattern = r'File:\s*([^\n]+\.(?:dart|yaml|json))\s*\n((?:(?!File:).*\n?)*)'
            matches = re.findall(file_pattern, response, re.MULTILINE | re.IGNORECASE)
            
            for filepath, content in matches:
                filepath = filepath.strip()
                content = content.strip()
                
                if filepath and content:
                    files.append({
                        "path": filepath,
                        "content": content,
                        "description": "File extracted from structured text"
                    })
            
            # If no files found with the above pattern, try alternative patterns
            if not files:
                # Alternative patterns for different formats
                alternative_patterns = [
                    r'(?:Path|//)\s*:\s*([^\n]+\.(?:dart|yaml|json))\s*\n((?:(?!(?:Path|//):).*\n?)*)',
                    r'---\s*([^\n]+\.(?:dart|yaml|json))\s*\n((?:(?!---).*\n?)*)'
                ]
                
                for pattern in alternative_patterns:
                    matches = re.findall(pattern, response, re.MULTILINE | re.IGNORECASE)
                    for filepath, content in matches:
                        filepath = filepath.strip()
                        content = content.strip()
                        
                        if filepath and content:
                            files.append({
                                "path": filepath,
                                "content": content,
                                "description": "File extracted from structured text"
                            })
            
            return files, "" if files else "No structured file patterns found"
            
        except Exception as e:
            return [], f"Structured text parsing error: {str(e)}"
    
    def _llm_reformat_strategy(self, response: str, context: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
        """Strategy 4: Ask LLM to reformat the response (requires think method)."""
        # This would need to be implemented by the caller since it requires LLM access
        # For now, return empty to indicate this strategy wasn't used
        return [], "LLM reformat strategy not implemented in parser"
    
    def _clean_response_for_json(self, response: str) -> str:
        """Clean LLM response to extract JSON."""
        # Remove common LLM prefixes/suffixes
        cleaners = [
            (r'^.*?(?=\{)', ''),  # Remove everything before first {
            (r'\}[^}]*$', '}'),   # Remove everything after last }
            (r'Here\'s the JSON.*?(?=\{)', ''),
            (r'```json\s*', ''),
            (r'\s*```', ''),
            (r'^\s*Sure.*?(?=\{)', ''),
            (r'^\s*I\'ll.*?(?=\{)', ''),
        ]
        
        cleaned = response
        for pattern, replacement in cleaners:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON object from text by matching braces."""
        # Find the first { and last } to extract JSON
        brace_count = 0
        start_idx = None
        end_idx = None
        
        for i, char in enumerate(text):
            if char == '{':
                if start_idx is None:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx is not None:
                    end_idx = i + 1
                    break
        
        if start_idx is not None and end_idx is not None:
            return text[start_idx:end_idx]
        
        return text
    
    def _validate_files_structure(self, files: List[Any]) -> List[Dict[str, Any]]:
        """Validate and normalize files structure."""
        validated = []
        
        if not isinstance(files, list):
            return []
        
        for file_info in files:
            if isinstance(file_info, dict):
                path = file_info.get("path", "")
                content = file_info.get("content", "")
                
                if path and content:
                    validated.append({
                        "path": path.strip(),
                        "content": content,
                        "description": file_info.get("description", "Generated file")
                    })
        
        return validated


# Enhanced parsing method for Implementation Agent
async def enhanced_parse_and_create_files(self, project_id: str, llm_response: str, retry_count: int = 0) -> List[str]:
    """
    Enhanced parsing method with better error handling and retry logic.
    
    This method replaces _parse_and_create_files in implementation_agent.py
    """
    parser = EnhancedLLMResponseParser(self.logger)
    
    # Parse the LLM response
    parsed_files, error = parser.parse_llm_response(llm_response, {
        "project_id": project_id,
        "agent": self
    })
    
    # If parsing failed and this is the first attempt, try asking LLM to reformat
    if not parsed_files and retry_count == 0:
        self.logger.warning(f"⚠️ Initial parsing failed: {error}")
        
        # Ask LLM to reformat the response
        reformat_prompt = f"""
Your previous response was not in the correct format. Please reformat it as valid JSON.

Previous response (first 500 chars):
{llm_response[:500]}...

CRITICAL: Return ONLY a valid JSON object with this exact structure (no other text):
{{
    "files": [
        {{
            "path": "lib/path/to/file.dart",
            "content": "complete file content here",
            "description": "what this file does"
        }}
    ]
}}

Ensure:
- The response starts with {{ and ends with }}
- No text before or after the JSON
- Valid JSON syntax
- Complete file contents
"""
        
        try:
            reformatted = await self.think(reformat_prompt, {
                "original_response": llm_response,
                "parse_error": error
            })
            
            # Try parsing the reformatted response
            parsed_files, error = parser.parse_llm_response(reformatted, {
                "project_id": project_id,
                "agent": self
            })
            
            if parsed_files:
                self.logger.info("✅ Successfully parsed reformatted response")
            else:
                self.logger.error(f"❌ Reformatting failed: {error}")
        except Exception as e:
            self.logger.error(f"❌ Error during reformatting: {e}")
    
    # Create the actual files
    created_files = []
    if parsed_files:
        project_state = shared_state.get_project_state(project_id)
        project_path = project_state.project_path if project_state else f"flutter_projects/project_{project_id[:8]}"
        
        for file_info in parsed_files:
            try:
                file_path = file_info["path"]
                file_content = file_info["content"]
                
                # Create the file
                success = await self._create_actual_file(project_path, file_path, file_content, project_id)
                if success:
                    created_files.append(file_path)
                    self.logger.info(f"✅ Created file: {file_path}")
            except Exception as e:
                self.logger.error(f"❌ Error creating file {file_info.get('path', 'unknown')}: {e}")
    
    return created_files

# Utility functions for easy integration in agents
def parse_llm_response_for_agent(agent, llm_response: str, context: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], str]:
    """
    Convenience function for agents to parse LLM responses.
    
    Args:
        agent: The agent instance (should have a logger)
        llm_response: The LLM response to parse
        context: Additional context for parsing
    
    Returns:
        Tuple of (parsed_files, error_message)
    """
    if not hasattr(agent, 'logger'):
        raise ValueError("Agent must have a logger attribute")
    
    parser = EnhancedLLMResponseParser(agent.logger)
    
    if context is None:
        context = {"agent": agent}
    else:
        context["agent"] = agent
    
    return parser.parse_llm_response(llm_response, context)


def create_files_from_parsed_response(agent, parsed_files: List[Dict[str, Any]], 
                                    project_path: str, project_id: str = None) -> List[str]:
    """
    Convenience function to create files from parsed LLM response.
    
    Args:
        agent: The agent instance
        parsed_files: List of file dictionaries from parse_llm_response
        project_path: Base path for the project
        project_id: Optional project ID for state tracking
    
    Returns:
        List of created file paths
    """
    import asyncio
    import os
    
    async def _create_files():
        created_files = []
        
        for file_info in parsed_files:
            try:
                file_path = file_info.get("path", "")
                file_content = file_info.get("content", "")
                
                if not file_path or not file_content:
                    continue
                
                full_path = os.path.join(project_path, file_path)
                
                # Create directory if it doesn't exist
                dir_path = os.path.dirname(full_path)
                os.makedirs(dir_path, exist_ok=True)
                
                # Write the file
                if hasattr(agent, 'execute_tool'):
                    # Use agent's tool system if available
                    file_result = await agent.execute_tool(
                        "file",
                        operation="write",
                        file_path=full_path,
                        content=file_content
                    )
                    if file_result.status.value == "success":
                        created_files.append(file_path)
                        if hasattr(agent, 'logger'):
                            agent.logger.info(f"✅ Created file: {file_path}")
                else:
                    # Fallback to direct file writing
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    created_files.append(file_path)
                    if hasattr(agent, 'logger'):
                        agent.logger.info(f"✅ Created file: {file_path}")
                
                # Register in shared state if available
                if project_id and hasattr(agent, 'shared_state'):
                    try:
                        agent.shared_state.add_file_to_project(project_id, file_path, file_content)
                    except Exception as e:
                        if hasattr(agent, 'logger'):
                            agent.logger.warning(f"Could not register file in shared state: {e}")
                            
            except Exception as e:
                if hasattr(agent, 'logger'):
                    agent.logger.error(f"❌ Error creating file {file_info.get('path', 'unknown')}: {e}")
        
        return created_files
    
    # Run the async function
    if asyncio.iscoroutinefunction(create_files_from_parsed_response):
        return asyncio.run(_create_files())
    else:
        return asyncio.run(_create_files())
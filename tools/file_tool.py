"""
File operations tool for reading, writing, and managing files.
"""

import os
import shutil
import time
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from .base_tool import BaseTool, ToolResult, ToolStatus
from utils.function_logger import track_function

class FileTool(BaseTool):
    """
    Tool for file operations like reading, writing, copying, etc.
    """
    
    def __init__(self, base_directory: Optional[str] = None):
        super().__init__(
            name="file",
            description="Perform file operations (read, write, copy, move, etc.)",
            timeout=30
        )
        self.base_directory = base_directory or os.getcwd()
    
    @track_function(log_args=True, log_return=True)
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute file operation.
        
        Args:
            operation: Type of operation (read, write, copy, move, delete, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        start_time = time.time()
        
        try:
            if operation == "read":
                return await self._read_file(**kwargs)
            elif operation == "write":
                return await self._write_file(**kwargs)
            elif operation == "copy":
                return await self._copy_file(**kwargs)
            elif operation == "move":
                return await self._move_file(**kwargs)
            elif operation == "delete":
                return await self._delete_file(**kwargs)
            elif operation == "list":
                return await self._list_directory(**kwargs)
            elif operation == "create_directory":
                return await self._create_directory(**kwargs)
            elif operation == "exists":
                return await self._check_exists(**kwargs)
            elif operation == "search":
                return await self._search_files(**kwargs)
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Unknown operation: {operation}",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"File operation '{operation}' failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _read_file(self, file_path: str, encoding: str = "utf-8", **kwargs) -> ToolResult:
        """Read file content."""
        full_path = self._get_full_path(file_path)
        
        if not os.path.exists(full_path):
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"File not found: {file_path}"
            )
        
        try:
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            file_info = os.stat(full_path)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=content,
                data={
                    "file_path": file_path,
                    "size": file_info.st_size,
                    "modified": file_info.st_mtime,
                    "encoding": encoding
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to read file: {str(e)}"
            )
    
    async def _write_file(self, file_path: str, content: str, 
                         encoding: str = "utf-8", create_dirs: bool = True, **kwargs) -> ToolResult:
        """Write content to file."""
        full_path = self._get_full_path(file_path)
        
        try:
            # Create directories if needed
            if create_dirs:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            file_info = os.stat(full_path)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Successfully wrote {len(content)} characters to {file_path}",
                data={
                    "file_path": file_path,
                    "size": file_info.st_size,
                    "content_length": len(content),
                    "encoding": encoding
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to write file: {str(e)}"
            )
    
    async def _copy_file(self, source: str, destination: str, **kwargs) -> ToolResult:
        """Copy file from source to destination."""
        source_path = self._get_full_path(source)
        dest_path = self._get_full_path(destination)
        
        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Successfully copied {source} to {destination}",
                data={
                    "source": source,
                    "destination": destination
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to copy file: {str(e)}"
            )
    
    async def _move_file(self, source: str, destination: str, **kwargs) -> ToolResult:
        """Move file from source to destination."""
        source_path = self._get_full_path(source)
        dest_path = self._get_full_path(destination)
        
        try:
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.move(source_path, dest_path)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Successfully moved {source} to {destination}",
                data={
                    "source": source,
                    "destination": destination
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to move file: {str(e)}"
            )
    
    async def _delete_file(self, file_path: str, **kwargs) -> ToolResult:
        """Delete file or directory."""
        full_path = self._get_full_path(file_path)
        
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output=f"Successfully deleted file: {file_path}"
                )
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output=f"Successfully deleted directory: {file_path}"
                )
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Path not found: {file_path}"
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to delete: {str(e)}"
            )
    
    async def _list_directory(self, directory: str = ".", recursive: bool = False, **kwargs) -> ToolResult:
        """List directory contents."""
        full_path = self._get_full_path(directory)
        
        try:
            files = []
            
            if recursive:
                for root, dirs, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, full_path)
                        file_info = os.stat(file_path)
                        files.append({
                            "path": rel_path,
                            "size": file_info.st_size,
                            "modified": file_info.st_mtime,
                            "is_directory": False
                        })
                    for dirname in dirs:
                        dir_path = os.path.join(root, dirname)
                        rel_path = os.path.relpath(dir_path, full_path)
                        files.append({
                            "path": rel_path,
                            "size": 0,
                            "modified": os.stat(dir_path).st_mtime,
                            "is_directory": True
                        })
            else:
                for item in os.listdir(full_path):
                    item_path = os.path.join(full_path, item)
                    file_info = os.stat(item_path)
                    files.append({
                        "path": item,
                        "size": file_info.st_size,
                        "modified": file_info.st_mtime,
                        "is_directory": os.path.isdir(item_path)
                    })
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Found {len(files)} items in {directory}",
                data={
                    "directory": directory,
                    "files": files,
                    "count": len(files)
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to list directory: {str(e)}"
            )
    
    async def _create_directory(self, directory: str, **kwargs) -> ToolResult:
        """Create directory."""
        full_path = self._get_full_path(directory)
        
        try:
            os.makedirs(full_path, exist_ok=True)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Successfully created directory: {directory}",
                data={"directory": directory}
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to create directory: {str(e)}"
            )
    
    async def _check_exists(self, path: str, **kwargs) -> ToolResult:
        """Check if file or directory exists."""
        full_path = self._get_full_path(path)
        
        exists = os.path.exists(full_path)
        is_file = os.path.isfile(full_path) if exists else False
        is_dir = os.path.isdir(full_path) if exists else False
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Path {'exists' if exists else 'does not exist'}: {path}",
            data={
                "path": path,
                "exists": exists,
                "is_file": is_file,
                "is_directory": is_dir
            }
        )
    
    async def _search_files(self, pattern: str, directory: str = ".", **kwargs) -> ToolResult:
        """Search for files matching pattern."""
        import fnmatch
        
        full_path = self._get_full_path(directory)
        matches = []
        
        try:
            for root, dirs, files in os.walk(full_path):
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, full_path)
                        matches.append(rel_path)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Found {len(matches)} files matching '{pattern}'",
                data={
                    "pattern": pattern,
                    "directory": directory,
                    "matches": matches,
                    "count": len(matches)
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to search files: {str(e)}"
            )
    
    def _get_full_path(self, path: str) -> str:
        """Get full path relative to base directory."""
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_directory, path)
    
    async def read_json(self, file_path: str) -> ToolResult:
        """Read and parse JSON file."""
        result = await self._read_file(file_path)
        
        if result.status != ToolStatus.SUCCESS:
            return result
        
        try:
            data = json.loads(result.output)
            result.data = {"json_data": data}
            result.output = f"Successfully parsed JSON file with {len(data) if isinstance(data, (dict, list)) else 1} items"
            return result
            
        except json.JSONDecodeError as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Invalid JSON format: {str(e)}"
            )
    
    async def write_json(self, file_path: str, data: Any, indent: int = 2) -> ToolResult:
        """Write data as JSON file."""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return await self._write_file(file_path, content)
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to serialize JSON: {str(e)}"
            )
    
    async def read_yaml(self, file_path: str) -> ToolResult:
        """Read and parse YAML file."""
        result = await self._read_file(file_path)
        
        if result.status != ToolStatus.SUCCESS:
            return result
        
        try:
            data = yaml.safe_load(result.output)
            result.data = {"yaml_data": data}
            result.output = f"Successfully parsed YAML file"
            return result
            
        except yaml.YAMLError as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Invalid YAML format: {str(e)}"
            )
    
    async def write_yaml(self, file_path: str, data: Any) -> ToolResult:
        """Write data as YAML file."""
        try:
            content = yaml.dump(data, default_flow_style=False, sort_keys=False)
            return await self._write_file(file_path, content)
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to serialize YAML: {str(e)}"
            )

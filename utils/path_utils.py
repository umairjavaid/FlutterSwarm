"""
Path utilities for FlutterSwarm - ensures cross-platform compatibility.
"""

import os
from pathlib import Path
from typing import Union


def get_absolute_project_path(project_name: str) -> str:
    """
    Get absolute path for a Flutter project.
    
    Args:
        project_name: Name of the Flutter project
        
    Returns:
        Absolute path to the project directory
    """
    if not project_name:
        raise ValueError("Project name cannot be empty")
    
    # Get the base directory (FlutterSwarm root)
    base_dir = Path(__file__).parent.parent.absolute()
    flutter_projects_dir = base_dir / "flutter_projects"
    project_path = flutter_projects_dir / project_name
    
    return str(project_path.absolute())


def safe_join(*paths: Union[str, Path]) -> str:
    """
    Safely join paths using os.path.join for cross-platform compatibility.
    
    Args:
        *paths: Path components to join
        
    Returns:
        Joined path as string
    """
    if not paths:
        raise ValueError("At least one path component required")
    
    # Convert all to strings and filter out empty ones
    clean_paths = [str(p) for p in paths if p]
    
    if not clean_paths:
        raise ValueError("No valid path components provided")
    
    return os.path.join(*clean_paths)


def ensure_absolute_path(path: Union[str, Path]) -> str:
    """
    Ensure a path is absolute.
    
    Args:
        path: Path to make absolute
        
    Returns:
        Absolute path as string
    """
    path_obj = Path(path)
    return str(path_obj.absolute())


def normalize_path_separators(path: str) -> str:
    """
    Normalize path separators for the current OS.
    
    Args:
        path: Path with potentially mixed separators
        
    Returns:
        Path with normalized separators
    """
    return os.path.normpath(path)


def create_directory_safely(directory_path: Union[str, Path]) -> bool:
    """
    Create directory and all parent directories safely.
    
    Args:
        directory_path: Path to directory to create
        
    Returns:
        True if directory was created or already exists, False on error
    """
    try:
        path_obj = Path(directory_path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False


def get_flutter_projects_dir() -> str:
    """
    Get the Flutter projects directory path.
    
    Returns:
        Absolute path to flutter_projects directory
    """
    base_dir = Path(__file__).parent.parent.absolute()
    flutter_projects_dir = base_dir / "flutter_projects"
    
    # Ensure the directory exists
    create_directory_safely(flutter_projects_dir)
    
    return str(flutter_projects_dir.absolute())


def get_project_relative_path(project_name: str, *sub_paths: str) -> str:
    """
    Get a path relative to a specific project.
    
    Args:
        project_name: Name of the Flutter project
        *sub_paths: Additional path components within the project
        
    Returns:
        Absolute path within the project
    """
    project_path = get_absolute_project_path(project_name)
    if sub_paths:
        return safe_join(project_path, *sub_paths)
    return project_path


def validate_project_name(project_name: str) -> bool:
    """
    Validate a Flutter project name.
    
    Args:
        project_name: Project name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not project_name or not isinstance(project_name, str):
        return False
    
    # Check for invalid characters
    invalid_chars = '<>:"|?*\\'
    if any(char in project_name for char in invalid_chars):
        return False
    
    # Check for reserved names
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                     'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                     'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
    if project_name.upper() in reserved_names:
        return False
    
    # Check length
    if len(project_name) > 255:
        return False
    
    return True

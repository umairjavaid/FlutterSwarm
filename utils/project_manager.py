"""
Project Manager utility for handling project file operations.
"""

import os
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from config.config_manager import get_config

load_dotenv()

class ProjectManager:
    """
    Handles creation and management of projects on disk.
    """
    
    def __init__(self):
        self.config = get_config()
        project_config = self.config.get_section('project') if hasattr(self.config, 'get_section') else {}
        
        # Get settings from config with fallbacks
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'flutter_projects')
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory set to: {self.output_dir}")
    
    def get_project_path(self, project_name: str) -> str:
        """Get the full path for a project directory."""
        return os.path.join(self.output_dir, project_name)
    
    def project_exists(self, project_name: str) -> bool:
        """Check if a project directory already exists."""
        project_path = self.get_project_path(project_name)
        return os.path.exists(project_path) and os.path.isdir(project_path)
    
    def create_project_directory(self, project_name: str) -> str:
        """
        Create a basic project directory.
        Returns the project path.
        """ 
        project_path = self.get_project_path(project_name)
        
        if self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' already exists at {project_path}")
        
        os.makedirs(project_path)
        print(f"✅ Project directory created at: {project_path}")
        return project_path

    def _create_basic_structure(self, project_name: str) -> str:
        """
        Creates a basic directory structure for a project.
        This can be used as a fallback.
        """
        project_path = self.get_project_path(project_name)
        
        # Basic structure
        directories = [
            'src',
            'tests',
            'docs',
            'config'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
            
        # Create a placeholder README
        self.write_file(project_name, 'README.md', f'# {project_name}\n')
        
        print(f"✅ Basic project structure created at: {project_path}")
        return project_path

    def write_file(self, project_name: str, file_path: str, content: str) -> bool:
        """
        Write content to a file inside a project directory.
        The file_path is relative to the project root.
        """
        project_path = self.get_project_path(project_name)
        full_path = os.path.join(project_path, file_path)
        
        try:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            return True
        except IOError as e:
            print(f"Error writing file {full_path}: {e}")
            return False

    def write_project_files(self, project_name: str, files: Dict[str, str]) -> List[str]:
        """
        Write multiple files to a project.
        
        Args:
            project_name: Name of the project
            files: Dictionary mapping file paths to content
            
        Returns:
            List of successfully written file paths
        """
        if not self.project_exists(project_name):
            self.create_project_directory(project_name)
        
        written_files = []
        for file_path, content in files.items():
            if self.write_file(project_name, file_path, content):
                written_files.append(file_path)
        return written_files

    def list_projects(self) -> List[str]:
        """List all projects in the output directory."""
        if not os.path.exists(self.output_dir):
            return []
        return [d for d in os.listdir(self.output_dir) if os.path.isdir(os.path.join(self.output_dir, d))]

    def get_project_info(self, project_name: str) -> Optional[Dict]:
        """Get information about a project."""
        project_path = self.get_project_path(project_name)
        if not self.project_exists(project_name):
            return None
        
        return {
            "name": project_name,
            "path": project_path,
            "files": [os.path.join(dp, f) for dp, dn, fn in os.walk(project_path) for f in fn]
        }
    
    def create_flutter_project_structure(self, project_name: str) -> str:
        pass
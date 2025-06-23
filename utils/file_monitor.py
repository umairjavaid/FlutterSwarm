"""
File Creation Monitor - Tracks all file operations during FlutterSwarm execution.
Simple version without external dependencies.
"""

import os
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

# Use comprehensive logging system with function tracking
from utils.function_logger import track_function
from monitoring.agent_logger import agent_logger
from utils.comprehensive_logging import get_logger


class FileCreationMonitor:
    """Monitor and track file creation during FlutterSwarm execution."""
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def __init__(self, watch_directory: str = "flutter_projects"):
        self.watch_directory = watch_directory
        self.created_files: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        self.lock = threading.Lock()
        self.monitoring = False
        
        # Setup logging
        self.logger = get_logger('FlutterSwarm.FileMonitor')
        
        # Ensure watch directory exists
        os.makedirs(watch_directory, exist_ok=True)
        
        self.logger.info(f"📂 File monitor initialized for: {watch_directory}")
        agent_logger.log_project_event("system", "file_monitor_init", 
                                     f"File monitor initialized for: {watch_directory}")
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def record_file_creation(self, file_path: str, content_length: int = 0):
        """Manually record a file creation."""
        if os.path.exists(file_path):
            with self.lock:
                file_info = {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'extension': os.path.splitext(file_path)[1],
                    'size': os.path.getsize(file_path) if os.path.exists(file_path) else content_length,
                    'created_at': datetime.now().isoformat(),
                    'relative_path': os.path.relpath(file_path, self.watch_directory) if file_path.startswith(self.watch_directory) else file_path
                }
                self.created_files.append(file_info)
            
            self.logger.info(f"📄 File recorded: {file_info['relative_path']} ({file_info['size']} bytes)")
    
    def scan_directory(self):
        """Scan the watch directory for all existing files."""
        if not os.path.exists(self.watch_directory):
            return
        
        self.logger.info(f"🔍 Scanning directory: {self.watch_directory}")
        
        for root, dirs, files in os.walk(self.watch_directory):
            for file in files:
                if file.endswith(('.dart', '.yaml', '.json', '.md')):
                    full_path = os.path.join(root, file)
                    self.record_file_creation(full_path)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of monitored file operations."""
        with self.lock:
            total_files = len(self.created_files)
            total_size = sum(f['size'] for f in self.created_files)
            
            # Group by extension
            by_extension = {}
            for file_info in self.created_files:
                ext = file_info['extension']
                if ext not in by_extension:
                    by_extension[ext] = {'count': 0, 'size': 0}
                by_extension[ext]['count'] += 1
                by_extension[ext]['size'] += file_info['size']
            
            return {
                'monitoring_duration': str(datetime.now() - self.start_time),
                'total_files_created': total_files,
                'total_size_bytes': total_size,
                'files_by_extension': by_extension,
                'recent_files': self.created_files[-10:] if self.created_files else [],
                'all_files': self.created_files
            }
    
    def print_summary(self):
        """Print a formatted summary of file operations."""
        summary = self.get_summary()
        
        print("\n📊 File Creation Summary")
        print("=" * 50)
        print(f"⏱️ Monitoring Duration: {summary['monitoring_duration']}")
        print(f"📄 Total Files Created: {summary['total_files_created']}")
        print(f"💾 Total Size: {summary['total_size_bytes']:,} bytes")
        print()
        
        if summary['files_by_extension']:
            print("📂 Files by Type:")
            for ext, stats in summary['files_by_extension'].items():
                ext_name = ext if ext else 'no extension'
                print(f"  {ext_name}: {stats['count']} files ({stats['size']:,} bytes)")
            print()
        
        if summary['all_files']:
            print("📋 All Files Created:")
            for file_info in summary['all_files']:
                print(f"  📄 {file_info['relative_path']} ({file_info['size']} bytes) - {file_info['created_at']}")
        print()


# Global file monitor instance
file_monitor = FileCreationMonitor()

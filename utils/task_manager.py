"""
Async task management utilities for proper cleanup and shutdown.
"""

import asyncio
import weakref
import time
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class TaskInfo:
    task: asyncio.Task
    name: str
    created_at: float
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[Exception] = None

class TaskManager:
    """
    Manages async tasks with proper cleanup and shutdown capabilities.
    Prevents resource leaks and ensures clean shutdown.
    """
    
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._task_groups: Dict[str, Set[str]] = {}
        self._shutdown_event = asyncio.Event()
        self._cleanup_interval = 30.0  # Cleanup every 30 seconds
        self._max_task_age = 3600.0    # Remove completed tasks after 1 hour
        
        # Start cleanup task
        self._cleanup_task = None
        
    async def create_task(self, coro, name: str = None, group: str = None) -> asyncio.Task:
        """Create and register a new task."""
        if name is None:
            name = f"task_{len(self._tasks)}"
            
        task = asyncio.create_task(coro, name=name)
        task_info = TaskInfo(
            task=task,
            name=name,
            created_at=time.time(),
            status=TaskStatus.PENDING
        )
        
        self._tasks[name] = task_info
        
        # Add to group if specified
        if group:
            if group not in self._task_groups:
                self._task_groups[group] = set()
            self._task_groups[group].add(name)
        
        # Add callback to update status
        task.add_done_callback(lambda t: self._on_task_done(name, t))
        
        print(f"✅ Created task '{name}' in group '{group or 'default'}'")
        return task
    
    def _on_task_done(self, task_name: str, task: asyncio.Task):
        """Callback when task completes."""
        if task_name in self._tasks:
            task_info = self._tasks[task_name]
            
            if task.cancelled():
                task_info.status = TaskStatus.CANCELLED
            elif task.exception():
                task_info.status = TaskStatus.FAILED
                task_info.error = task.exception()
                print(f"❌ Task '{task_name}' failed: {task_info.error}")
            else:
                task_info.status = TaskStatus.COMPLETED
                print(f"✅ Task '{task_name}' completed")
    
    async def cancel_task(self, name: str, timeout: float = 5.0) -> bool:
        """Cancel a specific task with timeout."""
        if name not in self._tasks:
            return False
            
        task_info = self._tasks[name]
        task = task_info.task
        
        if task.done():
            return True
            
        print(f"🛑 Cancelling task '{name}'...")
        task.cancel()
        
        try:
            await asyncio.wait_for(task, timeout=timeout)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        
        return task.cancelled() or task.done()
    
    async def cancel_group(self, group: str, timeout: float = 10.0) -> Dict[str, bool]:
        """Cancel all tasks in a group."""
        if group not in self._task_groups:
            return {}
        
        print(f"🛑 Cancelling task group '{group}'...")
        results = {}
        
        # Cancel all tasks in parallel
        cancel_tasks = []
        for task_name in self._task_groups[group].copy():
            cancel_tasks.append(self.cancel_task(task_name, timeout))
        
        if cancel_tasks:
            cancel_results = await asyncio.gather(*cancel_tasks, return_exceptions=True)
            for task_name, result in zip(self._task_groups[group], cancel_results):
                results[task_name] = result if isinstance(result, bool) else False
        
        return results
    
    async def cancel_all_tasks(self, timeout: float = 15.0) -> Dict[str, bool]:
        """Cancel all managed tasks."""
        print("🛑 Cancelling all managed tasks...")
        results = {}
        
        # Get all active tasks
        active_tasks = [
            (name, info) for name, info in self._tasks.items() 
            if not info.task.done()
        ]
        
        if not active_tasks:
            print("✅ No active tasks to cancel")
            return {}
        
        print(f"🛑 Cancelling {len(active_tasks)} active tasks...")
        
        # Cancel all tasks
        cancel_tasks = []
        for name, info in active_tasks:
            cancel_tasks.append(self.cancel_task(name, timeout / len(active_tasks)))
        
        cancel_results = await asyncio.gather(*cancel_tasks, return_exceptions=True)
        
        for (name, _), result in zip(active_tasks, cancel_results):
            results[name] = result if isinstance(result, bool) else False
        
        return results
    
    async def wait_for_completion(self, names: List[str] = None, timeout: float = None) -> Dict[str, bool]:
        """Wait for specific tasks or all tasks to complete."""
        if names is None:
            # Wait for all tasks
            tasks_to_wait = [info.task for info in self._tasks.values() if not info.task.done()]
            names = [name for name, info in self._tasks.items() if not info.task.done()]
        else:
            tasks_to_wait = [self._tasks[name].task for name in names if name in self._tasks]
        
        if not tasks_to_wait:
            return {name: True for name in names}
        
        print(f"⏳ Waiting for {len(tasks_to_wait)} tasks to complete...")
        
        try:
            if timeout:
                await asyncio.wait_for(
                    asyncio.gather(*tasks_to_wait, return_exceptions=True),
                    timeout=timeout
                )
            else:
                await asyncio.gather(*tasks_to_wait, return_exceptions=True)
            
            return {name: True for name in names}
            
        except asyncio.TimeoutError:
            print(f"⚠️ Timeout waiting for tasks")
            return {name: self._tasks[name].task.done() for name in names if name in self._tasks}
    
    def get_task_status(self, name: str = None) -> Dict[str, Any]:
        """Get status of specific task or all tasks."""
        if name:
            if name not in self._tasks:
                return {}
            
            info = self._tasks[name]
            return {
                "name": info.name,
                "status": info.status.value,
                "created_at": info.created_at,
                "age": time.time() - info.created_at,
                "done": info.task.done(),
                "cancelled": info.task.cancelled(),
                "error": str(info.error) if info.error else None
            }
        else:
            # Return summary of all tasks
            stats = {
                "total": len(self._tasks),
                "pending": 0,
                "running": 0,
                "completed": 0,
                "cancelled": 0,
                "failed": 0,
                "groups": len(self._task_groups)
            }
            
            for info in self._tasks.values():
                stats[info.status.value] += 1
            
            return stats
    
    async def cleanup_completed_tasks(self):
        """Remove old completed tasks to prevent memory leaks."""
        current_time = time.time()
        to_remove = []
        
        for name, info in self._tasks.items():
            if info.task.done() and (current_time - info.created_at) > self._max_task_age:
                to_remove.append(name)
        
        for name in to_remove:
            self._remove_task(name)
            
        if to_remove:
            print(f"🧹 Cleaned up {len(to_remove)} old tasks")
    
    def _remove_task(self, name: str):
        """Remove a task from tracking."""
        if name in self._tasks:
            del self._tasks[name]
            
        # Remove from groups
        for group_tasks in self._task_groups.values():
            group_tasks.discard(name)
    
    async def start_cleanup_loop(self):
        """Start background cleanup task."""
        if self._cleanup_task is not None:
            return
            
        async def cleanup_loop():
            while not self._shutdown_event.is_set():
                try:
                    await asyncio.sleep(self._cleanup_interval)
                    await self.cleanup_completed_tasks()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"❌ Error in cleanup loop: {e}")
        
        self._cleanup_task = await self.create_task(cleanup_loop(), name="task_manager_cleanup")
    
    async def shutdown(self, timeout: float = 30.0):
        """Shutdown task manager and cleanup all tasks."""
        print("🔄 Shutting down TaskManager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel cleanup task first
        if self._cleanup_task:
            await self.cancel_task("task_manager_cleanup", timeout=5.0)
        
        # Cancel all other tasks
        results = await self.cancel_all_tasks(timeout)
        
        failed_cancellations = [name for name, success in results.items() if not success]
        if failed_cancellations:
            print(f"⚠️ Failed to cancel {len(failed_cancellations)} tasks: {failed_cancellations}")
        
        # Final cleanup
        await self.cleanup_completed_tasks()
        
        print(f"✅ TaskManager shutdown complete. Final stats: {self.get_task_status()}")

# Global task manager instance
task_manager = TaskManager()

# Convenience functions
async def create_managed_task(coro, name: str = None, group: str = None) -> asyncio.Task:
    """Create a managed task."""
    return await task_manager.create_task(coro, name, group)

async def shutdown_all_tasks(timeout: float = 30.0):
    """Shutdown all managed tasks."""
    await task_manager.shutdown(timeout)

def get_task_stats() -> Dict[str, Any]:
    """Get task statistics."""
    return task_manager.get_task_status()

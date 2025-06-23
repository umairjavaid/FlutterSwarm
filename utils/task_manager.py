"""
Task Manager utility for handling agent tasks with timeouts and cancellation.
Prevents infinite loops and long-running operations from blocking the system.
"""

import asyncio
import time
from typing import Dict, Any, Callable, Awaitable, Optional
from datetime import datetime, timedelta

# Use comprehensive logging system with function tracking
from utils.function_logger import track_function
from monitoring.agent_logger import agent_logger
from utils.comprehensive_logging import get_logger

class TaskManager:
    """
    Manages agent tasks with proper timeout handling and cancellation.
    Prevents infinite loops and long-running operations from blocking the system.
    """
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_history: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger("FlutterSwarm.TaskManager")
        
        # Task timeouts by type (in seconds)
        self.task_timeouts = {
            'implement_feature': 600,      # 10 minutes for feature implementation
            'create_files': 300,           # 5 minutes for file creation
            'run_tests': 180,              # 3 minutes for test execution
            'architecture_design': 420,    # 7 minutes for architecture design
            'code_generation': 240,        # 4 minutes for code generation
            'validation': 120,             # 2 minutes for validation
            'file_operation': 60,          # 1 minute for file operations
            'llm_interaction': 180,        # 3 minutes for LLM calls
            'collaboration': 60,           # 1 minute for collaboration
            'monitoring': 30,              # 30 seconds for monitoring tasks
            'default': 300                 # 5 minutes default
        }
        
        # Circuit breaker settings
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # Log task manager initialization
        agent_logger.log_project_event("system", "task_manager_init", 
                                     "TaskManager initialized with timeout handling")
        
    @track_function(agent_id="system", log_args=True, log_return=True)
    async def run_task_with_timeout(self, task_name: str, coro: Awaitable, 
                                   timeout: Optional[int] = None,
                                   task_type: str = 'default') -> Any:
        """
        Run a coroutine with timeout and proper cancellation.
        
        Args:
            task_name: Unique identifier for the task
            coro: The coroutine to execute
            timeout: Custom timeout in seconds (overrides task_type timeout)
            task_type: Type of task for default timeout lookup
            
        Returns:
            Task result
            
        Raises:
            TimeoutError: If task exceeds timeout
            asyncio.CancelledError: If task was cancelled
        """
        # Determine timeout
        if timeout is None:
            timeout = self.task_timeouts.get(task_type, self.task_timeouts['default'])
        
        # Create unique task identifier
        task_id = f"{task_name}_{int(time.time())}"
        
        self.logger.info(f"🚀 Starting task '{task_name}' (timeout: {timeout}s)")
        
        # Create and register task
        task = asyncio.create_task(coro)
        self.running_tasks[task_id] = task
        
        # Record task start
        self.task_history[task_id] = {
            'name': task_name,
            'type': task_type,
            'start_time': datetime.now(),
            'timeout': timeout,
            'status': 'running'
        }
        
        try:
            # Wait for task with timeout
            result = await asyncio.wait_for(task, timeout=timeout)
            
            # Mark as completed
            self.task_history[task_id]['status'] = 'completed'
            self.task_history[task_id]['end_time'] = datetime.now()
            self.task_history[task_id]['duration'] = (
                self.task_history[task_id]['end_time'] - 
                self.task_history[task_id]['start_time']
            ).total_seconds()
            
            self.logger.info(f"✅ Task '{task_name}' completed successfully in {self.task_history[task_id]['duration']:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            # Cancel the task
            task.cancel()
            
            # Mark as timed out
            self.task_history[task_id]['status'] = 'timeout'
            self.task_history[task_id]['end_time'] = datetime.now()
            
            self.logger.error(f"⏰ Task '{task_name}' timed out after {timeout} seconds")
            raise TimeoutError(f"Task '{task_name}' timed out after {timeout} seconds")
            
        except asyncio.CancelledError:
            # Mark as cancelled
            self.task_history[task_id]['status'] = 'cancelled'
            self.task_history[task_id]['end_time'] = datetime.now()
            
            self.logger.warning(f"🚫 Task '{task_name}' was cancelled")
            raise
            
        except Exception as e:
            # Mark as failed
            self.task_history[task_id]['status'] = 'failed'
            self.task_history[task_id]['end_time'] = datetime.now()
            self.task_history[task_id]['error'] = str(e)
            
            self.logger.error(f"❌ Task '{task_name}' failed: {e}")
            raise
            
        finally:
            # Clean up
            self.running_tasks.pop(task_id, None)
    
    async def run_task_with_retry(self, task_name: str, coro_factory: Callable[[], Awaitable],
                                 max_retries: Optional[int] = None,
                                 retry_delay: Optional[float] = None,
                                 task_type: str = 'default') -> Any:
        """
        Run a task with retry logic and exponential backoff.
        
        Args:
            task_name: Name of the task
            coro_factory: Function that returns a new coroutine for each attempt
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries
            task_type: Type of task for timeout lookup
            
        Returns:
            Task result
        """
        if max_retries is None:
            max_retries = self.max_retries
        if retry_delay is None:
            retry_delay = self.retry_delay
            
        last_exception = None
        
        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                coro = coro_factory()
                result = await self.run_task_with_timeout(
                    f"{task_name}_attempt_{attempt + 1}",
                    coro,
                    task_type=task_type
                )
                
                if attempt > 0:
                    self.logger.info(f"✅ Task '{task_name}' succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"⚠️ Task '{task_name}' attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"❌ Task '{task_name}' failed after {max_retries + 1} attempts")
        
        # If we get here, all attempts failed
        raise last_exception
    
    async def execute_operation_with_retry(self, operation_name: str, operation_func: Callable[[], Awaitable],
                                          max_retries: Optional[int] = None,
                                          retry_delay: Optional[float] = None,
                                          task_type: str = 'default',
                                          timeout: Optional[int] = None) -> Any:
        """
        Execute an operation with both retry logic and timeout handling.
        Combines the functionality of run_task_with_retry and run_task_with_timeout.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Function that returns a coroutine for each attempt
            max_retries: Maximum number of retry attempts (defaults to class setting)
            retry_delay: Base delay between retries (defaults to class setting)
            task_type: Type of task for timeout lookup
            timeout: Custom timeout in seconds
            
        Returns:
            Operation result
            
        Raises:
            Exception: The last exception if all retries fail
        """
        if max_retries is None:
            max_retries = self.max_retries
        if retry_delay is None:
            retry_delay = self.retry_delay
            
        last_exception = None
        
        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                # Create coroutine for this attempt
                coro = operation_func()
                
                # Run with timeout
                result = await self.run_task_with_timeout(
                    f"{operation_name}_attempt_{attempt + 1}",
                    coro,
                    timeout=timeout,
                    task_type=task_type
                )
                
                if attempt > 0:
                    self.logger.info(f"✅ Operation '{operation_name}' succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"⚠️ Operation '{operation_name}' attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"❌ Operation '{operation_name}' failed after {max_retries + 1} attempts")
        
        # If we get here, all attempts failed
        raise last_exception

    def add_circuit_breaker(self, operation_name: str, failure_threshold: int = 5, 
                           recovery_timeout: int = 60) -> None:
        """
        Add circuit breaker configuration for an operation.
        
        Args:
            operation_name: Name of the operation to protect
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before trying to close circuit
        """
        if not hasattr(self, 'circuit_breakers'):
            self.circuit_breakers = {}
            
        self.circuit_breakers[operation_name] = {
            'failure_threshold': failure_threshold,
            'recovery_timeout': recovery_timeout,
            'failure_count': 0,
            'last_failure_time': None,
            'state': 'closed'  # closed, open, half-open
        }
        
        self.logger.info(f"🔒 Circuit breaker added for '{operation_name}' (threshold: {failure_threshold}, timeout: {recovery_timeout}s)")

    async def execute_with_circuit_breaker(self, operation_name: str, operation_func: Callable[[], Awaitable]) -> Any:
        """
        Execute an operation with circuit breaker protection.
        
        Args:
            operation_name: Name of the operation
            operation_func: Function that returns a coroutine
            
        Returns:
            Operation result
            
        Raises:
            Exception: Circuit breaker is open or operation failed
        """
        if not hasattr(self, 'circuit_breakers'):
            self.circuit_breakers = {}
            
        # Initialize circuit breaker if not exists
        if operation_name not in self.circuit_breakers:
            self.add_circuit_breaker(operation_name)
            
        breaker = self.circuit_breakers[operation_name]
        current_time = time.time()
        
        # Check circuit breaker state
        if breaker['state'] == 'open':
            # Check if recovery timeout has passed
            if (breaker['last_failure_time'] and 
                current_time - breaker['last_failure_time'] > breaker['recovery_timeout']):
                breaker['state'] = 'half-open'
                self.logger.info(f"🔓 Circuit breaker for '{operation_name}' moved to half-open state")
            else:
                raise Exception(f"Circuit breaker for '{operation_name}' is open. Operation blocked.")
        
        try:
            # Execute the operation
            result = await operation_func()
            
            # Success - reset failure count and close circuit if half-open
            if breaker['state'] == 'half-open':
                breaker['state'] = 'closed'
                self.logger.info(f"✅ Circuit breaker for '{operation_name}' closed after successful recovery")
            
            breaker['failure_count'] = 0
            return result
            
        except Exception as e:
            # Failure - increment count and potentially open circuit
            breaker['failure_count'] += 1
            breaker['last_failure_time'] = current_time
            
            if breaker['failure_count'] >= breaker['failure_threshold']:
                breaker['state'] = 'open'
                self.logger.error(f"🚨 Circuit breaker for '{operation_name}' opened after {breaker['failure_count']} failures")
            
            raise

    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about task execution."""
        completed_tasks = [t for t in self.task_history.values() if t['status'] == 'completed']
        failed_tasks = [t for t in self.task_history.values() if t['status'] == 'failed']
        timeout_tasks = [t for t in self.task_history.values() if t['status'] == 'timeout']
        
        if completed_tasks:
            avg_duration = sum(t.get('duration', 0) for t in completed_tasks) / len(completed_tasks)
        else:
            avg_duration = 0
        
        return {
            'total_tasks': len(self.task_history),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(completed_tasks),
            'failed_tasks': len(failed_tasks),
            'timeout_tasks': len(timeout_tasks),
            'average_duration': avg_duration,
            'success_rate': len(completed_tasks) / len(self.task_history) if self.task_history else 0
        }


# Global task manager instance for use across the system
global_task_manager = TaskManager()

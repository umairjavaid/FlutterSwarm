"""
Global exception handling utilities for FlutterSwarm.
"""

import asyncio
import logging
import traceback
import sys
from typing import Optional, Callable, Any
from datetime import datetime


# Global logger for exception handling
exception_logger = logging.getLogger('FlutterSwarm.Exceptions')


def setup_global_exception_handler(logger: Optional[logging.Logger] = None) -> None:
    """
    Setup global exception handlers for both sync and async exceptions.
    
    Args:
        logger: Optional logger to use for exception logging
    """
    global exception_logger
    if logger:
        exception_logger = logger
    
    # Setup sync exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught synchronous exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow KeyboardInterrupt to work normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        exception_logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={
                'timestamp': datetime.now().isoformat(),
                'exception_type': exc_type.__name__,
                'exception_message': str(exc_value)
            }
        )
    
    # Set the sync exception handler
    sys.excepthook = handle_exception
    
    # Setup async exception handler
    def handle_async_exception(loop: asyncio.AbstractEventLoop, context: dict) -> None:
        """Handle uncaught asynchronous exceptions."""
        exception = context.get('exception')
        
        # Don't log cancelled task exceptions as errors
        if isinstance(exception, asyncio.CancelledError):
            exception_logger.debug(f"Task cancelled: {context.get('message', 'Unknown task')}")
            return
        
        # Log other exceptions
        if exception:
            exception_logger.error(
                f"Uncaught async exception: {context}",
                exc_info=exception,
                extra={
                    'timestamp': datetime.now().isoformat(),
                    'context': context,
                    'exception_type': type(exception).__name__ if exception else 'Unknown',
                    'exception_message': str(exception) if exception else context.get('message', 'Unknown error')
                }
            )
        else:
            exception_logger.error(
                f"Async error without exception: {context}",
                extra={
                    'timestamp': datetime.now().isoformat(),
                    'context': context
                }
            )
    
    # Set the async exception handler
    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(handle_async_exception)
    except RuntimeError:
        # No running loop, set up handler to be applied when loop starts
        def setup_handler_on_loop_start():
            try:
                loop = asyncio.get_running_loop()
                loop.set_exception_handler(handle_async_exception)
            except RuntimeError:
                pass
        
        # Store the handler to be applied later
        _pending_exception_handler = handle_async_exception


def safe_async_run(coro, timeout: Optional[float] = None) -> Any:
    """
    Safely run an async coroutine with exception handling.
    
    Args:
        coro: Coroutine to run
        timeout: Optional timeout in seconds
        
    Returns:
        Result of the coroutine or None if it failed
    """
    try:
        if timeout:
            return asyncio.wait_for(coro, timeout=timeout)
        else:
            return asyncio.run(coro)
    except asyncio.TimeoutError:
        exception_logger.warning(f"Async operation timed out after {timeout}s")
        return None
    except Exception as e:
        exception_logger.error(f"Async operation failed: {e}", exc_info=True)
        return None


def with_exception_handling(func: Callable) -> Callable:
    """
    Decorator to add exception handling to functions.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with exception handling
    """
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exception_logger.error(
                f"Exception in {func.__name__}: {e}",
                exc_info=True,
                extra={
                    'function_name': func.__name__,
                    'args': str(args)[:200],  # Limit arg string length
                    'kwargs': str(kwargs)[:200]
                }
            )
            return None
    
    async def async_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result
        except Exception as e:
            exception_logger.error(
                f"Exception in {func.__name__}: {e}",
                exc_info=True,
                extra={
                    'function_name': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
            )
            return None
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def log_and_suppress_exception(operation_name: str, exception: Exception) -> None:
    """
    Log an exception and suppress it (for non-critical operations).
    
    Args:
        operation_name: Name of the operation that failed
        exception: Exception that occurred
    """
    exception_logger.warning(
        f"Non-critical operation '{operation_name}' failed: {exception}",
        exc_info=True,
        extra={
            'operation_name': operation_name,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception)
        }
    )


def ensure_exception_handler_set() -> None:
    """
    Ensure that exception handlers are set for the current event loop.
    Call this when creating new event loops.
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.get_exception_handler() is None:
            def handle_async_exception(loop: asyncio.AbstractEventLoop, context: dict) -> None:
                exception = context.get('exception')
                
                if isinstance(exception, asyncio.CancelledError):
                    return
                
                if exception:
                    exception_logger.error(
                        f"Uncaught async exception: {context}",
                        exc_info=exception
                    )
                else:
                    exception_logger.error(f"Async error: {context}")
            
            loop.set_exception_handler(handle_async_exception)
    except RuntimeError:
        # No running loop
        pass


# Initialize exception handling when module is imported
setup_global_exception_handler()

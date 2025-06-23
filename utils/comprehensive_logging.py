"""
Comprehensive Logging Initialization
Sets up enhanced logging across the entire FlutterSwarm codebase.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_comprehensive_logging():
    """
    Initialize comprehensive logging for the entire FlutterSwarm system.
    This function should be called at startup to ensure all components
    are properly logged with complete input/output tracking.
    """
    
    # Import all loggers with error handling
    try:
        from utils.llm_logger import llm_logger
    except ImportError as e:
        print(f"Warning: Could not import LLM logger: {e}")
        llm_logger = None
    
    try:
        from utils.function_logger import function_logger
    except ImportError as e:
        print(f"Warning: Could not import function logger: {e}")
        function_logger = None
    
    try:
        from monitoring.agent_logger import agent_logger
    except ImportError as e:
        print(f"Warning: Could not import agent logger: {e}")
        agent_logger = None
    
    # Set up root logger for comprehensive output
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Session ID for this run
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Console handler with detailed formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Master log file with ALL details
    master_log_file = log_dir / f"comprehensive_log_{session_id}.log"
    file_handler = logging.FileHandler(master_log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    # Ultra-detailed formatter for file logging
    detailed_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(name)-30s | %(levelname)-8s | %(funcName)-20s:%(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Simpler formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(console_formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Initialize component loggers
    if llm_logger:
        llm_logger.logger.info("🤖 LLM Logger activated - tracking all AI interactions")
    if function_logger:
        function_logger.logger.info("📊 Function Logger activated - tracking all function calls")
    if agent_logger:
        agent_logger.logger.info("🐝 Agent Logger activated - tracking all agent activities")
    
    # Log system initialization
    root_logger.info("=" * 100)
    root_logger.info("🚀 FLUTTERSWARM COMPREHENSIVE LOGGING SYSTEM INITIALIZED")
    root_logger.info(f"📋 Session ID: {session_id}")
    root_logger.info(f"📄 Master log file: {master_log_file}")
    root_logger.info(f"🎯 Logging level: DEBUG (all details captured)")
    root_logger.info(f"💾 Individual component logs also available in logs/")
    root_logger.info("=" * 100)
    
    return {
        "session_id": session_id,
        "master_log_file": str(master_log_file),
        "llm_logger": llm_logger,
        "function_logger": function_logger,
        "agent_logger": agent_logger
    }

def log_system_info():
    """Log comprehensive system information for debugging."""
    import platform
    import os
    import sys
    
    logger = logging.getLogger("FlutterSwarm.SystemInfo")
    
    logger.info("📊 SYSTEM INFORMATION:")
    logger.info(f"   Platform: {platform.platform()}")
    logger.info(f"   Python: {sys.version}")
    logger.info(f"   Working Directory: {os.getcwd()}")
    logger.info(f"   Python Path: {sys.path}")
    
    # Log environment variables (sanitized)
    logger.info("🔐 ENVIRONMENT VARIABLES:")
    for key, value in os.environ.items():
        if any(sensitive in key.lower() for sensitive in ['key', 'token', 'secret', 'password']):
            logger.info(f"   {key}: [REDACTED]")
        else:
            logger.info(f"   {key}: {value}")

def enable_debug_mode():
    """Enable maximum debugging output."""
    # Set all FlutterSwarm loggers to DEBUG
    for name in ['FlutterSwarm', 'FlutterSwarm.LLM', 'FlutterSwarm.FunctionLogger', 'FlutterSwarm.Governance']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
    
    # Log debug mode activation
    logger = logging.getLogger("FlutterSwarm.Debug")
    logger.info("🔍 DEBUG MODE ACTIVATED - Maximum logging detail enabled")

def log_startup_banner():
    """Log a comprehensive startup banner."""
    logger = logging.getLogger("FlutterSwarm.Startup")
    
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════════╗
    ║                            🐝 FLUTTERSWARM SYSTEM                                ║
    ║                        Comprehensive Logging Active                             ║
    ╟──────────────────────────────────────────────────────────────────────────────────╢
    ║  📊 All function calls, inputs, and outputs are being tracked                   ║
    ║  🤖 Complete LLM request/response cycles are logged                             ║
    ║  🔧 All tool usage with detailed parameters is captured                         ║
    ║  🐝 Agent activities and collaborations are monitored                           ║
    ║  ❌ Errors with full stack traces are preserved                                 ║
    ║  📈 Performance metrics are continuously collected                              ║
    ╟──────────────────────────────────────────────────────────────────────────────────╢
    ║  🎯 Goal: Complete visibility into system execution for debugging              ║
    ║  📋 Check logs/ directory for detailed execution traces                        ║
    ╚══════════════════════════════════════════════════════════════════════════════════╝
    """
    
    for line in banner.split('\n'):
        if line.strip():
            logger.info(line)

def generate_final_report():
    """Generate a comprehensive final report of the execution."""
    try:
        from utils.llm_logger import llm_logger
    except ImportError:
        llm_logger = None
        
    try:
        from utils.function_logger import function_logger
    except ImportError:
        function_logger = None
        
    try:
        from monitoring.agent_logger import agent_logger
    except ImportError:
        agent_logger = None
    
    logger = logging.getLogger("FlutterSwarm.FinalReport")
    
    logger.info("📊 FINAL EXECUTION REPORT")
    logger.info("=" * 80)
    
    # LLM Statistics
    if llm_logger:
        try:
            llm_summary = llm_logger.get_session_summary()
            logger.info(f"🤖 LLM INTERACTIONS:")
            logger.info(f"   Total Requests: {llm_summary.get('total_requests', 0)}")
            logger.info(f"   Total Tokens: {llm_summary.get('total_tokens', 0):,}")
            logger.info(f"   Success Rate: {llm_summary.get('success_rate', 0):.1%}")
            logger.info(f"   Total Duration: {llm_summary.get('total_duration', 0):.2f}s")
            logger.info(f"   Average Duration: {llm_summary.get('average_duration', 0):.2f}s")
        except Exception as e:
            logger.error(f"   Failed to get LLM statistics: {e}")
    else:
        logger.info("🤖 LLM INTERACTIONS: Not available")
    
    # Function Call Statistics
    if function_logger:
        try:
            func_summary = function_logger.get_session_summary()
            logger.info(f"📊 FUNCTION CALLS:")
            logger.info(f"   Total Calls: {func_summary.get('total_function_calls', 0)}")
            logger.info(f"   Total Tool Usage: {func_summary.get('total_tool_usages', 0)}")
            logger.info(f"   Success Rate: {func_summary.get('success_rate', 0):.1%}")
            logger.info(f"   Total Duration: {func_summary.get('total_duration', 0):.2f}s")
        except Exception as e:
            logger.error(f"   Failed to get function statistics: {e}")
    else:
        logger.info("📊 FUNCTION CALLS: Not available")
    
    # Agent Activity Statistics
    if agent_logger:
        try:
            agent_summary = agent_logger.get_session_summary()
            logger.info(f"🐝 AGENT ACTIVITIES:")
            logger.info(f"   Total Log Entries: {agent_summary.get('total_entries', 0)}")
            logger.info(f"   Error Count: {agent_summary.get('error_count', 0)}")
            logger.info(f"   Session Duration: {agent_summary.get('session_duration', 'Unknown')}")
        except Exception as e:
            logger.error(f"   Failed to get agent statistics: {e}")
    else:
        logger.info("🐝 AGENT ACTIVITIES: Not available")
    
    # Export all logs
    logger.info("📄 EXPORTING DETAILED LOGS:")
    
    if llm_logger:
        try:
            llm_file = llm_logger.export_interactions_to_json()
            logger.info(f"   LLM Interactions: {llm_file}")
        except Exception as e:
            logger.error(f"   Failed to export LLM logs: {e}")
    
    if function_logger:
        try:
            func_file = function_logger.export_function_calls_to_json()
            logger.info(f"   Function Calls: {func_file}")
        except Exception as e:
            logger.error(f"   Failed to export function logs: {e}")
    
    if agent_logger:
        try:
            agent_file = agent_logger.export_logs_to_json()
            logger.info(f"   Agent Activities: {agent_file}")
        except Exception as e:
            logger.error(f"   Failed to export agent logs: {e}")
    
    logger.info("=" * 80)
    logger.info("✅ COMPREHENSIVE LOGGING COMPLETE - All execution details preserved")

def get_logger(name: str = "FlutterSwarm"):
    """
    Get a logger instance for the specified name.
    This function provides a centralized way to get loggers in the comprehensive logging system.
    
    Args:
        name: Logger name (defaults to "FlutterSwarm")
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

# Auto-initialization when module is imported
if __name__ != "__main__":
    try:
        # Don't auto-initialize to avoid circular imports
        # Call setup_comprehensive_logging() explicitly from main entry points
        pass
    except Exception as e:
        print(f"⚠️ Failed to initialize comprehensive logging: {e}")
        import traceback
        traceback.print_exc()

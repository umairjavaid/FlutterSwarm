"""
Live Terminal Display for FlutterSwarm
Shows real-time agent activities, progress, and status updates.
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import required modules for terminal display
import os
import sys

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Fallback color codes
    class Fore:
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'
        RESET_ALL = '\033[0m'

from shared.state import shared_state, AgentStatus, MessageType


@dataclass
class DisplayConfig:
    """Configuration for the live display."""
    refresh_rate: float = 0.5  # seconds
    show_agent_details: bool = True
    show_tool_usage: bool = True
    show_messages: bool = True
    compact_mode: bool = False
    max_message_history: int = 20
    terminal_width: int = 80


class LiveDisplay:
    """
    Real-time terminal display for FlutterSwarm activities.
    Shows agent status, progress, and activities in a live updating interface.
    """
    
    def __init__(self, config: Optional[DisplayConfig] = None):
        self.config = config or DisplayConfig()
        self.is_running = False
        self.display_thread = None
        self._lock = threading.Lock()
        self._terminal_lock = threading.Lock()  # Synchronize terminal access
        
        # Display state
        self.last_update = datetime.now()
        self.message_history: List[Dict[str, Any]] = []
        self.tool_usage_history: List[Dict[str, Any]] = []
        self.agent_activities: Dict[str, List[str]] = {}
        
        # Terminal setup
        self._setup_terminal()
        
    def _setup_terminal(self):
        """Setup terminal for live display."""
        with self._terminal_lock:
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Unix/Linux/macOS
                os.system('clear')
            
            # Hide cursor
            sys.stdout.write('\033[?25l')
            sys.stdout.flush()
    
    def start(self):
        """Start the live display."""
        if self.is_running:
            return
        
        self.is_running = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
        with self._terminal_lock:
            print(f"{Fore.GREEN}🚀 Live monitoring started{Style.RESET_ALL}")
    
    def stop(self):
        """Stop the live display."""
        self.is_running = False
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1.0)
        
        with self._terminal_lock:
            # Show cursor
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()
            
            print(f"\n{Fore.YELLOW}📊 Live monitoring stopped{Style.RESET_ALL}")
    
    def _display_loop(self):
        """Main display loop."""
        # Add circuit breaker to prevent infinite loops
        import time
        
        class SimpleCircuitBreaker:
            def __init__(self, max_iterations, max_time, name):
                self.max_iterations = max_iterations
                self.max_time = max_time
                self.name = name
                self.start_time = time.time()
                self.iterations = 0
                
            def check(self):
                self.iterations += 1
                elapsed = time.time() - self.start_time
                
                if self.iterations > self.max_iterations:
                    print(f"⚠️ Circuit breaker {self.name}: Maximum iterations exceeded")
                    return False
                if elapsed > self.max_time:
                    print(f"⚠️ Circuit breaker {self.name}: Maximum time exceeded")
                    return False
                return True
        
        circuit_breaker = SimpleCircuitBreaker(
            max_iterations=86400,  # 24 hours at 1 second intervals 
            max_time=86400.0,      # 24 hours max
            name="live_display"
        )
        
        iteration_count = 0
        while self.is_running and circuit_breaker.check():
            try:
                self._update_display()
                time.sleep(self.config.refresh_rate)
                
                iteration_count += 1
                # Log status every 3600 iterations (1 hour at 1s intervals)
                if iteration_count % 3600 == 0:
                    print(f"🔍 Live display: {iteration_count} iterations, elapsed: {iteration_count}s")
                    
            except Exception as e:
                print(f"Display error: {e}")
                break
                
        if not circuit_breaker.check():
            print("⚠️ Live display stopped by circuit breaker")
    
    def _update_display(self):
        """Update the terminal display."""
        with self._terminal_lock:  # Use terminal lock for thread-safe output
            # Clear screen and move cursor to top
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Unix/Linux/macOS
                sys.stdout.write('\033[2J\033[H')
            
            # Build display content
            with self._lock:  # Use regular lock for data access
                content = self._build_display_content()
            
            # Print content
            sys.stdout.write(content)
            sys.stdout.flush()
    
    def _build_display_content(self) -> str:
        """Build the complete display content."""
        lines = []
        
        # Header
        lines.extend(self._build_header())
        
        # Agent status section
        if self.config.show_agent_details:
            lines.extend(self._build_agent_status())
        
        # Tool usage section
        if self.config.show_tool_usage:
            lines.extend(self._build_tool_usage())
        
        # Recent messages section
        if self.config.show_messages:
            lines.extend(self._build_recent_messages())
        
        # Footer
        lines.extend(self._build_footer())
        
        return '\n'.join(lines)
    
    def _build_header(self) -> List[str]:
        """Build header section."""
        lines = []
        lines.append(f"{Style.BRIGHT}{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}")
        lines.append(f"{Style.BRIGHT}{Fore.CYAN}🐝 FlutterSwarm Live Monitor{Style.RESET_ALL}")
        lines.append(f"{Fore.WHITE}Last Update: {self.last_update.strftime('%H:%M:%S')}{Style.RESET_ALL}")
        lines.append(f"{Style.BRIGHT}{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}")
        
        return lines
    
    def _build_agent_status(self) -> List[str]:
        """Build agent status section."""
        lines = []
        lines.append(f"\n{Style.BRIGHT}{Fore.YELLOW}📡 Agent Status:{Style.RESET_ALL}")
        lines.append("-" * 60)
        
        agent_states = shared_state.get_agent_states()
        
        if not agent_states:
            lines.append(f"{Fore.YELLOW}No agents registered{Style.RESET_ALL}")
            return lines
        
        for agent_id, state in agent_states.items():
            status_color = self._get_status_color(state.status)
            progress_bar = self._create_progress_bar(state.progress)
            
            lines.append(
                f"{status_color}● {agent_id:<15} "
                f"{state.status.value:<10} "
                f"{progress_bar} "
                f"{state.current_task or 'Idle':<25}{Style.RESET_ALL}"
            )
            
            # Show recent activities for this agent
            if agent_id in self.agent_activities:
                recent_activities = self.agent_activities[agent_id][-2:]  # Last 2 activities
                for activity in recent_activities:
                    lines.append(f"  {Fore.WHITE}└─ {activity}{Style.RESET_ALL}")
        
        return lines
    
    def _build_tool_usage(self) -> List[str]:
        """Build tool usage section."""
        lines = []
        lines.append(f"\n{Style.BRIGHT}{Fore.GREEN}🔧 Recent Tool Usage:{Style.RESET_ALL}")
        lines.append("-" * 60)
        
        recent_tools = self.tool_usage_history[-5:]  # Last 5 tool usages
        
        if not recent_tools:
            lines.append(f"{Fore.YELLOW}No recent tool usage{Style.RESET_ALL}")
            return lines
        
        for tool_usage in recent_tools:
            agent = tool_usage.get('agent', 'unknown')
            tool_name = tool_usage.get('tool', 'unknown')
            operation = tool_usage.get('operation', 'unknown')
            status = tool_usage.get('status', 'unknown')
            timestamp = tool_usage.get('timestamp', datetime.now())
            
            status_color = Fore.GREEN if status == 'success' else Fore.RED
            time_str = timestamp.strftime('%H:%M:%S')
            
            lines.append(
                f"{Fore.CYAN}{time_str}{Style.RESET_ALL} "
                f"{Fore.MAGENTA}{agent:<12}{Style.RESET_ALL} "
                f"{Fore.WHITE}{tool_name:<15}{Style.RESET_ALL} "
                f"{status_color}{status:<8}{Style.RESET_ALL} "
                f"{Fore.WHITE}{operation}{Style.RESET_ALL}"
            )
        
        return lines
    
    def _build_recent_messages(self) -> List[str]:
        """Build recent messages section."""
        lines = []
        lines.append(f"\n{Style.BRIGHT}{Fore.BLUE}💬 Recent Messages:{Style.RESET_ALL}")
        lines.append("-" * 60)
        
        recent_messages = self.message_history[-self.config.max_message_history:]
        
        if not recent_messages:
            lines.append(f"{Fore.YELLOW}No recent messages{Style.RESET_ALL}")
            return lines
        
        for msg in recent_messages[-10:]:  # Show last 10 messages
            timestamp = msg.get('timestamp', datetime.now())
            from_agent = msg.get('from_agent', 'unknown')
            to_agent = msg.get('to_agent', 'broadcast')
            message_type = msg.get('message_type', 'unknown')
            content = str(msg.get('content', ''))[:50] + '...' if len(str(msg.get('content', ''))) > 50 else str(msg.get('content', ''))
            
            time_str = timestamp.strftime('%H:%M:%S')
            type_color = self._get_message_type_color(message_type)
            
            lines.append(
                f"{Fore.CYAN}{time_str}{Style.RESET_ALL} "
                f"{Fore.MAGENTA}{from_agent}{Style.RESET_ALL} → "
                f"{Fore.GREEN}{to_agent}{Style.RESET_ALL} "
                f"{type_color}[{message_type}]{Style.RESET_ALL} "
                f"{Fore.WHITE}{content}{Style.RESET_ALL}"
            )
        
        # Add LLM usage summary
        try:
            from utils.llm_logger import llm_logger
            llm_summary = llm_logger.get_session_summary()
            
            lines.append("")
            lines.append(f"{Style.BRIGHT}{Fore.MAGENTA}🤖 LLM Usage Summary:{Style.RESET_ALL}")
            lines.append(f"{Fore.CYAN}Total Requests: {llm_summary.get('total_requests', 0)}{Style.RESET_ALL}")
            lines.append(f"{Fore.CYAN}Total Tokens: {llm_summary.get('total_tokens', 0):,}{Style.RESET_ALL}")
            lines.append(f"{Fore.CYAN}Success Rate: {llm_summary.get('success_rate', 0):.1%}{Style.RESET_ALL}")
            lines.append(f"{Fore.CYAN}Avg Duration: {llm_summary.get('average_duration', 0):.2f}s{Style.RESET_ALL}")
        except ImportError:
            pass
        except Exception as e:
            lines.append(f"{Fore.RED}LLM metrics error: {e}{Style.RESET_ALL}")
        
        return lines
    
    def _build_footer(self) -> List[str]:
        """Build footer section."""
        lines = []
        lines.append(f"\n{Style.BRIGHT}{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}")
        lines.append(f"{Fore.WHITE}Press Ctrl+C to stop monitoring{Style.RESET_ALL}")
        
        return lines
    
    def _get_status_color(self, status: AgentStatus) -> str:
        """Get color for agent status."""
        color_map = {
            AgentStatus.IDLE: Fore.WHITE,
            AgentStatus.WORKING: Fore.GREEN,
            AgentStatus.WAITING: Fore.YELLOW,
            AgentStatus.COMPLETED: Fore.BLUE,
            AgentStatus.ERROR: Fore.RED
        }
        return color_map.get(status, Fore.WHITE)
    
    def _get_message_type_color(self, message_type: str) -> str:
        """Get color for message type."""
        color_map = {
            'STATUS_UPDATE': Fore.BLUE,
            'TASK_REQUEST': Fore.GREEN,
            'TASK_COMPLETED': Fore.CYAN,
            'COLLABORATION_REQUEST': Fore.MAGENTA,
            'ERROR_REPORT': Fore.RED
        }
        return color_map.get(message_type.upper(), Fore.WHITE)
    
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create a progress bar."""
        if progress is None:
            progress = 0.0
        
        filled = int(progress * width)
        bar = '█' * filled + '░' * (width - filled)
        percentage = f"{progress * 100:5.1f}%"
        
        return f"[{Fore.GREEN}{bar}{Style.RESET_ALL}] {percentage}"
    
    def log_agent_activity(self, agent_id: str, activity: str):
        """Log an agent activity."""
        with self._lock:
            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.agent_activities[agent_id].append(f"{timestamp} - {activity}")
            
            # Keep only recent activities
            if len(self.agent_activities[agent_id]) > 10:
                self.agent_activities[agent_id] = self.agent_activities[agent_id][-10:]
    
    def log_tool_usage(self, agent_id: str, tool_name: str, operation: str, status: str):
        """Log tool usage."""
        with self._lock:
            self.tool_usage_history.append({
                'agent': agent_id,
                'tool': tool_name,
                'operation': operation,
                'status': status,
                'timestamp': datetime.now()
            })
            
            # Keep only recent tool usage
            if len(self.tool_usage_history) > 50:
                self.tool_usage_history = self.tool_usage_history[-50:]
    
    def log_message(self, from_agent: str, to_agent: str, message_type: str, content: Any):
        """Log a message."""
        with self._lock:
            self.message_history.append({
                'from_agent': from_agent,
                'to_agent': to_agent,
                'message_type': message_type,
                'content': content,
                'timestamp': datetime.now()
            })
            
            # Keep only recent messages
            if len(self.message_history) > 100:
                self.message_history = self.message_history[-100:]
            
            self.last_update = datetime.now()


# Global live display instance
live_display = LiveDisplay()

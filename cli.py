#!/usr/bin/env python3
"""
FlutterSwarm CLI - Command line interface for the FlutterSwarm system.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from flutter_swarm import FlutterSwarm
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.panel import Panel
from config.config_manager import get_config

# Initialize configuration-aware console
config = get_config()
cli_config = config.get_cli_config()
console = Console(width=cli_config.get('console_width', 80))

class FlutterSwarmCLI:
    """Command line interface for FlutterSwarm."""
    
    def __init__(self):
        self.swarm = None
        self.config = get_config()
        self.cli_config = self.config.get_cli_config()
        self.display_config = self.config.get_display_config()
        self.messages = self.config.get_messages_config()
        
    async def create_project(self, args):
        """Create a new Flutter project."""
        create_msg = self.messages.get('project_creating', '� Creating new Flutter project...')
        console.print(f"🐝 [bold blue]{create_msg}[/bold blue]")
        
        # Parse requirements if provided
        requirements = []
        if args.requirements:
            requirements = [req.strip() for req in args.requirements.split(',')]
        
        # Parse features if provided
        features = []
        if args.features:
            features = [feat.strip() for feat in args.features.split(',')]
        
        self.swarm = FlutterSwarm()
        
        project_id = self.swarm.create_project(
            name=args.name,
            description=args.description,
            requirements=requirements,
            features=features
        )
        
        success_msg = self.messages.get('build_complete', '✅ Project created successfully!')
        console.print(f"[green]{success_msg}[/green]")
        
        # Use configurable ID length for display
        id_length = self.display_config.get('project_id_length', 8)
        displayed_id = project_id[:id_length] + '...' if len(project_id) > id_length else project_id
        console.print(f"📋 Project ID: [bold]{displayed_id}[/bold]")
        
        if args.build:
            building_msg = self.messages.get('building', '🔨 Starting build process...')
            console.print(f"\n🏗️  [bold blue]{building_msg}[/bold blue]")
            await self.build_project_with_progress(project_id, args.platforms.split(',') if args.platforms else None)
    
    async def build_project_with_progress(self, project_id: str, platforms=None):
        """Build project with live progress display and monitoring."""
        # Import monitoring here to avoid circular imports
        from monitoring import live_display
        
        console.print("\n🔍 [bold green]Starting live monitoring...[/bold green]")
        console.print("📊 You can see real-time agent activities below:")
        console.print("💡 [dim]Press Ctrl+C to stop (monitoring will continue in background)[/dim]\n")
        
        try:
            # Start live display in parallel with build
            live_display.start()
            
            # Start build
            build_task = asyncio.create_task(
                self.swarm.build_project(project_id, platforms)
            )
            
            # Wait for build to complete or user interruption
            result = await build_task
            
            # Display results
            self.display_build_results(result)
            
        except KeyboardInterrupt:
            console.print("\n⏸️ [yellow]Live monitoring interrupted by user[/yellow]")
            console.print("🔄 [dim]Build process continues in background...[/dim]")
            
            # Wait a bit for the build to potentially complete
            try:
                result = await asyncio.wait_for(build_task, timeout=5.0)
                self.display_build_results(result)
            except asyncio.TimeoutError:
                console.print("⏰ [yellow]Build still in progress. Check logs for updates.[/yellow]")
            
        finally:
            # Stop live display
            live_display.stop()
    
    def display_build_results(self, result):
        """Display build results in a nice format."""
        console.print("\n🎉 [bold green]Build Results[/bold green]")
        
        # Get table headers from config
        table_headers = self.display_config.get('table_headers', {})
        project_headers = table_headers.get('projects', ['Metric', 'Value'])
        
        table = Table(title="Project Summary")
        table.add_column(project_headers[0], style="cyan")
        table.add_column(project_headers[1], style="magenta")
        
        table.add_row("Status", result.get('status', 'Unknown'))
        table.add_row("Files Created", str(result.get('files_created', 0)))
        table.add_row("Architecture Decisions", str(result.get('architecture_decisions', 0)))
        table.add_row("Security Findings", str(len(result.get('security_findings', []))))
        table.add_row("Documentation Files", str(len(result.get('documentation', []))))
        
        console.print(table)
        
        # Add LLM usage summary
        try:
            from utils.llm_logger import llm_logger
            llm_summary = llm_logger.get_session_summary()
            
            console.print(f"\n🤖 [bold blue]LLM Usage Summary[/bold blue]")
            console.print(f"  • Total Requests: {llm_summary.get('total_requests', 0)}")
            console.print(f"  • Total Tokens: {llm_summary.get('total_tokens', 0):,}")
            console.print(f"  • Success Rate: {llm_summary.get('success_rate', 0):.1%}")
            console.print(f"  • Average Duration: {llm_summary.get('average_duration', 0):.2f}s")
            console.print(f"  • Total Duration: {llm_summary.get('total_duration', 0):.2f}s")
            
            if llm_summary.get('error_count', 0) > 0:
                console.print(f"  • [red]Errors: {llm_summary.get('error_count', 0)}[/red]")
        except ImportError:
            pass
        except Exception as e:
            console.print(f"  • [red]LLM metrics error: {e}[/red]")
        
        if result.get('test_results'):
            console.print("\n📋 [bold blue]Test Results[/bold blue]")
            for test_type, results in result['test_results'].items():
                console.print(f"  • {test_type}: {results.get('status', 'Unknown')}")
    
    async def status(self, args):
        """Show project and agent status."""
        if not self.swarm:
            self.swarm = FlutterSwarm()
        
        if args.project_id:
            status = self.swarm.get_project_status(args.project_id)
            self.display_project_status(status)
        else:
            agent_status = self.swarm.get_agent_status()
            self.display_agent_status(agent_status)
    
    def display_project_status(self, status):
        """Display project status."""
        if 'error' in status:
            console.print(f"❌ [red]{status['error']}[/red]")
            return
        
        project = status['project']
        agents = status['agents']
        
        # Project info panel
        project_info = f"""
[bold]Name:[/bold] {project['name']}
[bold]Phase:[/bold] {project['current_phase']}
[bold]Progress:[/bold] {project['progress']:.1%}
[bold]Files:[/bold] {project['files_created']}
[bold]Architecture Decisions:[/bold] {project['architecture_decisions']}
[bold]Security Findings:[/bold] {project['security_findings']}
        """
        
        console.print(Panel(project_info, title="📋 Project Status", border_style="blue"))
        
        # Agent status table
        table = Table(title="🤖 Agent Status")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Current Task", style="yellow")
        table.add_column("Progress", style="magenta")
        
        for agent_id, agent_info in agents.items():
            status_emoji = {
                'idle': '💤',
                'working': '🔄',
                'waiting': '⏳',
                'completed': '✅',
                'error': '❌'
            }.get(agent_info['status'], '❓')
            
            table.add_row(
                agent_id.title(),
                f"{status_emoji} {agent_info['status']}",
                agent_info['current_task'] or 'None',
                f"{agent_info['progress']:.1%}"
            )
        
        console.print(table)
    
    def display_agent_status(self, agent_status):
        """Display agent status."""
        table = Table(title="🤖 All Agents Status")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green") 
        table.add_column("Current Task", style="yellow")
        table.add_column("Last Update", style="blue")
        
        for agent_id, info in agent_status.items():
            status_emoji = {
                'idle': '💤',
                'working': '🔄', 
                'waiting': '⏳',
                'completed': '✅',
                'error': '❌'
            }.get(info['status'], '❓')
            
            table.add_row(
                agent_id.title(),
                f"{status_emoji} {info['status']}",
                info['current_task'] or 'None',
                info['last_update'][:19]  # Truncate timestamp
            )
        
        console.print(table)
    
    async def run_interactive(self, args):
        """Run interactive FlutterSwarm session."""
        console.print("🐝 [bold blue]Starting FlutterSwarm Interactive Mode[/bold blue]")
        console.print("Type 'help' for available commands or 'quit' to exit")
        
        self.swarm = FlutterSwarm()
        
        # Start agents in background
        swarm_task = asyncio.create_task(self.swarm.start())
        
        try:
            while True:
                command = console.input("\n[bold cyan]FlutterSwarm>[/bold cyan] ")
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    self.show_interactive_help()
                elif command.startswith('create'):
                    await self.handle_interactive_create(command)
                elif command.startswith('status'):
                    await self.handle_interactive_status(command)
                elif command.startswith('list'):
                    self.handle_interactive_list()
                else:
                    console.print(f"❓ Unknown command: {command}")
                    
        except KeyboardInterrupt:
            pass
        finally:
            console.print("\n🛑 [yellow]Shutting down FlutterSwarm...[/yellow]")
            await self.swarm.stop()
    
    def show_interactive_help(self):
        """Show help for interactive mode."""
        help_text = """
[bold blue]Available Commands:[/bold blue]

[bold]create <name> [description][/bold] - Create a new Flutter project
[bold]status [project_id][/bold] - Show project or agent status  
[bold]list[/bold] - List all projects
[bold]help[/bold] - Show this help message
[bold]quit/exit/q[/bold] - Exit FlutterSwarm

[bold blue]Examples:[/bold blue]
  create MyApp "A todo application"
  status 
  status abc-123-def
  list
        """
        console.print(help_text)
    
    async def handle_interactive_create(self, command):
        """Handle create command in interactive mode."""
        parts = command.split(maxsplit=2)
        if len(parts) < 2:
            console.print("❌ Usage: create <name> [description]")
            return
        
        name = parts[1]
        description = parts[2] if len(parts) > 2 else f"Flutter application: {name}"
        
        project_id = self.swarm.create_project(name, description)
        console.print(f"✅ Created project '{name}' with ID: {project_id}")
    
    async def handle_interactive_status(self, command):
        """Handle status command in interactive mode."""
        parts = command.split()
        if len(parts) > 1:
            project_id = parts[1]
            status = self.swarm.get_project_status(project_id)
            self.display_project_status(status)
        else:
            agent_status = self.swarm.get_agent_status()
            self.display_agent_status(agent_status)
    
    def handle_interactive_list(self):
        """Handle list command in interactive mode."""
        projects = self.swarm.list_projects()
        if not projects:
            no_projects_msg = self.messages.get('no_projects', '📭 No projects found')
            console.print(no_projects_msg)
            return
        
        # Get table headers from config
        table_headers = self.display_config.get('table_headers', {})
        project_headers = table_headers.get('projects', ['ID', 'Name', 'Phase', 'Progress'])
        
        table = Table(title="📋 Projects")
        table.add_column(project_headers[0], style="cyan")
        table.add_column(project_headers[1], style="green")
        table.add_column(project_headers[2], style="yellow") 
        table.add_column(project_headers[3], style="magenta")
        
        # Get display settings from config
        id_length = self.display_config.get('project_id_length', 8)
        progress_format = self.display_config.get('progress_format', '{:.1%}')
        
        for project in projects:
            displayed_id = project['id'][:id_length] + '...' if len(project['id']) > id_length else project['id']
            progress_str = progress_format.format(project['progress'])
            
            table.add_row(
                displayed_id,
                project['name'],
                project['current_phase'],
                progress_str
            )
        
        console.print(table)
    
    async def monitor(self, args):
        """Start live monitoring for a project or general system monitoring."""
        from monitoring import live_display, build_monitor, agent_logger
        
        if args.project_id:
            # Monitor specific project
            console.print(f"🔍 [bold green]Starting monitoring for project: {args.project_id[:8]}...[/bold green]")
        else:
            # General system monitoring
            console.print("🔍 [bold green]Starting general FlutterSwarm monitoring...[/bold green]")
        
        console.print("📊 Real-time agent activities, tool usage, and collaboration")
        console.print("💡 [dim]Press Ctrl+C to stop monitoring[/dim]\n")
        
        # Initialize swarm if needed
        if not self.swarm:
            self.swarm = FlutterSwarm(enable_monitoring=True)
            await self.swarm.start()
        
        try:
            # Start live display
            live_display.start()
            
            # If monitoring a specific project, start build monitoring
            if args.project_id:
                build_monitor.start_monitoring(args.project_id)
            
            # Keep monitoring until interrupted
            console.print("🔄 [dim]Monitoring active... (Ctrl+C to stop)[/dim]")
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            console.print("\n⏸️ [yellow]Monitoring stopped by user[/yellow]")
            
        finally:
            # Stop monitoring components
            live_display.stop()
            
            if build_monitor.is_monitoring:
                summary = build_monitor.stop_monitoring()
                console.print(f"\n📊 [bold]Monitoring Summary:[/bold]")
                console.print(f"⏱️ Duration: {summary.get('build_duration', 'Unknown')}")
                console.print(f"🔧 Tool calls: {summary.get('total_tool_calls', 0)}")
                console.print(f"📈 Events: {summary.get('total_events', 0)}")
                
                # Offer to export reports
                if summary.get('total_events', 0) > 0:
                    export = console.input("\n📄 Export detailed report? (y/n): ").strip().lower()
                    if export in ['y', 'yes']:
                        report_file = build_monitor.export_build_report()
                        log_file = agent_logger.export_logs_to_json()
                        console.print(f"✅ Reports saved:")
                        console.print(f"   🏗️ Build report: {report_file}")
                        console.print(f"   📋 Detailed logs: {log_file}")
                
            await self.swarm.stop()
    
    async def logs(self, args):
        """Show or export logs from previous sessions."""
        from monitoring import agent_logger
        import os
        import json
        from pathlib import Path
        
        if args.export:
            # Export current session logs
            filename = args.filename or f"flutterswarm_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = agent_logger.export_logs_to_json(filename)
            console.print(f"📄 Logs exported to: {filepath}")
            
        elif args.list:
            # List available log files
            logs_dir = Path("logs")
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.json"))
                if log_files:
                    console.print("📋 [bold]Available log files:[/bold]")
                    for log_file in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True):
                        size = log_file.stat().st_size
                        modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                        console.print(f"  📄 {log_file.name} ({size:,} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
                else:
                    console.print("📭 No log files found")
            else:
                console.print("📭 Logs directory not found")
                
        elif args.show:
            # Show logs from specific file or current session
            if args.filename:
                # Load from file
                try:
                    with open(args.filename, 'r') as f:
                        log_data = json.load(f)
                    
                    console.print(f"📋 [bold]Logs from: {args.filename}[/bold]")
                    console.print(f"📅 Session: {log_data.get('session_id', 'Unknown')}")
                    console.print(f"⏱️ Duration: {log_data.get('session_start', 'Unknown')}")
                    console.print(f"📊 Total entries: {log_data.get('total_entries', 0)}\n")
                    
                    # Show recent entries
                    logs = log_data.get('logs', [])
                    recent_logs = logs[-args.limit:] if args.limit else logs[-20:]
                    
                    for entry in recent_logs:
                        timestamp = entry['timestamp'][:19]  # Remove microseconds
                        level_color = {
                            'DEBUG': 'dim',
                            'INFO': 'blue',
                            'WARNING': 'yellow', 
                            'ERROR': 'red'
                        }.get(entry['level'], 'white')
                        
                        console.print(f"[dim]{timestamp}[/dim] [{level_color}]{entry['level']}[/{level_color}] {entry['agent_id']}: {entry['message']}")
                        
                except FileNotFoundError:
                    console.print(f"❌ Log file not found: {args.filename}")
                except json.JSONDecodeError:
                    console.print(f"❌ Invalid log file format: {args.filename}")
                    
            else:
                # Show current session logs
                summary = agent_logger.get_session_summary()
                console.print("📋 [bold]Current Session Logs[/bold]")
                console.print(f"📅 Session: {summary.get('session_id', 'Unknown')}")
                console.print(f"⏱️ Duration: {summary.get('session_duration', 'Unknown')}")
                console.print(f"📊 Total entries: {summary.get('total_entries', 0)}")
                console.print(f"❌ Errors: {summary.get('error_count', 0)}\n")
                
                # Show recent entries
                recent_logs = agent_logger.get_recent_logs(args.limit or 20)
                for entry in recent_logs:
                    timestamp = entry.timestamp.strftime('%H:%M:%S')
                    level_color = {
                        'DEBUG': 'dim',
                        'INFO': 'blue', 
                        'WARNING': 'yellow',
                        'ERROR': 'red'
                    }.get(entry.level, 'white')
                    
                    console.print(f"[dim]{timestamp}[/dim] [{level_color}]{entry.level}[/{level_color}] {entry.agent_id}: {entry.message}")
        else:
            # Default: show current session summary
            summary = agent_logger.get_session_summary()
            console.print("📋 [bold]Current Logging Session[/bold]")
            
            # Session info
            console.print(f"📅 Session ID: {summary.get('session_id', 'Unknown')}")
            console.print(f"⏱️ Duration: {summary.get('session_duration', 'Unknown')}")
            console.print(f"📊 Total entries: {summary.get('total_entries', 0)}")
            console.print(f"❌ Errors: {summary.get('error_count', 0)}")
            
            # Events by type
            events = summary.get('events_by_type', {})
            if events:
                console.print("\n📈 [bold]Events by type:[/bold]")
                for event_type, count in sorted(events.items(), key=lambda x: x[1], reverse=True):
                    console.print(f"  {event_type}: {count}")
            
            # Entries by agent
            agents = summary.get('entries_by_agent', {})
            if agents:
                console.print("\n🤖 [bold]Activity by agent:[/bold]")
                for agent_id, count in sorted(agents.items(), key=lambda x: x[1], reverse=True):
                    console.print(f"  {agent_id}: {count}")
            
            console.print(f"\n💡 Use --show to see detailed logs or --export to save them")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FlutterSwarm - Multi-Agent Flutter Development System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flutter-swarm create MyApp "A todo application" --build
  flutter-swarm status --project-id abc-123
  flutter-swarm interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new Flutter project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('description', help='Project description')
    create_parser.add_argument('--requirements', help='Comma-separated list of requirements')
    create_parser.add_argument('--features', help='Comma-separated list of features')
    create_parser.add_argument('--platforms', default='android,ios', help='Target platforms')
    create_parser.add_argument('--build', action='store_true', help='Build project after creation')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show project or agent status')
    status_parser.add_argument('--project-id', help='Specific project ID to check')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start live monitoring')
    monitor_parser.add_argument('--project-id', help='Specific project ID to monitor')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show or export logs')
    logs_parser.add_argument('--export', action='store_true', help='Export logs to a file')
    logs_parser.add_argument('--show', action='store_true', help='Show logs in the console')
    logs_parser.add_argument('--list', action='store_true', help='List available log files')
    logs_parser.add_argument('--filename', help='Log file name (for export or display)')
    logs_parser.add_argument('--limit', type=int, default=20, help='Number of log entries to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = FlutterSwarmCLI()
    
    try:
        if args.command == 'create':
            asyncio.run(cli.create_project(args))
        elif args.command == 'status':
            asyncio.run(cli.status(args))
        elif args.command == 'interactive':
            asyncio.run(cli.run_interactive(args))
        elif args.command == 'monitor':
            asyncio.run(cli.monitor(args))
        elif args.command == 'logs':
            asyncio.run(cli.logs(args))
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()

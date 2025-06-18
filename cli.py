#!/usr/bin/env python3
"""
FlutterSwarm CLI - Command line interface for the FlutterSwarm system.
"""

import argparse
import asyncio
import json
import sys
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
        """Build project with live progress display."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            building_msg = self.messages.get('building', 'Building Flutter project...')
            task = progress.add_task(building_msg, total=None)
            
            # Start build in background
            build_task = asyncio.create_task(
                self.swarm.build_project(project_id, platforms)
            )
            
            # Get update frequency from config
            update_frequency = self.config.get_interval_setting('progress_update')
            
            # Monitor progress
            while not build_task.done():
                status = self.swarm.get_project_status(project_id)
                if 'project' in status:
                    project_info = status['project']
                    progress_format = self.display_config.get('progress_format', '{:.1%}')
                    progress_str = progress_format.format(project_info['progress'])
                    progress.update(
                        task, 
                        description=f"Phase: {project_info['current_phase']} - Progress: {progress_str}"
                    )
                
                await asyncio.sleep(update_frequency)
            
            # Get final result
            result = await build_task
            complete_msg = self.messages.get('build_complete', '✅ Build completed!')
            progress.update(task, description=complete_msg)
        
        # Display results
        self.display_build_results(result)
    
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
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()

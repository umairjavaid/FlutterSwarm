#!/usr/bin/env python3
"""
FlutterSwarm Live Monitoring Demo
Demonstrates the live monitoring capabilities during Flutter app development.
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from flutter_swarm import FlutterSwarm
from monitoring import build_monitor, live_display, agent_logger
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class MonitoringDemo:
    """Demonstrates FlutterSwarm's live monitoring capabilities."""
    
    def __init__(self):
        self.swarm = None
        self.current_project_id = None
        self.demo_running = True
        
    async def run_demo(self):
        """Run the complete monitoring demo."""
        console.print(Panel.fit(
            Text("🐝 FlutterSwarm Live Monitoring Demo", style="bold blue"),
            border_style="blue"
        ))
        
        console.print("\n📖 [bold]What you'll see:[/bold]")
        console.print("• Real-time agent status updates")
        console.print("• Tool usage tracking")
        console.print("• Agent collaboration messages")
        console.print("• Build phase progress")
        console.print("• Performance metrics")
        console.print("\n💡 [dim]Press Ctrl+C to stop monitoring and see summary[/dim]\n")
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        try:
            # Initialize FlutterSwarm with monitoring enabled
            self.swarm = FlutterSwarm(enable_monitoring=True)
            await self.swarm.start()
            
            # Create a demo project
            console.print("🏗️ [bold green]Creating demo Flutter project...[/bold green]")
            project_id = self.swarm.create_project(
                name="MonitoringDemo",
                description="A demo Flutter app to showcase live monitoring",
                requirements=["user authentication", "music player", "offline sync"],
                features=["auth", "media", "database"]
            )
            self.current_project_id = project_id
            
            console.print(f"✅ Project created: {project_id[:8]}...")
            console.print("\n🔍 [bold yellow]Starting live monitoring...[/bold yellow]")
            
            # Start the build process with live monitoring
            await self._run_monitored_build(project_id)
            
        except KeyboardInterrupt:
            console.print("\n⏸️ [yellow]Demo interrupted by user[/yellow]")
        except Exception as e:
            console.print(f"\n❌ [red]Demo error: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def _run_monitored_build(self, project_id: str):
        """Run the build process with full monitoring."""
        # Start live display
        live_display.start()
        
        try:
            # Build the project (this will trigger all agent activities)
            result = await self.swarm.build_project(
                project_id, 
                platforms=["android", "ios"]
            )
            
            console.print("\n🎉 [bold green]Build completed![/bold green]")
            self._display_final_results(result)
            
        except asyncio.CancelledError:
            console.print("\n⏰ [yellow]Build process cancelled[/yellow]")
        finally:
            # Stop live display
            live_display.stop()
    
    def _display_final_results(self, result: dict):
        """Display final build results and monitoring summary."""
        console.print("\n" + "─"*50)
        console.print("📊 [bold blue]FINAL MONITORING SUMMARY[/bold blue]")
        console.print("─"*50)
        
        # Build results
        console.print(f"✅ Status: {result.get('status', 'Unknown')}")
        console.print(f"📁 Files created: {result.get('files_created', 0)}")
        console.print(f"🏛️ Architecture decisions: {result.get('architecture_decisions', 0)}")
        console.print(f"🔒 Security findings: {len(result.get('security_findings', []))}")
        console.print(f"📚 Documentation files: {len(result.get('documentation', []))}")
        
        # Monitoring summary
        if build_monitor.is_monitoring:
            summary = build_monitor.get_build_summary()
            console.print(f"\n🔧 Total tool calls: {summary.get('total_tool_calls', 0)}")
            console.print(f"👥 Active agents: {len(summary.get('active_agents', []))}")
            console.print(f"⏱️ Build duration: {summary.get('build_duration', 'Unknown')}")
            console.print(f"📈 Build events: {summary.get('total_events', 0)}")
        
        # Agent logger summary
        logger_summary = agent_logger.get_session_summary()
        console.print(f"\n📝 Log entries: {logger_summary.get('total_entries', 0)}")
        console.print(f"❌ Errors logged: {logger_summary.get('error_count', 0)}")
        console.print(f"⏰ Session duration: {logger_summary.get('session_duration', 'Unknown')}")
        
        # Export reports
        console.print("\n📄 [bold]Exporting detailed reports...[/bold]")
        
        # Export build report
        if build_monitor.is_monitoring:
            build_report = build_monitor.export_build_report()
            console.print(f"🏗️ Build report: {build_report}")
        
        # Export logs
        log_file = agent_logger.export_logs_to_json()
        console.print(f"📋 Detailed logs: {log_file}")
        
        console.print("\n💡 [dim]Check the exported files for complete details![/dim]")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signal for graceful shutdown."""
        self.demo_running = False
    
    async def _cleanup(self):
        """Clean up resources."""
        console.print("\n🧹 [dim]Cleaning up...[/dim]")
        
        if self.swarm:
            await self.swarm.stop()
        
        # Stop monitoring components
        if live_display.is_running:
            live_display.stop()
        
        if build_monitor.is_monitoring:
            build_monitor.stop_monitoring()


async def main():
    """Main entry point for the demo."""
    demo = MonitoringDemo()
    await demo.run_demo()


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 [blue]Demo finished![/blue]")
    except Exception as e:
        console.print(f"\n❌ [red]Demo failed: {e}[/red]")
        sys.exit(1)

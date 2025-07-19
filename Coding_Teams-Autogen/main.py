#!/usr/bin/env python3
"""
Multi-Agent Coding Team - Main Entry Point

This system creates an autonomous coding team that takes a problem statement
and delivers a fully-working solution through collaborative multi-agent workflow.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.team.coding_team import CodingTeam, CodingTeamConfig

# Load environment variables
load_dotenv()

app = typer.Typer(help="Multi-Agent Coding Team System")
console = Console()

def get_claude_config() -> Dict[str, Any]:
    """Get Claude API configuration"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY environment variable not set[/red]")
        console.print("Please set your Anthropic API key in a .env file or environment variable")
        sys.exit(1)
    
    return {
        "config_list": [
            {
                "model": "claude-3-haiku-20240307",
                "api_key": api_key,
                "api_type": "anthropic",
                "temperature": 0.3,
                "max_tokens": 2048,
                "stream": True,
            }
        ]
    }

@app.command()
def solve(
    problem: str = typer.Argument(help="The problem statement to solve"),
    output_dir: str = typer.Option("output", help="Output directory for results"),
    timeout: int = typer.Option(10, help="Step timeout in minutes"),
    verbose: bool = typer.Option(False, help="Enable verbose logging"),
    no_ui: bool = typer.Option(False, help="Disable rich UI"),
    cache: bool = typer.Option(True, help="Enable intelligent caching"),
    progress: bool = typer.Option(True, help="Enable real-time progress tracking"),
    analysis: bool = typer.Option(True, help="Enable code analysis and search"),
    ui: bool = typer.Option(True, help="Enable rich UI and monitoring"),
    cache_cycle: int = typer.Option(5, help="Cache write cycle in minutes"),
    batch_size: int = typer.Option(3, help="Number of parallel agents for batch processing"),
    streaming: bool = typer.Option(True, help="Enable streaming responses"),
):
    """
    Solve a coding problem using the multi-agent team
    
    Example:
        python main.py solve "Create a REST API for a todo list application"
        python main.py solve "Create a REST API" --cache --progress --analysis --ui --batch-size 3
    """
    asyncio.run(solve_problem_async(problem, output_dir, timeout, verbose, ui and not no_ui, cache, progress, analysis, cache_cycle, batch_size, streaming))

@app.command()
def interactive():
    """Start an interactive session to define and solve problems"""
    console.print(Panel(
        "[bold blue]🤖 Multi-Agent Coding Team - Interactive Mode[/bold blue]\n\n"
        "Welcome to the interactive problem solving session!\n"
        "This system will help you break down complex coding problems\n"
        "and solve them using a collaborative team of AI agents.",
        title="Interactive Mode",
        border_style="blue"
    ))
    
    # Get problem statement
    problem = Prompt.ask("\n[bold green]What coding problem would you like to solve?[/bold green]")
    
    # Get configuration options
    output_dir = Prompt.ask("Output directory", default="output")
    timeout = int(Prompt.ask("Step timeout (minutes)", default="30"))
    verbose = Confirm.ask("Enable verbose logging?", default=False)
    enable_ui = Confirm.ask("Enable rich UI?", default=True)
    
    # Confirm before starting
    console.print(f"\n[bold]Problem:[/bold] {problem}")
    console.print(f"[bold]Output Directory:[/bold] {output_dir}")
    console.print(f"[bold]Timeout:[/bold] {timeout} minutes")
    console.print(f"[bold]Verbose:[/bold] {verbose}")
    console.print(f"[bold]Rich UI:[/bold] {enable_ui}")
    
    if not Confirm.ask("\nProceed with these settings?"):
        console.print("Cancelled.")
        return
    
    asyncio.run(solve_problem_async(problem, output_dir, timeout, verbose, enable_ui, True, True, True, 5, 3, True))

@app.command()
def example():
    """Run an example problem to demonstrate the system"""
    example_problem = """
    Create a web-based task management application with the following features:
    
    1. User authentication (login/logout)
    2. Create, read, update, delete tasks
    3. Task categories and priorities
    4. Due dates and reminders
    5. Search and filter functionality
    6. Responsive design for mobile and desktop
    7. RESTful API backend
    8. Database for data persistence
    9. Unit and integration tests
    10. Deployment configuration
    
    Technical requirements:
    - Use modern web technologies (React/Vue.js for frontend)
    - Node.js/Express or Python/FastAPI for backend
    - PostgreSQL or MongoDB for database
    - JWT for authentication
    - Docker for containerization
    - CI/CD pipeline setup
    """
    
    console.print(Panel(
        "[bold blue]🚀 Running Example Problem[/bold blue]\n\n"
        "This will demonstrate the multi-agent coding team solving\n"
        "a comprehensive web application development problem.",
        title="Example Execution",
        border_style="blue"
    ))
    
    if not Confirm.ask("Run the example problem?"):
        console.print("Cancelled.")
        return
    
    asyncio.run(solve_problem_async(example_problem, "example_output", 15, True, True, True, True, True, 5, 4, True))

async def solve_problem_async(
    problem: str, 
    output_dir: str, 
    timeout: int, 
    verbose: bool, 
    enable_ui: bool,
    enable_cache: bool = True,
    enable_progress: bool = True,
    enable_analysis: bool = True,
    cache_cycle: int = 5,
    batch_size: int = 3,
    streaming: bool = True
):
    """Async function to solve the problem"""
    try:
        # Create configuration
        config = CodingTeamConfig(
            claude_config=get_claude_config(),
            output_directory=output_dir,
            log_level="DEBUG" if verbose else "INFO",
            step_timeout_minutes=timeout,
            enable_rich_ui=enable_ui,
            enable_caching=enable_cache,
            enable_progress_tracking=enable_progress,
            enable_code_analysis=enable_analysis,
            cache_write_cycle_minutes=cache_cycle,
            batch_processing_size=batch_size,
            enable_streaming=streaming
        )
        
        # Create and run the coding team
        team = CodingTeam(config)
        
        console.print(Panel(
            "[bold green]🎯 Problem Analysis Starting...[/bold green]\n\n"
            "The multi-agent team is now analyzing your problem and\n"
            "creating a comprehensive solution plan.",
            title="Execution Started",
            border_style="green"
        ))
        
        # Solve the problem
        result = await team.solve_problem(problem)
        
        console.print(Panel(
            f"[bold green]✅ Problem Solved Successfully![/bold green]\n\n"
            f"[bold]Output Directory:[/bold] {output_dir}\n"
            f"[bold]Project Name:[/bold] {result.get('project_name', 'Unknown')}\n"
            f"[bold]Duration:[/bold] {result.get('duration_seconds', 0):.1f} seconds\n"
            f"[bold]Steps Completed:[/bold] {result.get('progress', {}).get('completed_steps', 0)}\n"
            f"[bold]Artifacts Generated:[/bold] {len(result.get('artifacts', []))}\n\n"
            f"Check the output directory for all generated files and documentation.",
            title="🎉 Success!",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Execution interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print("[red]Check the logs for more details.[/red]")
        sys.exit(1)

@app.command()
def status():
    """Check system status and requirements"""
    console.print(Panel(
        "[bold blue]🔍 System Status Check[/bold blue]",
        title="Status",
        border_style="blue"
    ))
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        console.print("[green]✅ Anthropic API Key: Configured[/green]")
    else:
        console.print("[red]❌ Anthropic API Key: Not configured[/red]")
        console.print("[yellow]Please set ANTHROPIC_API_KEY in your environment[/yellow]")
    
    # Check dependencies
    try:
        import autogen
        console.print("[green]✅ AutoGen: Installed[/green]")
    except ImportError:
        console.print("[red]❌ AutoGen: Not installed[/red]")
    
    try:
        import anthropic
        console.print("[green]✅ Anthropic: Installed[/green]")
    except ImportError:
        console.print("[red]❌ Anthropic: Not installed[/red]")
    
    try:
        import rich
        console.print("[green]✅ Rich: Installed[/green]")
    except ImportError:
        console.print("[red]❌ Rich: Not installed[/red]")
    
    # Check directories
    if os.path.exists("src"):
        console.print("[green]✅ Source directory: Found[/green]")
    else:
        console.print("[red]❌ Source directory: Not found[/red]")
    
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("• solve: Solve a specific problem")
    console.print("• interactive: Start interactive mode")
    console.print("• example: Run example problem")
    console.print("• status: Check system status")

if __name__ == "__main__":
    app() 
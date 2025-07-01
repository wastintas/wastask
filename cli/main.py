"""
WasTask CLI - Command line interface for project management
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from wastask.agents.coordinator.agent import coordinator
from wastask.agents.planning.agent import planning_agent
from wastask.config.settings import settings


console = Console()


def handle_async(func):
    """Decorator to handle async functions in Click commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def cli(ctx, verbose, config):
    """
    WasTask - AI-native project management system
    
    A comprehensive project management tool powered by AI agents
    for intelligent task decomposition, planning, and execution.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    if verbose:
        console.print(f"[bold green]WasTask CLI v{settings.version}[/bold green]")
        console.print(f"Using model: {settings.adk_model_default}")


@cli.group()
def project():
    """Project management commands"""
    pass


@project.command()
@click.option('--name', '-n', required=True, help='Project name')
@click.option('--description', '-d', help='Project description')
@click.option('--github-repo', '-g', help='GitHub repository (owner/repo)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@handle_async
async def create(name, description, github_repo, interactive):
    """Create a new project"""
    try:
        if interactive:
            console.print(Panel("[bold blue]Creating New Project[/bold blue]", expand=False))
            
            if not name:
                name = Prompt.ask("Project name")
            
            if not description:
                description = Prompt.ask("Project description", default="")
            
            if not github_repo:
                if Confirm.ask("Link to GitHub repository?"):
                    github_repo = Prompt.ask("GitHub repository (owner/repo)")
        
        with console.status("[bold green]Creating project..."):
            result = await coordinator.agent.run(
                f"Create a new project with name '{name}', description '{description}', "
                f"and GitHub repo '{github_repo or 'None'}'"
            )
        
        if result:
            console.print(f"[bold green]✓[/bold green] Project '{name}' created successfully!")
            console.print(f"[dim]Result: {result.content}[/dim]")
        else:
            console.print(f"[bold red]✗[/bold red] Failed to create project")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@project.command()
@click.option('--status', '-s', help='Filter by status')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'simple']), default='table', help='Output format')
@handle_async
async def list(status, format):
    """List all projects"""
    try:
        with console.status("[bold green]Fetching projects..."):
            response = await coordinator.process_message(
                user_id="cli_user",
                message=f"List all projects{' with status ' + status if status else ''}"
            )
        
        if format == 'json':
            console.print(json.dumps({"response": response.response}, indent=2))
        elif format == 'simple':
            console.print(response.response)
        else:
            # Table format
            table = Table(title="Projects")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Status", style="green")
            table.add_column("Tasks", justify="right")
            table.add_column("Created", style="dim")
            
            # This would be populated with actual data in a real implementation
            table.add_row("proj_0001", "Sample Project", "active", "5", "2025-01-01")
            
            console.print(table)
            console.print(f"\n[dim]Response: {response.response}[/dim]")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@project.command()
@click.argument('project_id')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'detailed']), default='detailed', help='Output format')
@handle_async
async def show(project_id, format):
    """Show project details"""
    try:
        with console.status(f"[bold green]Fetching project {project_id}..."):
            response = await coordinator.process_message(
                user_id="cli_user",
                message=f"Show details for project {project_id}",
                project_id=project_id
            )
        
        if format == 'json':
            console.print(json.dumps({"response": response.response}, indent=2))
        elif format == 'table':
            console.print(response.response)
        else:
            # Detailed format
            console.print(Panel(f"[bold]Project: {project_id}[/bold]", expand=False))
            console.print(Markdown(response.response))
            
            if response.suggestions:
                console.print("\n[bold cyan]Suggestions:[/bold cyan]")
                for suggestion in response.suggestions:
                    console.print(f"• {suggestion}")
                    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@project.command()
@click.argument('project_id')
@click.argument('description')
@click.option('--method', '-m', type=click.Choice(['agile', 'waterfall', 'hybrid']), default='agile', help='Planning methodology')
@click.option('--team-size', '-t', type=int, default=2, help='Team size')
@click.option('--duration', '-d', type=int, help='Target duration in days')
@handle_async
async def plan(project_id, description, method, team_size, duration):
    """Create a detailed project plan"""
    try:
        constraints = {}
        if duration:
            constraints['max_duration_days'] = duration
        
        preferences = {
            'methodology': method,
            'team_size': team_size
        }
        
        with console.status("[bold green]Creating project plan..."):
            result = await planning_agent.create_project_plan(
                project_description=description,
                constraints=constraints,
                preferences=preferences
            )
        
        if result['status'] == 'success':
            plan = result['plan']
            
            console.print(Panel(f"[bold]Project Plan: {plan['project_summary']['title']}[/bold]", expand=False))
            console.print(f"[bold]Description:[/bold] {plan['project_summary']['description']}")
            
            # Show phases
            console.print("\n[bold cyan]Phases:[/bold cyan]")
            for i, phase in enumerate(plan['phases'], 1):
                console.print(f"{i}. [bold]{phase['name']}[/bold] ({phase['duration_days']} days)")
                console.print(f"   {phase['description']}")
                console.print(f"   Tasks: {len(phase['tasks'])}")
            
            # Show timeline
            timeline = plan['timeline']
            console.print(f"\n[bold cyan]Timeline:[/bold cyan]")
            console.print(f"Duration: {timeline['total_duration_days']} days")
            console.print(f"Start: {timeline['start_date']}")
            console.print(f"End: {timeline['end_date']}")
            
            # Show risks
            if plan.get('risks'):
                console.print(f"\n[bold yellow]Key Risks:[/bold yellow]")
                for risk in plan['risks'][:3]:
                    console.print(f"• {risk['risk']} ({risk['probability']}/{risk['impact']})")
            
            # Save plan option
            if Confirm.ask("\nSave detailed plan to file?"):
                filename = f"project_plan_{project_id}.json"
                with open(filename, 'w') as f:
                    json.dump(plan, f, indent=2)
                console.print(f"[green]Plan saved to {filename}[/green]")
        else:
            console.print(f"[bold red]✗[/bold red] Failed to create plan: {result['message']}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.group()
def task():
    """Task management commands"""
    pass


@task.command()
@click.option('--project', '-p', required=True, help='Project ID')
@click.option('--title', '-t', required=True, help='Task title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']), default='medium', help='Task priority')
@click.option('--assignee', '-a', help='Assignee ID')
@handle_async
async def create(project, title, description, priority, assignee):
    """Create a new task"""
    try:
        with console.status("[bold green]Creating task..."):
            response = await coordinator.process_message(
                user_id="cli_user",
                message=f"Create task '{title}' in project {project} with priority {priority}",
                project_id=project
            )
        
        console.print(f"[bold green]✓[/bold green] Task created successfully!")
        console.print(f"[dim]{response.response}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@task.command()
@click.option('--project', '-p', help='Filter by project ID')
@click.option('--status', '-s', help='Filter by status')
@click.option('--assignee', '-a', help='Filter by assignee')
@handle_async
async def list(project, status, assignee):
    """List tasks"""
    try:
        filters = []
        if project:
            filters.append(f"project {project}")
        if status:
            filters.append(f"status {status}")
        if assignee:
            filters.append(f"assignee {assignee}")
        
        filter_text = " and ".join(filters) if filters else ""
        
        with console.status("[bold green]Fetching tasks..."):
            response = await coordinator.process_message(
                user_id="cli_user",
                message=f"List tasks{' with ' + filter_text if filter_text else ''}",
                project_id=project
            )
        
        # Create table
        table = Table(title="Tasks")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="bold")
        table.add_column("Status", style="green")
        table.add_column("Priority", style="yellow")
        table.add_column("Project", style="dim")
        
        # This would be populated with actual data
        table.add_row("task_001", "Setup project", "completed", "high", "proj_0001")
        table.add_row("task_002", "Implement features", "in_progress", "high", "proj_0001")
        
        console.print(table)
        console.print(f"\n[dim]Response: {response.response}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@task.command()
@click.argument('task_id')
@click.argument('status', type=click.Choice(['pending', 'in_progress', 'completed', 'blocked', 'cancelled']))
@handle_async
async def status(task_id, status):
    """Update task status"""
    try:
        with console.status(f"[bold green]Updating task {task_id}..."):
            response = await coordinator.process_message(
                user_id="cli_user",
                message=f"Update task {task_id} status to {status}"
            )
        
        console.print(f"[bold green]✓[/bold green] Task {task_id} updated to {status}")
        console.print(f"[dim]{response.response}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('message')
@click.option('--project', '-p', help='Project context')
@click.option('--agent', '-a', type=click.Choice(['coordinator', 'planning', 'tasks', 'github', 'analytics']), help='Specific agent to use')
@handle_async
async def chat(message, project, agent):
    """Chat with WasTask AI assistant"""
    try:
        with console.status("[bold green]Processing..."):
            response = await coordinator.process_message(
                user_id="cli_user",
                message=message,
                project_id=project
            )
        
        console.print(Panel(f"[bold blue]WasTask Assistant[/bold blue]", expand=False))
        console.print(Markdown(response.response))
        
        if response.suggestions:
            console.print("\n[bold cyan]Suggestions:[/bold cyan]")
            for suggestion in response.suggestions:
                console.print(f"• {suggestion}")
        
        if response.actions:
            console.print("\n[bold yellow]Available Actions:[/bold yellow]")
            for action in response.actions:
                console.print(f"• {action['description']}")
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--project', '-p', help='Analyze specific project')
@handle_async
async def analyze(project):
    """Analyze project progress and performance"""
    try:
        with console.status("[bold green]Analyzing project..."):
            if project:
                response = await coordinator.process_message(
                    user_id="cli_user",
                    message=f"Analyze project {project} progress and provide insights",
                    project_id=project
                )
            else:
                response = await coordinator.process_message(
                    user_id="cli_user",
                    message="Analyze overall project portfolio and provide insights"
                )
        
        console.print(Panel("[bold blue]Project Analysis[/bold blue]", expand=False))
        console.print(Markdown(response.response))
        
        if response.suggestions:
            console.print("\n[bold cyan]Recommendations:[/bold cyan]")
            for suggestion in response.suggestions:
                console.print(f"• {suggestion}")
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration"""
    config_info = {
        "version": settings.version,
        "default_model": settings.adk_model_default,
        "complex_model": settings.adk_model_complex,
        "simple_model": settings.adk_model_simple,
        "cost_optimization": settings.cost_optimization_enabled,
        "semantic_cache": settings.semantic_cache_enabled,
        "max_daily_cost": f"${settings.max_daily_cost_usd}",
    }
    
    console.print(Panel("[bold blue]WasTask Configuration[/bold blue]", expand=False))
    
    table = Table(show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="bold")
    
    for key, value in config_info.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)


if __name__ == '__main__':
    cli()
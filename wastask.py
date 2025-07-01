#!/usr/bin/env python3
"""
WasTask - Unified CLI Entry Point
Consolidated command-line interface for WasTask project management
"""
import asyncio
import sys
import os
import json
import click
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add current path
sys.path.insert(0, os.path.abspath('.'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

console = Console()

# Import functions from existing CLIs
try:
    from wastask_simple import analyze_prd_file, display_results
except ImportError:
    analyze_prd_file = None
    display_results = None

try:
    from database_manager import WasTaskDatabase, connect_and_run
except ImportError:
    WasTaskDatabase = None
    connect_and_run = None

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    WasTask - AI-powered project management system
    
    Unified CLI for PRD analysis, task generation, and project management.
    """
    pass

# === PRD Analysis Commands ===
@cli.group()
def prd():
    """PRD analysis and enhancement commands"""
    pass

@prd.command("analyze")
@click.argument('prd_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Choice(['console', 'json', 'db']), default='console', help='Output format')
@click.option('--project-name', help='Override project name')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--interactive/--no-interactive', default=True, help='Interactive mode')
@click.option('--save-comparison', is_flag=True, help='Save PRD comparison files')
def analyze_prd_cmd(prd_file, output, project_name, verbose, interactive, save_comparison):
    """Analyze PRD and generate tasks automatically"""
    if not analyze_prd_file:
        console.print("[red]Error: PRD analysis not available. Check imports.[/red]")
        sys.exit(1)
    
    async def run_analysis():
        try:
            console.print(Panel(
                f"[bold blue]🚀 WasTask PRD Analyzer[/bold blue]\n\n"
                f"[cyan]File: {prd_file}[/cyan]\n"
                f"[yellow]Analyzing and generating tasks...[/yellow]",
                expand=False
            ))
            
            # Run analysis
            results = await analyze_prd_file(prd_file, verbose, interactive)
            
            if not results:
                console.print("[red]❌ Analysis failed[/red]")
                sys.exit(1)
            
            # Handle output
            if output == 'json':
                project_name_safe = results['project']['name'].lower().replace(' ', '_')
                output_file = f"{project_name_safe}_analysis.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                console.print(f"✅ Results saved to: {output_file}")
                
            elif output == 'db':
                if not connect_and_run:
                    console.print("[red]Database functionality not available[/red]")
                    sys.exit(1)
                
                async def save_to_db(db):
                    project_id = await db.save_project_analysis(results)
                    console.print(f"✅ Project saved to database with ID: {project_id}")
                    return project_id
                
                await connect_and_run(save_to_db)
                
            else:  # console
                display_results(results, verbose)
            
            console.print(Panel(
                f"[bold green]✅ Analysis Complete![/bold green]\n\n"
                f"[cyan]Project: {results['project']['name']}[/cyan]\n"
                f"[yellow]Tasks: {len(results.get('tasks', []))}[/yellow]",
                title="Success",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(Panel(
                f"[bold red]❌ Error[/bold red]\n\n"
                f"[red]{str(e)}[/red]",
                title="Error",
                border_style="red"
            ))
            sys.exit(1)
    
    asyncio.run(run_analysis())

# === Database Commands ===
@cli.group()
def db():
    """Database management commands"""
    pass

@db.command("setup")
def setup_db():
    """Setup database schema"""
    if not connect_and_run:
        console.print("[red]Database functionality not available[/red]")
        sys.exit(1)
    
    async def setup():
        async def create_schema(db):
            await db.create_schema()
            console.print("✅ Database schema created successfully!")
            stats = await db.get_project_stats()
            console.print(f"📊 Database ready - {stats}")
        
        await connect_and_run(create_schema)
    
    asyncio.run(setup())

@db.command("list")
def list_projects():
    """List all projects"""
    if not connect_and_run:
        console.print("[red]Database functionality not available[/red]")
        sys.exit(1)
    
    async def list_all():
        async def get_projects(db):
            projects = await db.list_projects()
            
            if not projects:
                console.print("No projects found.")
                return
            
            table = Table(title="WasTask Projects")
            table.add_column("ID", justify="right", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Status", style="green")
            table.add_column("Complexity", justify="right")
            table.add_column("Timeline")
            table.add_column("Created", style="dim")
            
            for project in projects:
                created = project['created_at'].strftime('%Y-%m-%d')
                table.add_row(
                    str(project['id']),
                    project['name'],
                    project['status'],
                    f"{project['complexity_score']:.1f}/10",
                    project['timeline'],
                    created
                )
            
            console.print(table)
        
        await connect_and_run(get_projects)
    
    asyncio.run(list_all())

@db.command("show")
@click.argument('project_id', type=int)
def show_project(project_id):
    """Show project details"""
    if not connect_and_run:
        console.print("[red]Database functionality not available[/red]")
        sys.exit(1)
    
    async def show_details():
        async def get_project(db):
            project_data = await db.get_project(project_id)
            
            if not project_data:
                console.print(f"❌ Project {project_id} not found")
                return
            
            project = project_data['project']
            
            console.print(Panel(f"[bold]Project: {project['name']}[/bold]", expand=False))
            console.print(f"📝 Description: {project['description']}")
            console.print(f"📊 Complexity: {project['complexity_score']:.1f}/10")
            console.print(f"⏱️ Timeline: {project['timeline']}")
            console.print(f"📈 Total Hours: {project['total_hours']}h")
            console.print(f"🔄 Status: {project['status']}")
            
            # Technologies
            technologies = project_data['technologies']
            if technologies:
                console.print(f"\n🛠️ Technologies ({len(technologies)}):")
                for tech in technologies:
                    confidence = "🟢" if tech['confidence'] > 0.8 else "🟡"
                    console.print(f"  {confidence} {tech['technology']} v{tech['version']}")
            
            # Tasks summary
            tasks = project_data['tasks']
            if tasks:
                task_counts = {}
                for task in tasks:
                    status = task['status']
                    task_counts[status] = task_counts.get(status, 0) + 1
                
                console.print(f"\n📝 Tasks ({len(tasks)} total):")
                for status, count in task_counts.items():
                    emoji = {"todo": "⏳", "in_progress": "🚧", "completed": "✅"}.get(status, "📋")
                    console.print(f"  {emoji} {status.replace('_', ' ').title()}: {count}")
        
        await connect_and_run(get_project)
    
    asyncio.run(show_details())

@db.command("stats")
def show_stats():
    """Show database statistics"""
    if not connect_and_run:
        console.print("[red]Database functionality not available[/red]")
        sys.exit(1)
    
    async def get_stats():
        async def show_database_stats(db):
            stats = await db.get_project_stats()
            
            table = Table(title="WasTask Database Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold")
            
            table.add_row("Total Projects", str(stats['total_projects']))
            table.add_row("Total Tasks", str(stats['total_tasks']))
            table.add_row("Completed Tasks", str(stats['completed_tasks']))
            table.add_row("Active Projects", str(stats['active_projects']))
            
            if stats['avg_complexity']:
                table.add_row("Average Complexity", f"{stats['avg_complexity']:.1f}/10")
            
            if stats['total_tasks'] > 0:
                completion_rate = (stats['completed_tasks'] / stats['total_tasks']) * 100
                table.add_row("Completion Rate", f"{completion_rate:.1f}%")
            
            console.print(table)
        
        await connect_and_run(show_database_stats)
    
    asyncio.run(get_stats())

# === Legacy Commands ===
@cli.command("demo")
@click.argument('demo_type', type=click.Choice(['simple', 'interactive', 'postgres']))
def run_demo(demo_type):
    """Run demonstration scenarios"""
    console.print(f"🎮 Running {demo_type} demo...")
    console.print("[yellow]Demo functionality consolidated - use 'prd analyze' instead[/yellow]")

@cli.command("version")
def show_version():
    """Show version information"""
    console.print(Panel(
        "[bold blue]WasTask v1.0.0[/bold blue]\n\n"
        "AI-powered project management system\n"
        "Unified CLI for PRD analysis and task generation",
        title="Version Info",
        expand=False
    ))

@cli.group()
def migrate():
    """Database migration commands"""
    pass

@migrate.command("status")
def migration_status():
    """Show migration status"""
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            "migrations/migration_manager.py", 
            "status"
        ], 
        env={**os.environ, "PYTHONPATH": "."},
        capture_output=True, 
        text=True, 
        cwd="."
        )
        
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print(f"[red]Error:[/red] {result.stderr}")
    except Exception as e:
        console.print(f"[red]Migration error:[/red] {e}")

@migrate.command("run")
def run_migrations():
    """Execute pending migrations"""
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, 
            "migrations/migration_manager.py", 
            "migrate"
        ], 
        env={**os.environ, "PYTHONPATH": "."},
        capture_output=True, 
        text=True, 
        cwd="."
        )
        
        if result.returncode == 0:
            console.print(result.stdout)
            console.print("[green]✅ Migrations completed successfully![/green]")
        else:
            console.print(f"[red]Error:[/red] {result.stderr}")
    except Exception as e:
        console.print(f"[red]Migration error:[/red] {e}")

if __name__ == '__main__':
    cli()
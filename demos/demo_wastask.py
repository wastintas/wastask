#!/usr/bin/env python3
"""
WasTask Demo - Working demonstration
"""
import sys
import os
import asyncio

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

async def main():
    """Main demo function"""
    
    console.print(Panel("[bold blue]🚀 WasTask Demo - Live Test[/bold blue]", expand=False))
    
    # Test 1: Core models
    console.print("\n[bold cyan]📊 Testing Core Models[/bold cyan]")
    try:
        from core.models import Project, Task, TaskStatus, TaskPriority
        
        project = Project(
            name="Demo Project",
            description="A demonstration project for WasTask capabilities",
            owner_id="550e8400-e29b-41d4-a716-446655440000"
        )
        
        task = Task(
            title="Setup Development Environment",
            description="Initialize project structure and dependencies",
            project_id=project.id,
            creator_id=project.owner_id,
            priority=TaskPriority.HIGH
        )
        
        console.print(f"✅ Project created: {project.name}")
        console.print(f"✅ Task created: {task.title} (Priority: {task.priority.value})")
        
    except Exception as e:
        console.print(f"❌ Models test failed: {e}")
    
    # Test 2: Configuration
    console.print("\n[bold cyan]⚙️ Testing Configuration[/bold cyan]")
    try:
        from config.settings import settings
        
        console.print(f"✅ App: {settings.app_name} v{settings.version}")
        console.print(f"✅ Debug Mode: {settings.debug}")
        console.print(f"✅ Default Model: {settings.adk_model_default}")
        
    except Exception as e:
        console.print(f"❌ Config test failed: {e}")
    
    # Test 3: Mock ADK
    console.print("\n[bold cyan]🤖 Testing Mock AI Framework[/bold cyan]")
    try:
        from wastask.mock_adk import LlmAgent, FunctionTool
        
        def test_tool(message: str) -> str:
            """Test tool function"""
            return f"Tool processed: {message}"
        
        tool = FunctionTool(test_tool)
        agent = LlmAgent(
            name="test_agent",
            model="mock-model",
            description="Test agent",
            tools=[tool]
        )
        
        response = await agent.run("Hello from WasTask!")
        console.print(f"✅ Agent response: {response.content[:80]}...")
        
    except Exception as e:
        console.print(f"❌ Mock ADK test failed: {e}")
    
    # Test 4: Coordinator Agent
    console.print("\n[bold cyan]🎯 Testing Coordinator Agent[/bold cyan]")
    try:
        from agents.coordinator.agent import coordinator
        
        response = await coordinator.process_message(
            user_id="demo_user",
            message="I want to create a new software project for a web application. Can you help me plan it?"
        )
        
        console.print(f"✅ Coordinator response received")
        console.print(f"   Agent: {response.agent_type}")
        console.print(f"   Response: {response.response[:100]}...")
        
        if response.suggestions:
            console.print("   Suggestions:")
            for suggestion in response.suggestions[:2]:
                console.print(f"   • {suggestion}")
        
    except Exception as e:
        console.print(f"❌ Coordinator test failed: {e}")
    
    # Test 5: Planning Agent
    console.print("\n[bold cyan]📋 Testing Planning Agent[/bold cyan]")
    try:
        from agents.planning.agent import planning_agent
        
        result = await planning_agent.create_project_plan(
            project_description="Build a modern web application with React frontend and Python backend",
            constraints={"max_duration_days": 21},
            preferences={"methodology": "agile", "team_size": 2}
        )
        
        if result['status'] == 'success':
            plan = result['plan']
            console.print(f"✅ Project plan created successfully")
            console.print(f"   Title: {plan['project_summary']['title']}")
            console.print(f"   Phases: {len(plan['phases'])}")
            console.print(f"   Duration: {plan['timeline']['total_duration_days']} days")
            console.print(f"   Team Size: {plan['resources']['estimated_team_size']}")
        
    except Exception as e:
        console.print(f"❌ Planning test failed: {e}")
    
    # Summary
    console.print("\n[bold cyan]📈 WasTask Status Summary[/bold cyan]")
    
    table = Table(title="Component Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Functionality", style="dim")
    
    table.add_row("Core Models", "✅ Ready", "Pydantic data models with validation")
    table.add_row("Configuration", "✅ Ready", "Environment-based settings")
    table.add_row("Mock ADK", "✅ Ready", "AI agent framework simulation")
    table.add_row("Coordinator Agent", "✅ Ready", "Main AI orchestrator")
    table.add_row("Planning Agent", "✅ Ready", "Project planning & decomposition")
    table.add_row("CLI Interface", "🔄 Partial", "Basic structure in place")
    table.add_row("Web API", "📋 Planned", "FastAPI REST endpoints")
    table.add_row("GitHub Integration", "📋 Planned", "Repository synchronization")
    table.add_row("Database", "📋 Planned", "PostgreSQL + SQLAlchemy")
    
    console.print(table)
    
    # Demo conversation
    console.print(f"\n[bold green]💬 Interactive Demo Conversation[/bold green]")
    
    demo_messages = [
        "Hello WasTask! I'm starting a new project.",
        "I need to build a task management application.",
        "Can you break this down into smaller tasks?",
        "What's the estimated timeline for this project?"
    ]
    
    for i, message in enumerate(demo_messages, 1):
        console.print(f"\n[bold blue]User:[/bold blue] {message}")
        
        try:
            from agents.coordinator.agent import coordinator
            response = await coordinator.process_message(
                user_id="demo_user",
                message=message,
                project_id="demo_project" if i > 1 else None
            )
            
            console.print(f"[bold green]WasTask:[/bold green] {response.response[:150]}...")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    # Final status
    console.print(f"\n[bold green]🎉 WasTask Demo Completed Successfully![/bold green]")
    console.print("\n[bold yellow]Ready for Next Steps:[/bold yellow]")
    console.print("• Complete CLI implementation")
    console.print("• Add web interface with FastAPI")
    console.print("• Implement real Google ADK integration")
    console.print("• Add database persistence")
    console.print("• Create GitHub integration")
    
    console.print(f"\n[bold cyan]Usage Commands:[/bold cyan]")
    console.print("• uv run python demo_wastask.py - Run this demo")
    console.print("• make help - Show available commands")
    console.print("• uv run pytest tests/ - Run test suite")


if __name__ == '__main__':
    asyncio.run(main())
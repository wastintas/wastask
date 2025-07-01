#!/usr/bin/env python3
"""
WasTask Setup Script with UV
Ultra-fast setup using UV package manager
"""
import os
import shutil
import subprocess
import sys
import platform
from pathlib import Path


def print_banner():
    """Print setup banner"""
    print("🚀 WasTask Setup with UV")
    print("=" * 50)
    print("Ultra-fast Python package management")
    print()


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")


def install_uv():
    """Install UV if not already available"""
    if shutil.which('uv'):
        print("✅ UV is already installed")
        return True
    
    print("📦 Installing UV...")
    try:
        # Install UV using the official installer
        if platform.system() == "Windows":
            # Windows installation
            subprocess.run([
                "powershell", "-c", 
                "irm https://astral.sh/uv/install.ps1 | iex"
            ], check=True)
        else:
            # Unix-like systems (macOS, Linux)
            subprocess.run([
                "curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"
            ], shell=True, check=True)
        
        print("✅ UV installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install UV")
        print("Please install UV manually: https://github.com/astral-sh/uv")
        return False


def init_uv_project():
    """Initialize UV project"""
    try:
        print("🔧 Initializing UV project...")
        
        # Check if already initialized
        if Path("pyproject.toml").exists():
            print("✅ Project already has pyproject.toml")
        else:
            # Initialize UV project
            subprocess.run(["uv", "init", "--no-readme", "--name", "wastask"], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize UV project: {e}")
        return False


def install_dependencies():
    """Install dependencies using UV"""
    try:
        print("📦 Installing dependencies with UV...")
        
        # Install main dependencies
        main_deps = [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.23.0",
            "redis[hiredis]>=5.0.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "click>=8.0.0",
            "rich>=13.0.0",
            "structlog>=24.0.0",
            "python-jose[cryptography]>=3.3.0",
            "python-multipart>=0.0.6",
            "httpx>=0.24.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0",
            "asyncpg>=0.28.0",
            "python-dotenv>=1.0.0",
            "github3.py>=3.0.0",
            "litellm>=1.0.0"
        ]
        
        # Try to install google-adk, but don't fail if it's not available
        try:
            subprocess.run(["uv", "add", "google-adk>=1.0.0"], check=True)
            print("✅ Google ADK installed")
        except subprocess.CalledProcessError:
            print("⚠️  Google ADK not available, will use mock implementation")
            # Add a placeholder comment in requirements
            main_deps.append("# google-adk>=1.0.0  # Not available yet")
        
        # Install main dependencies in batches for better performance
        for dep in main_deps:
            if not dep.startswith("#"):
                try:
                    subprocess.run(["uv", "add", dep], check=True)
                except subprocess.CalledProcessError:
                    print(f"⚠️  Could not install {dep}")
        
        # Install dev dependencies
        dev_deps = [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "types-redis>=4.6.0"
        ]
        
        print("🛠️ Installing development dependencies...")
        for dep in dev_deps:
            try:
                subprocess.run(["uv", "add", "--dev", dep], check=True)
            except subprocess.CalledProcessError:
                print(f"⚠️  Could not install dev dependency {dep}")
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template"""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return
    
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env with your API keys and configuration")


def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data', 'uploads', 'backups', '.uv-cache']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Created necessary directories")


def create_makefile():
    """Create Makefile for common tasks"""
    makefile_content = '''# WasTask Makefile
.PHONY: help install dev test format lint type-check clean docker-build docker-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install: ## Install dependencies with UV
	uv sync

dev: ## Start development server
	uv run uvicorn wastask.api.main:app --reload --host 0.0.0.0 --port 8000

cli: ## Run CLI interface
	uv run python -m wastask.cli.main

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=wastask --cov-report=html

format: ## Format code
	uv run black wastask/ tests/
	uv run ruff check wastask/ tests/ --fix

lint: ## Lint code
	uv run ruff check wastask/ tests/

type-check: ## Type check with mypy
	uv run mypy wastask/

clean: ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .mypy_cache/ .coverage dist/ build/ 2>/dev/null || true

setup-pre-commit: ## Setup pre-commit hooks
	uv run pre-commit install

update: ## Update dependencies
	uv sync --upgrade

shell: ## Open UV shell
	uv shell

info: ## Show project info
	uv tree
	@echo ""
	@echo "Project structure:"
	@find wastask -name "*.py" 2>/dev/null | head -10 || echo "No Python files found yet"

# WasTask specific commands
create-project: ## Create new project interactively
	uv run python -m wastask.cli.main project create --interactive

chat: ## Chat with WasTask AI
	uv run python -m wastask.cli.main chat "Hello WasTask!"

analyze: ## Analyze project
	uv run python -m wastask.cli.main analyze

demo: ## Run a quick demo
	@echo "🚀 WasTask Demo"
	@echo "Testing CLI..."
	uv run python -m wastask.cli.main --help
'''
    
    Path("Makefile").write_text(makefile_content)
    print("✅ Created Makefile with common tasks")


def create_mock_adk():
    """Create a mock Google ADK implementation for testing"""
    mock_adk_dir = Path("wastask/mock_adk")
    mock_adk_dir.mkdir(exist_ok=True)
    
    # Create mock ADK files
    init_content = '''"""
Mock Google ADK implementation for development/testing
"""
__version__ = "1.0.0"

from .agent import Agent, LlmAgent, FunctionTool
from .session import Session

__all__ = ["Agent", "LlmAgent", "FunctionTool", "Session"]
'''
    
    agent_content = '''"""
Mock Agent implementation
"""
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class ToolResult:
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FunctionTool:
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or f"Tool: {func.__name__}"
    
    def execute(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Agent:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    async def run(self, message: str, **kwargs) -> ToolResult:
        # Mock implementation
        return ToolResult(content=f"Mock response for: {message}")


class LlmAgent(Agent):
    def __init__(
        self, 
        name: str, 
        model: str = "mock-model",
        description: str = "",
        instruction: str = "",
        tools: List[FunctionTool] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
        **kwargs
    ):
        super().__init__(name, description)
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    async def run(self, message: str, context: Dict[str, Any] = None, session: Any = None) -> ToolResult:
        # Mock intelligent response based on message content
        message_lower = message.lower()
        
        if "create" in message_lower and "project" in message_lower:
            return ToolResult(
                content="I can help you create a new project. Let me gather the requirements and create a structured plan.",
                metadata={"action": "create_project"}
            )
        elif "list" in message_lower and "project" in message_lower:
            return ToolResult(
                content="Here are your projects:\\n- Sample Project (active)\\n- Demo Project (planning)",
                metadata={"action": "list_projects"}
            )
        elif "task" in message_lower:
            return ToolResult(
                content="I can help you manage tasks. Would you like to create, update, or list tasks?",
                metadata={"action": "task_management"}
            )
        elif "analyze" in message_lower:
            return ToolResult(
                content="Project Analysis:\\n- Total tasks: 10\\n- Completed: 3 (30%)\\n- In progress: 4\\n- Pending: 3\\n\\nRecommendations:\\n- Focus on completing in-progress tasks\\n- Review pending task priorities",
                metadata={"action": "analyze"}
            )
        else:
            return ToolResult(
                content=f"I understand you want to know about: {message}\\n\\nAs your AI project management assistant, I can help with:\\n- Creating and managing projects\\n- Task planning and decomposition\\n- Progress analysis\\n- GitHub integration\\n\\nHow can I assist you today?",
                metadata={"action": "general_help"}
            )
'''
    
    session_content = '''"""
Mock Session implementation
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class Session:
    def __init__(self, user_id: str, project_id: Optional[str] = None, **kwargs):
        self.user_id = user_id
        self.project_id = project_id
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
'''
    
    (mock_adk_dir / "__init__.py").write_text(init_content)
    (mock_adk_dir / "agent.py").write_text(agent_content)
    (mock_adk_dir / "session.py").write_text(session_content)
    
    print("✅ Created mock Google ADK for development")


def update_imports_for_mock():
    """Update imports to use mock ADK if real one is not available"""
    coordinator_file = Path("wastask/agents/coordinator/agent.py")
    if coordinator_file.exists():
        content = coordinator_file.read_text()
        
        # Replace Google ADK import with conditional import
        new_import = '''try:
    from google.adk import Agent, LlmAgent, FunctionTool
    from google.adk.core.session import Session
except ImportError:
    # Use mock implementation for development
    from wastask.mock_adk import Agent, LlmAgent, FunctionTool
    from wastask.mock_adk.session import Session'''
        
        if "from google.adk import" in content:
            content = content.replace(
                "from google.adk import Agent, LlmAgent, FunctionTool\nfrom google.adk.core.session import Session",
                new_import
            )
            coordinator_file.write_text(content)
            print("✅ Updated coordinator agent imports")


def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 WasTask setup with UV completed!")
    print("\nQuick test:")
    print("  make help          # Show all commands")
    print("  make demo          # Run a quick demo")
    print("  make cli           # Try the CLI")
    print()
    print("Development:")
    print("  make dev           # Start development server")
    print("  make test          # Run tests")
    print("  make format        # Format code")
    print()
    print("Next steps:")
    print("  1. Edit .env with your API keys")
    print("  2. Run: make demo")
    print("  3. Try: make create-project")
    print()
    print("🚀 Happy coding with WasTask!")


def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    check_python_version()
    
    if not install_uv():
        sys.exit(1)
    
    # Setup steps
    create_env_file()
    create_directories()
    
    if init_uv_project():
        install_dependencies()
        create_makefile()
        create_mock_adk()
        update_imports_for_mock()
        print_next_steps()
    else:
        print("❌ Setup failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
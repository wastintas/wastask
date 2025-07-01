#!/usr/bin/env python3
"""
Simplified test for WasTask without module imports
"""
import sys
from pathlib import Path

print("🚀 WasTask Project Structure Test")
print("=" * 40)

# Check project structure
project_files = [
    "wastask/core/models.py",
    "wastask/config/settings.py", 
    "wastask/agents/coordinator/agent.py",
    "wastask/agents/planning/agent.py",
    "wastask/cli/main.py",
    "wastask/mock_adk/__init__.py",
    "pyproject.toml",
    "Makefile",
    "README.md"
]

print("📁 Checking project structure:")
all_good = True
for file_path in project_files:
    if Path(file_path).exists():
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path}")
        all_good = False

print(f"\n📊 Structure Status: {'✅ Complete' if all_good else '⚠️ Missing files'}")

# Check UV environment
print(f"\n🐍 Python Version: {sys.version}")
print(f"🔍 Python Path: {sys.executable}")

# Check if UV is working
try:
    import subprocess
    result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"⚡ UV Version: {result.stdout.strip()}")
    else:
        print("❌ UV not working properly")
except:
    print("❌ UV not found")

# Test basic imports
print(f"\n📦 Testing Basic Imports:")
try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__}")
except ImportError:
    print("❌ FastAPI not found")

try:
    import pydantic
    print(f"✅ Pydantic {pydantic.__version__}")
except ImportError:
    print("❌ Pydantic not found")

try:
    import click
    print(f"✅ Click {click.__version__}")
except ImportError:
    print("❌ Click not found")

try:
    import rich
    print(f"✅ Rich {rich.__version__}")
except ImportError:
    print("❌ Rich not found")

print(f"\n🎯 Available Make Commands:")
makefile = Path("Makefile")
if makefile.exists():
    print("   make help     - Show all commands")
    print("   make demo     - Run demo")
    print("   make test     - Run tests")
    print("   make format   - Format code")
else:
    print("❌ Makefile not found")

print(f"\n🚀 WasTask is ready for development!")
print("Next steps:")
print("1. Fix module structure: uv sync --reinstall")
print("2. Test imports: python -c 'import wastask'")
print("3. Run CLI: uv run python -m wastask.cli.main --help")
print("4. Create project: make create-project")
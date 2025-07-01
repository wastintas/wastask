#!/usr/bin/env python3
"""
WasTask Setup Script
Helps initialize the WasTask environment
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")


def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = ['redis-server', 'git']
    missing = []
    
    for dep in dependencies:
        if not shutil.which(dep):
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing system dependencies: {', '.join(missing)}")
        print("Please install them and run setup again")
        return False
    
    print("✅ System dependencies are available")
    return True


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


def install_python_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False


def initialize_git():
    """Initialize git repository if not already done"""
    if Path('.git').exists():
        print("✅ Git repository already initialized")
        return
    
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial WasTask setup'], check=True)
        print("✅ Git repository initialized")
    except subprocess.CalledProcessError:
        print("⚠️  Could not initialize git repository")


def setup_pre_commit():
    """Set up pre-commit hooks"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pre-commit'], check=True)
        subprocess.run(['pre-commit', 'install'], check=True)
        print("✅ Pre-commit hooks installed")
    except subprocess.CalledProcessError:
        print("⚠️  Could not set up pre-commit hooks")


def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data', 'uploads', 'backups']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Created necessary directories")


def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 WasTask setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys and configuration")
    print("2. Start Redis: redis-server")
    print("3. Set up your database (PostgreSQL)")
    print("4. Test the CLI: python -m wastask.cli.main --help")
    print("5. Create your first project: python -m wastask.cli.main project create --interactive")
    print("\nFor more information, see README.md")


def main():
    """Main setup function"""
    print("🚀 Setting up WasTask...")
    print("=" * 50)
    
    # Check requirements
    check_python_version()
    if not check_dependencies():
        sys.exit(1)
    
    # Setup steps
    create_env_file()
    create_directories()
    
    if install_python_dependencies():
        setup_pre_commit()
        initialize_git()
        print_next_steps()
    else:
        print("❌ Setup failed at dependency installation")
        sys.exit(1)


if __name__ == '__main__':
    main()
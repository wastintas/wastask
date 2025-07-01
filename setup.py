#!/usr/bin/env python3
"""
WasTask Setup - Unified setup script
Consolidates all setup functionality for WasTask
"""
import asyncio
import sys
import os
from pathlib import Path
import subprocess

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Check if uv is available
    try:
        subprocess.run(['uv', '--version'], check=True, capture_output=True)
        print("✅ Using uv for faster installation")
        subprocess.run(['uv', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️ uv not found, using pip")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    
    print("✅ Dependencies installed")

def setup_database():
    """Setup database schema"""
    print("🗄️ Setting up database...")
    
    async def create_db():
        try:
            from database_manager import connect_and_run
            
            async def setup_schema(db):
                await db.create_schema()
                return await db.get_project_stats()
            
            stats = await connect_and_run(setup_schema)
            print(f"✅ Database ready - {stats}")
            
        except ImportError:
            print("⚠️ Database modules not available")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
    
    asyncio.run(create_db())

def create_config():
    """Create configuration files"""
    print("⚙️ Creating configuration...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Basic settings
    if not (config_dir / "settings.py").exists():
        settings_content = '''"""
WasTask Settings
"""
import os

# Model settings
adk_model_default = "claude-3-5-sonnet-20241022"
adk_model_complex = "claude-3-5-sonnet-20241022"  
adk_model_simple = "claude-3-5-haiku-20241022"

# Features
cost_optimization_enabled = True
semantic_cache_enabled = True
max_daily_cost_usd = 10.0

# Version
version = "1.0.0"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///wastask.db")
'''
        (config_dir / "settings.py").write_text(settings_content)
        print("✅ Settings created")

def main():
    """Main setup function"""
    print("🚀 WasTask Setup")
    print("=" * 40)
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            sys.exit(1)
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Install dependencies
        install_dependencies()
        
        # Create config
        create_config()
        
        # Setup database
        setup_database()
        
        print("\n" + "=" * 40)
        print("✅ WasTask setup complete!")
        print("\nNext steps:")
        print("  python wastask.py prd analyze <your_prd.md>")
        print("  python wastask.py db list")
        print("  python wastask.py --help")
        
        # Make CLI executable
        cli_path = Path("wastask.py")
        if cli_path.exists():
            os.chmod(cli_path, 0o755)
            print(f"✅ {cli_path} is now executable")
        
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
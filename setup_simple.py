#!/usr/bin/env python3
"""
Simple WasTask Setup Script with UV
"""
import subprocess
import sys
from pathlib import Path


def main():
    print("🚀 Simple WasTask Setup with UV")
    print("=" * 40)
    
    # Initialize project without building
    try:
        print("📦 Installing dependencies directly...")
        
        # Install dependencies one by one without building the local package
        deps = [
            "fastapi",
            "uvicorn[standard]",
            "pydantic",
            "pydantic-settings", 
            "click",
            "rich",
            "httpx",
            "python-dotenv"
        ]
        
        for dep in deps:
            try:
                subprocess.run(["uv", "add", dep], check=True, capture_output=True)
                print(f"✅ {dep}")
            except subprocess.CalledProcessError:
                print(f"⚠️  {dep} - failed")
        
        # Install dev dependencies
        dev_deps = ["pytest", "black", "ruff"]
        for dep in dev_deps:
            try:
                subprocess.run(["uv", "add", "--dev", dep], check=True, capture_output=True)
                print(f"✅ {dep} (dev)")
            except subprocess.CalledProcessError:
                print(f"⚠️  {dep} (dev) - failed")
                
        print("\n✅ Basic dependencies installed!")
        print("\nTry these commands:")
        print("  uv run python -m wastask.cli.main --help")
        print("  make help")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
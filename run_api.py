#!/usr/bin/env python3
"""
Run the WasTask API server
"""
import uvicorn
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Set default environment variables if not set
    os.environ.setdefault("WASTASK_SECRET_KEY", "dev-secret-key-change-in-production")
    os.environ.setdefault("WASTASK_DATABASE_URL", "postgresql://wastask:password@localhost:5433/wastask")
    os.environ.setdefault("WASTASK_DEBUG", "true")
    
    # Run the server
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
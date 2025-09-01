#!/usr/bin/env python
"""
Standalone API runner - starts the OpenCanvas API server directly

This script allows you to run the API server without using the opencanvas CLI.
It properly sets up the Python path and starts the FastAPI server.

Usage:
    python api/run_api.py
    or
    chmod +x api/run_api.py && ./api/run_api.py
"""
import sys
import os
from pathlib import Path

def main():
    """Start the API server"""
    # Add parent src directory to path so we can import opencanvas
    src_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(src_dir))
    
    print("🚀 Starting OpenCanvas API Server (Standalone)")
    print(f"📁 Source directory: {src_dir}")
    print("📍 Host: 0.0.0.0")
    print("🔌 Port: 8000")
    print("🔄 Reload: True")
    print("📚 API Docs: http://0.0.0.0:8000/docs")
    print("🔍 ReDoc: http://0.0.0.0:8000/redoc")
    print("❤️  Health: http://0.0.0.0:8000/api/v1/health")
    print("--" * 25)
    
    try:
        import uvicorn
        
        # Run the API directly
        uvicorn.run(
            "api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except ImportError:
        print("❌ FastAPI dependencies not installed.")
        print("Please install with: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
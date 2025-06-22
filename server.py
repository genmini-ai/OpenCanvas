#!/usr/bin/env python3
"""
OpenCanvas API Server

Standalone server script for running the OpenCanvas API.
This provides a RESTful interface to all OpenCanvas functionality.
"""

import uvicorn
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api.app import app
from opencanvas.config import Config


def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(
        description="OpenCanvas API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python server.py
  
  # Run on specific host and port
  python server.py --host 0.0.0.0 --port 8080
  
  # Run in development mode with auto-reload
  python server.py --reload --log-level debug
  
  # Run in production mode
  python server.py --host 0.0.0.0 --port 80 --workers 4
        """
    )
    
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
        print("✅ Configuration validated successfully")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)
    
    # Print startup information
    print(f"🚀 Starting OpenCanvas API Server")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Reload: {args.reload}")
    print(f"📝 Log Level: {args.log_level}")
    print(f"👥 Workers: {args.workers}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔍 ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"❤️  Health: http://{args.host}:{args.port}/api/v1/health")
    print("-" * 50)
    
    # Start server
    uvicorn.run(
        "src.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        workers=args.workers if args.workers > 1 else None,
        access_log=True
    )


if __name__ == "__main__":
    main() 
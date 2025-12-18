#!/usr/bin/env python3
"""
Test server startup script
"""

import asyncio
import sys
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent))

from main import app
import uvicorn


def run_server():
    """Run test server"""
    print("Starting test server...")
    print("Application available at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run_server()
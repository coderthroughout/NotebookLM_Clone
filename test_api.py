#!/usr/bin/env python3
"""
Simple API test script to debug startup issues.
"""

import sys
sys.path.append('.')

try:
    print("🔧 Testing imports...")
    from research.frontend_api import app
    print("✅ Imports successful")
    
    print("🚀 Starting API...")
    import uvicorn
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        reload=False
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

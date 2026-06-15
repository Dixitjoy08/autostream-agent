"""
run.py — Start the AutoStream FastAPI server.
Usage:  python run.py
Then open:  http://localhost:8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,         # Auto-reload on code changes during dev
        log_level="info",
    )

"""
run.py — Start the AutoStream FastAPI server.
Usage:  python run.py
Then open:  http://localhost:8000

On Render.com, the PORT env variable is automatically set.
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,        # Disable reload in production
        log_level="info",
    )

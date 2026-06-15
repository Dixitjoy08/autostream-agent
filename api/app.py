"""
FastAPI backend for AutoStream AI Agent
Exposes a /chat endpoint that the web UI communicates with.
Each browser session maintains its own AgentState.
"""

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.agent import run_agent, AgentState


# ── In-memory session store ───────────────────────────────────────────────────
# Maps session_id (str) → AgentState
# In production, swap this for Redis.
sessions: dict[str, AgentState] = {}


# ── App setup ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AutoStream API starting up…")
    yield
    print("🛑 AutoStream API shutting down.")


app = FastAPI(
    title="AutoStream AI Agent API",
    description="Powers the AutoStream conversational sales agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the frontend (same origin or localhost) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the static frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ── Request / Response schemas ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str | None = None   # None → new session
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    lead_captured: bool
    user_name: str | None
    user_email: str | None
    user_platform: str | None
    user_plan: str | None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_ui():
    """Serve the chat frontend."""
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health():
    """Simple health-check for Render / monitoring."""
    return {"status": "ok", "active_sessions": len(sessions)}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Process one chat turn.
    - Creates a new session if session_id is absent or unknown.
    - Runs the agent and returns the AI response + current lead state.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Get or create session
    session_id = req.session_id if req.session_id else str(uuid.uuid4())
    state = sessions.get(session_id, AgentState())

    # Run one agent turn
    state, response = run_agent(req.message, state)

    # Persist updated state
    sessions[session_id] = state

    return ChatResponse(
        session_id=session_id,
        response=response,
        lead_captured=state.lead_captured,
        user_name=state.user_name,
        user_email=state.user_email,
        user_platform=state.user_platform,
        user_plan=state.user_plan,
    )


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session (e.g., when user clicks 'New Chat')."""
    sessions.pop(session_id, None)
    return {"status": "cleared"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import websocket, dashboard

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-Time Multimodal 3D AI Assistant Backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(dashboard.router, tags=["dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.post("/api/ingest")
async def ingest_documents():
    """Triggers the backend to scan the /documents folder and index any new files."""
    try:
        from app.agents.rag import knowledge_base
        import asyncio
        # Run ingestion in a thread so it doesn't block the async event loop
        await asyncio.to_thread(knowledge_base.ingest_documents)
        return {"status": "success", "message": "Documents ingested successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

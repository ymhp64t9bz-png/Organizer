"""
ORBIT - GPS Financeiro Brasileiro
Backend Principal FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api import chat, transactions, dashboard, voice, ocr
from app.core.config import settings
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: startup e shutdown"""
    # Startup: criar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("🚀 ORBIT Backend iniciado!")
    yield
    # Shutdown
    print("👋 ORBIT Backend encerrado.")

app = FastAPI(
    title="ORBIT API",
    description="GPS Financeiro Brasileiro - Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS para o frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://orbit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transações"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voz"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])

@app.get("/")
async def root():
    return {
        "message": "🛸 ORBIT API - GPS Financeiro",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orbit-backend"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

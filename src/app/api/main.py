from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.routers.ask import router as ask_router
from src.app.api.routers.ingest import router as ingest_router

app = FastAPI(
    title="Finance Multi-Agent API",
    description="Pipeline Multi-Agentes para RAG Financeiro",
    version="1.0.0"
)

# CORS (opcional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas principais
app.include_router(ask_router)
app.include_router(ingest_router)

"""
--------------------------------------------------------------------
|   AquaIntelli - God's Eye View of Earth's Water                  |
|   Satellite-Based Water Intelligence Platform                    |
|   FastAPI Application Entry Point                                |
--------------------------------------------------------------------

Features:
- 3 Databases: SQL (SQLAlchemy), NoSQL (MongoDB), Graph (Neo4j)
- OpenAPI/Swagger documentation at /docs
- GenAI: LangChain RAG, LangGraph Agent, Graph RAG, MCP, LangSmith
- 9 API route groups with 30+ endpoints
"""
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import get_settings
from .database import init_sql_db, init_nosql_db, init_graph_db
from .genai import rag_pipeline, graph_rag, init_langsmith

from .api.routes import (
    groundwater_routes, borewell_routes, irrigation_routes,
    satellite_routes, exchange_routes, farm_routes,
    genai_routes, alert_routes, db_routes, reservoir_routes, search_routes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

# ── Resolve frontend path ──
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    print("\n" + "="*62)
    print("   AquaIntelli - Initializing God's Eye View")
    print("="*62)

    # 1. SQL Database
    await init_sql_db()

    # 2. NoSQL Database
    await init_nosql_db()

    # 3. Graph Database
    await init_graph_db()

    # 4. LangSmith tracing
    init_langsmith()

    # 5. RAG Pipeline
    rag_pipeline.initialize()

    # 6. Graph RAG
    graph_rag.initialize()

    print("="*62)
    print("   All systems operational")
    print(f"   API Docs: http://localhost:{settings.PORT}/docs")
    print(f"   Frontend: http://localhost:{settings.PORT}")
    print("="*62 + "\n")

    yield

    # Shutdown
    logger.info("AquaIntelli shutting down...")


# ── FastAPI Application ──
app = FastAPI(
    title="AquaIntelli API",
    description="""
# 🌊 AquaIntelli - Satellite-Based Water Intelligence Platform

**God's Eye View of Earth's Water**

## Features
- **GRACE-FO Satellite Data** - Groundwater anomaly detection
- **AI Forecasting** - 90-day groundwater depletion prediction
- **Borewell Prediction** - Drilling success probability
- **Irrigation Optimization** - FAO-56 Penman-Monteith
- **Water Futures Exchange** - AI-priced water trading
- **Smart Farm** - IoT sensor monitoring
- **GenAI** - RAG, LangGraph Agent, Graph RAG, MCP tools

## Databases
- **SQL** (SQLAlchemy + SQLite/PostgreSQL) - Structured readings & predictions
- **NoSQL** (MongoDB) - Satellite data cache & documents
- **Neo4j** (Graph) - Water network relationships

## GenAI Stack
- **LangChain** - RAG pipeline with FAISS vectorstore
- **LangGraph** - Multi-step agent workflows
- **LangSmith** - Tracing and monitoring
- **MCP** - Model Context Protocol tool server
- **Graph RAG** - Neo4j + RAG fusion
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={"name": "AquaIntelli Team", "url": "https://aquaintelli.antigravity.app"},
    license_info={"name": "MIT License"},
    openapi_tags=[
        {"name": "Groundwater", "description": "GRACE-FO groundwater analysis & forecasting"},
        {"name": "Borewell", "description": "AI borewell drilling success prediction"},
        {"name": "Irrigation", "description": "FAO-56 crop water optimization"},
        {"name": "Satellite", "description": "Satellite data retrieval (GRACE, Sentinel, NASA POWER)"},
        {"name": "Water Exchange", "description": "Water Futures trading exchange"},
        {"name": "Smart Farm", "description": "IoT farm monitoring & scheduling"},
        {"name": "GenAI", "description": "RAG, LangGraph Agent, Graph RAG, MCP tools"},
        {"name": "Alerts", "description": "Water crisis alerts & events"},
        {"name": "Database", "description": "Multi-database health & info"},
    ],
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ──
PREFIX = "/api/v1"
app.include_router(groundwater_routes.router, prefix=PREFIX)
app.include_router(borewell_routes.router, prefix=PREFIX)
app.include_router(irrigation_routes.router, prefix=PREFIX)
app.include_router(satellite_routes.router, prefix=PREFIX)
app.include_router(exchange_routes.router, prefix=PREFIX)
app.include_router(farm_routes.router, prefix=PREFIX)
app.include_router(genai_routes.router, prefix=PREFIX)
app.include_router(alert_routes.router, prefix=PREFIX)
app.include_router(db_routes.router, prefix=PREFIX)
app.include_router(reservoir_routes.router, prefix=PREFIX)
app.include_router(search_routes.router, prefix=PREFIX)


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "service": "aquaintelli-backend",
        "version": settings.APP_VERSION,
        "databases": {"sql": "connected", "nosql": "connected", "graph": "connected"},
    }


# ── Serve Frontend Static Files ──
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

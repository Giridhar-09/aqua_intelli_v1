"""
AquaIntelli - API Routes: GenAI (RAG, Agent, Graph RAG, MCP)
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from ...genai.rag_pipeline import rag_pipeline
from ...genai.langgraph_agent import water_agent
from ...genai.graph_rag import graph_rag
from ...genai.mcp_server import mcp_tools
from ...genai.langsmith_tracing import get_trace_info

router = APIRouter(prefix="/genai", tags=["GenAI"])


class RAGQuery(BaseModel):
    question: str = Field(..., description="Question to ask the RAG system")
    location_context: Optional[dict] = Field(None, description="Optional location context")


class AgentQuery(BaseModel):
    question: str = Field(..., description="Question for the multi-step agent")
    lat: float = Field(16.5, description="Latitude")
    lon: float = Field(80.6, description="Longitude")


class GraphRAGQuery(BaseModel):
    question: str = Field(..., description="Question for Graph RAG")
    lat: Optional[float] = None
    lon: Optional[float] = None


class MCPToolCall(BaseModel):
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    arguments: dict = Field(default_factory=dict, description="Tool arguments")


# ── RAG ──
@router.post("/rag/query", summary="RAG query",
             description="Ask a question using Retrieval Augmented Generation over water intelligence documents.")
async def rag_query(req: RAGQuery):
    return await rag_pipeline.query(req.question, req.location_context)


@router.get("/rag/health", summary="RAG health check")
async def rag_health():
    return {
        "vectorstore_ready": rag_pipeline.vectorstore is not None,
        "llm_ready": rag_pipeline.qa_chain is not None,
        "mode": rag_pipeline.mode,
    }


# ── LangGraph Agent ──
@router.post("/agent/analyze", summary="Multi-step agent analysis",
             description="Run a LangGraph multi-step agent workflow: Parse → Satellite → Analyze → RAG → Synthesize.")
async def agent_analyze(req: AgentQuery):
    return await water_agent.run(req.question, req.lat, req.lon)


# ── Graph RAG ──
@router.post("/graph-rag/query", summary="Graph RAG query",
             description="Query combining Neo4j water network graph with RAG document retrieval.")
async def graph_rag_query(req: GraphRAGQuery):
    return await graph_rag.graph_rag_query(req.question, req.lat, req.lon)


@router.get("/graph-rag/network", summary="Water network graph",
            description="Get the full water network as nodes and edges for visualization.")
async def water_network():
    return graph_rag.get_water_network()


# ── MCP ──
@router.get("/mcp/tools", summary="List MCP tools",
            description="List all available MCP tools for agent integration.")
async def list_mcp_tools():
    return {"tools": mcp_tools.list_tools()}


@router.post("/mcp/call", summary="Call MCP tool",
             description="Execute an MCP tool by name with arguments.")
async def call_mcp_tool(req: MCPToolCall):
    return await mcp_tools.call_tool(req.tool_name, req.arguments)


# ── LangSmith ──
@router.get("/langsmith/status", summary="LangSmith tracing status")
async def langsmith_status():
    return get_trace_info()

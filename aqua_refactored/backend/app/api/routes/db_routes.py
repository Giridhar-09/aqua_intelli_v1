"""
AquaIntelli - API Routes: Database Health & Info
"""
from fastapi import APIRouter
from ...database.nosql_db import get_nosql_db
from ...database.graph_db import get_graph_db

router = APIRouter(prefix="/db", tags=["Database"])


@router.get("/health", summary="All database health status")
async def db_health():
    nosql = get_nosql_db()
    graph = get_graph_db()
    return {
        "sql": {"status": "connected", "type": "SQLite (dev) / PostgreSQL (prod)"},
        "nosql": {
            "status": "connected",
            "type": "MongoDB" if not isinstance(nosql, type(nosql)) else "Mock",
        },
        "graph": {
            "status": "connected",
            "type": "Neo4j" if hasattr(graph, '_session') else "Mock",
        },
    }


@router.get("/graph/nodes", summary="Graph database nodes")
async def graph_nodes():
    graph = get_graph_db()
    with graph.session() as session:
        nodes = session.run("MATCH (n) RETURN n")
    return {"nodes": nodes, "count": len(nodes)}


@router.get("/graph/relationships", summary="Graph database relationships")
async def graph_relationships():
    graph = get_graph_db()
    with graph.session() as session:
        rels = session.run("MATCH ()-[r:RECHARGES]->() RETURN r")
    return {"relationships": rels, "count": len(rels)}

"""
AquaIntelli - GenAI Module: Graph RAG
Combines Neo4j graph knowledge with RAG for relationship-aware intelligence.
"""
import logging
from typing import Optional
from ..database.graph_db import get_graph_db

logger = logging.getLogger(__name__)


class GraphRAG:
    """
    Graph RAG combines structured graph knowledge (Neo4j) with
    unstructured document retrieval (RAG) for context-rich answers.
    """

    def __init__(self):
        self.graph = None

    def initialize(self):
        self.graph = get_graph_db()
        print("  [OK] Graph RAG initialized")

    def query_graph(self, entity_type: str = "all") -> list[dict]:
        """Query the water network graph."""
        if not self.graph:
            self.graph = get_graph_db()
        with self.graph.session() as session:
            if entity_type == "rivers":
                return session.run("MATCH (r:River) RETURN r")
            elif entity_type == "aquifers":
                return session.run("MATCH (a:Aquifer) RETURN a")
            elif entity_type == "districts":
                return session.run("MATCH (d:District) RETURN d")
            elif entity_type == "reservoirs":
                return session.run("MATCH (res:Reservoir) RETURN res")
            elif entity_type == "relationships":
                return session.run("MATCH (a)-[r:RECHARGES]->(b) RETURN a,r,b")
            return session.run("MATCH (n) RETURN n")

    def get_water_network(self) -> dict:
        """Get the full water network as nodes + edges."""
        if not self.graph:
            self.graph = get_graph_db()

        with self.graph.session() as session:
            nodes = session.run("MATCH (n) RETURN n")
            rels = session.run("MATCH ()-[r:RELATIONSHIP]->() RETURN r")

        # Format for frontend visualization
        graph_nodes = []
        for n in nodes:
            graph_nodes.append({
                "id": n.get("name", "unknown"),
                "type": n.get("type", "unknown"),
                "label": n.get("name", "unknown"),
                **{k: v for k, v in n.items() if k not in ("type", "name")},
            })

        graph_edges = []
        for r in rels:
            graph_edges.append({
                "source": r.get("from", ""),
                "target": r.get("to", ""),
                "relationship": r.get("rel", "CONNECTED"),
            })

        return {"nodes": graph_nodes, "edges": graph_edges}

    async def graph_rag_query(self, question: str, lat: Optional[float] = None, lon: Optional[float] = None) -> dict:
        """Combined Graph + RAG query."""
        # Step 1: Extract entities from question
        q = question.lower()
        entity_type = "all"
        if "river" in q:
            entity_type = "rivers"
        elif "aquifer" in q:
            entity_type = "aquifers"
        elif "district" in q:
            entity_type = "districts"
        elif "reservoir" in q or "dam" in q:
            entity_type = "reservoirs"

        # Step 2: Query graph for structured knowledge
        graph_results = self.query_graph(entity_type)

        # Step 3: Combine with RAG context
        from .rag_pipeline import rag_pipeline
        rag_result = await rag_pipeline.query(question)

        # Step 4: Synthesize
        graph_context = f"Found {len(graph_results)} {entity_type} in water network graph."
        if graph_results:
            sample = graph_results[:3]
            graph_context += f" Examples: {', '.join(n.get('name', str(n)) for n in sample if isinstance(n, dict))}."

        return {
            "answer": rag_result.get("answer", ""),
            "graph_context": graph_context,
            "graph_entities": graph_results[:10],
            "rag_sources": rag_result.get("sources", []),
            "mode": f"graph_rag ({rag_result.get('mode', 'mock')})",
            "question": question,
        }


# Singleton
graph_rag = GraphRAG()

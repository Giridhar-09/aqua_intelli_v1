"""
AquaIntelli - Neo4j Graph Database
Models water network relationships: rivers → reservoirs → aquifers → districts.
Used for Graph RAG and relationship queries.
"""
import logging
from typing import Optional
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_neo4j_driver = None


class MockNeo4jSession:
    """In-memory mock for Neo4j graph queries."""
    def __init__(self):
        self._nodes: list[dict] = []
        self._relationships: list[dict] = []
        self._seed_data()

    def _seed_data(self):
        """Seed the graph with India water network data."""
        # Rivers
        rivers = [
            {"type": "River", "name": "Krishna", "length_km": 1400, "basin_km2": 258948, "lat": 16.51, "lon": 80.62},
            {"type": "River", "name": "Godavari", "length_km": 1465, "basin_km2": 314000, "lat": 17.00, "lon": 81.78},
            {"type": "River", "name": "Cauvery", "length_km": 800, "basin_km2": 81155, "lat": 12.43, "lon": 76.57},
            {"type": "River", "name": "Narmada", "length_km": 1312, "basin_km2": 98796, "lat": 21.83, "lon": 73.75},
            {"type": "River", "name": "Ganga", "length_km": 2525, "basin_km2": 907000, "lat": 25.43, "lon": 81.85},
        ]
        # Aquifers
        aquifers = [
            {"type": "Aquifer", "name": "Krishna Basin Aquifer", "aquifer_type": "fractured_granite", "status": "over-exploited", "lat": 16.5, "lon": 80.6},
            {"type": "Aquifer", "name": "Indo-Gangetic Alluvial", "aquifer_type": "alluvial_gravel", "status": "critical", "lat": 28.0, "lon": 79.0},
            {"type": "Aquifer", "name": "Rajasthan Desert Aquifer", "aquifer_type": "sandstone", "status": "over-exploited", "lat": 26.9, "lon": 70.9},
            {"type": "Aquifer", "name": "Gujarat Basalt Aquifer", "aquifer_type": "basalt_vesicular", "status": "recovering", "lat": 23.0, "lon": 72.5},
            {"type": "Aquifer", "name": "Cauvery Delta Aquifer", "aquifer_type": "alluvial_gravel", "status": "safe", "lat": 11.0, "lon": 79.5},
        ]
        # Districts
        districts = [
            {"type": "District", "name": "Krishna", "state": "Andhra Pradesh", "population": 4530000, "borewell_success_pct": 68},
            {"type": "District", "name": "Jodhpur", "state": "Rajasthan", "population": 3690000, "borewell_success_pct": 22},
            {"type": "District", "name": "Ludhiana", "state": "Punjab", "population": 3490000, "borewell_success_pct": 70},
            {"type": "District", "name": "Ahmedabad", "state": "Gujarat", "population": 5570000, "borewell_success_pct": 60},
            {"type": "District", "name": "Chennai", "state": "Tamil Nadu", "population": 4680000, "borewell_success_pct": 38},
        ]
        # Reservoirs
        reservoirs = [
            {"type": "Reservoir", "name": "Nagarjuna Sagar", "capacity_mcm": 11472, "river": "Krishna", "lat": 16.57, "lon": 79.31},
            {"type": "Reservoir", "name": "Sardar Sarovar", "capacity_mcm": 9460, "river": "Narmada", "lat": 21.83, "lon": 73.75},
            {"type": "Reservoir", "name": "Mettur", "capacity_mcm": 2646, "river": "Cauvery", "lat": 11.79, "lon": 77.81},
        ]
        self._nodes = rivers + aquifers + districts + reservoirs
        # Relationships
        self._relationships = [
            {"from": "Krishna", "to": "Krishna Basin Aquifer", "rel": "RECHARGES"},
            {"from": "Krishna", "to": "Nagarjuna Sagar", "rel": "FEEDS"},
            {"from": "Krishna Basin Aquifer", "to": "Krishna", "rel": "UNDERLIES"},
            {"from": "Godavari", "to": "Indo-Gangetic Alluvial", "rel": "RECHARGES"},
            {"from": "Cauvery", "to": "Cauvery Delta Aquifer", "rel": "RECHARGES"},
            {"from": "Cauvery", "to": "Mettur", "rel": "FEEDS"},
            {"from": "Narmada", "to": "Gujarat Basalt Aquifer", "rel": "RECHARGES"},
            {"from": "Narmada", "to": "Sardar Sarovar", "rel": "FEEDS"},
            {"from": "Krishna", "to": "Krishna", "rel": "FLOWS_THROUGH", "district": True},
            {"from": "Rajasthan Desert Aquifer", "to": "Jodhpur", "rel": "SERVES"},
            {"from": "Indo-Gangetic Alluvial", "to": "Ludhiana", "rel": "SERVES"},
            {"from": "Gujarat Basalt Aquifer", "to": "Ahmedabad", "rel": "SERVES"},
            {"from": "Cauvery Delta Aquifer", "to": "Chennai", "rel": "SERVES"},
        ]

    def run(self, query: str, **params):
        """Execute a mock Cypher query."""
        return self._mock_query(query, params)

    def _mock_query(self, query: str, params: dict):
        q = query.upper()
        if "MATCH" in q and "RIVER" in q:
            return [n for n in self._nodes if n["type"] == "River"]
        elif "MATCH" in q and "AQUIFER" in q:
            return [n for n in self._nodes if n["type"] == "Aquifer"]
        elif "MATCH" in q and "DISTRICT" in q:
            return [n for n in self._nodes if n["type"] == "District"]
        elif "MATCH" in q and "RESERVOIR" in q:
            return [n for n in self._nodes if n["type"] == "Reservoir"]
        elif "RECHARGES" in q or "RELATIONSHIP" in q:
            return self._relationships
        return self._nodes


class MockNeo4jDriver:
    """Mock Neo4j driver for development."""
    def __init__(self):
        self._session = MockNeo4jSession()

    def session(self, **kwargs):
        return MockNeo4jContextManager(self._session)

    def close(self):
        pass


class MockNeo4jContextManager:
    def __init__(self, session):
        self._session = session
    def __enter__(self):
        return self._session
    def __exit__(self, *args):
        pass


async def init_graph_db():
    """Initialize Neo4j connection or mock."""
    global _neo4j_driver
    if settings.NEO4J_MOCK:
        _neo4j_driver = MockNeo4jDriver()
        print("  [OK] Graph Database initialized (mock mode)")
        return _neo4j_driver
    try:
        from neo4j import GraphDatabase
        _neo4j_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        _neo4j_driver.verify_connectivity()
        # Create constraints and indexes
        with _neo4j_driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:River) REQUIRE r.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Aquifer) REQUIRE a.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:District) REQUIRE d.name IS UNIQUE")
        print("  [OK] Graph Database initialized (Neo4j)")
    except Exception as e:
        logger.warning(f"Neo4j connection failed: {e} - using mock")
        _neo4j_driver = MockNeo4jDriver()
        print("  [OK] Graph Database initialized (mock fallback)")
    return _neo4j_driver


def get_graph_db():
    """Get the Neo4j driver instance."""
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = MockNeo4jDriver()
    return _neo4j_driver

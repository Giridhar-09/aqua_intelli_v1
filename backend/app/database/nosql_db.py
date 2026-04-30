"""
AquaIntelli - NoSQL Database (MongoDB)
Document store for satellite data, sensor streams, RAG documents.
Uses mongomock for development without MongoDB installed.
"""
import logging
from typing import Optional
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_mongo_client = None
_mongo_db = None


class MockMongoCollection:
    """In-memory mock for MongoDB collections when MongoDB is unavailable."""
    def __init__(self, name: str):
        self.name = name
        self._docs: list[dict] = []
        self._counter = 0

    async def insert_one(self, doc: dict):
        self._counter += 1
        doc["_id"] = str(self._counter)
        self._docs.append(doc.copy())
        return type("Result", (), {"inserted_id": doc["_id"]})()

    async def insert_many(self, docs: list[dict]):
        ids = []
        for doc in docs:
            result = await self.insert_one(doc)
            ids.append(result.inserted_id)
        return type("Result", (), {"inserted_ids": ids})()

    async def find_one(self, query: dict = None):
        if not query:
            return self._docs[0] if self._docs else None
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    async def find(self, query: dict = None, limit: int = 100):
        results = self._docs
        if query:
            results = [d for d in results if all(d.get(k) == v for k, v in query.items())]
        return results[:limit]

    async def count_documents(self, query: dict = None):
        if not query:
            return len(self._docs)
        return len([d for d in self._docs if all(d.get(k) == v for k, v in query.items())])

    async def update_one(self, query: dict, update: dict):
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                return type("Result", (), {"modified_count": 1})()
        return type("Result", (), {"modified_count": 0})()

    async def delete_one(self, query: dict):
        for i, doc in enumerate(self._docs):
            if all(doc.get(k) == v for k, v in query.items()):
                self._docs.pop(i)
                return type("Result", (), {"deleted_count": 1})()
        return type("Result", (), {"deleted_count": 0})()

    async def create_index(self, keys, **kwargs):
        pass  # No-op for mock


class MockMongoDB:
    """In-memory mock MongoDB database."""
    def __init__(self):
        self._collections: dict[str, MockMongoCollection] = {}

    def __getattr__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        if name not in self._collections:
            self._collections[name] = MockMongoCollection(name)
        return self._collections[name]

    def __getitem__(self, name):
        return getattr(self, name)


async def init_nosql_db():
    """Initialize MongoDB connection or mock."""
    global _mongo_client, _mongo_db
    if settings.MONGO_MOCK:
        _mongo_db = MockMongoDB()
        logger.info("  [OK] NoSQL Database initialized (mock mode)")
        print("  [OK] NoSQL Database initialized (mock mode)")
        return _mongo_db
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        _mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
        _mongo_db = _mongo_client[settings.MONGO_DB_NAME]
        # Create indexes
        await _mongo_db.satellite_data.create_index([("lat", 1), ("lon", 1)])
        await _mongo_db.sensor_readings.create_index([("timestamp", -1)])
        await _mongo_db.rag_documents.create_index([("source", 1)])
        logger.info("  [OK] NoSQL Database initialized (MongoDB)")
        print("  [OK] NoSQL Database initialized (MongoDB)")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e} - using mock")
        _mongo_db = MockMongoDB()
        print("  [OK] NoSQL Database initialized (mock fallback)")
    return _mongo_db


def get_nosql_db():
    """Get the NoSQL database instance."""
    global _mongo_db
    if _mongo_db is None:
        _mongo_db = MockMongoDB()
    return _mongo_db

"""
AquaIntelli - SQL Database (SQLAlchemy + SQLite/PostgreSQL)
Primary structured data store for readings, predictions, alerts.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.SQL_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_sql_db():
    """Create all SQL tables on startup."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("  [OK] SQL Database initialized")
    except (ImportError, ValueError) as e:
        print(f"  [!] SQL Database initialization skipped (missing dependency: {e})")
        print("    Running in memory-only mode for some features.")

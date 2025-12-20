"""
Dependency Injection
FastAPI dependencies for database sessions, authentication, etc.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings

# Create async engine with SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DEBUG,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    Yields an async database session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database on startup"""
    from app.models.base import Base

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections on shutdown"""
    await engine.dispose()

"""
Base Repository with generic CRUD operations
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository class with generic CRUD operations

    This class provides common database operations for all models
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """
        Get a single record by ID

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filter conditions

        Returns:
            List of model instances
        """
        query = select(self.model)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record

        Args:
            db: Database session
            obj_in: Pydantic schema with data

        Returns:
            Created model instance
        """
        # Convert Pydantic model to dict
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)

        # Create model instance
        db_obj = self.model(**obj_data)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Pydantic schema or dict with update data

        Returns:
            Updated model instance
        """
        # Convert to dict
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Update fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> bool:
        """
        Delete a record by ID

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            delete(self.model).where(self.model.id == id)
        )

        return result.rowcount > 0

    async def count(self, db: AsyncSession, **filters) -> int:
        """
        Count records with optional filters

        Args:
            db: Database session
            **filters: Filter conditions

        Returns:
            Number of matching records
        """
        query = select(self.model)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        result = await db.execute(query)
        return len(list(result.scalars().all()))

    async def exists(self, db: AsyncSession, id: str) -> bool:
        """
        Check if a record exists

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        result = await db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None

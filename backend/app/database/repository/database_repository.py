from typing import Generic, TypeVar
from datetime import datetime

from sqlalchemy import BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.models import Base

Model = TypeVar("Model", bound=Base)


class AbstractRepository(Generic[Model]):
    async def create(self, data: dict) -> Model:
        raise NotImplementedError

    async def get(self, pk: int) -> Model | None:
        raise NotImplementedError

    async def update(self, instance: Model, data: dict) -> Model:
        raise NotImplementedError

    async def delete(self, instance: Model) -> Model:
        raise NotImplementedError

    async def get_all(self) -> list[Model]:
        raise NotImplementedError

    async def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        raise NotImplementedError

class DatabaseRepository(AbstractRepository[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, pk: int) -> Model | None:
        return await self.session.get(self.model, int(pk))

    async def update(self, instance: Model, data: dict) -> Model:
        for field, value in data.items():
            setattr(instance, field, value)

        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: Model) -> Model:
        # If self.model has a deleted field, set it to True
        if hasattr(instance, "deleted"):
            setattr(instance, "deleted", True)
            return await self.update(
                instance, {"deleted": True, "updated_at": datetime.now()}
            )

        # Otherwise, delete the instance
        await self.session.delete(instance)
        await self.session.commit()
        return instance

    async def get_all(self, include_deleted=False) -> list[Model]:
        query = select(self.model)

        if hasattr(self.model, "deleted") and not include_deleted:
            query = query.where(self.model.deleted == False)  # noqa: E712

        return list((await self.session.scalars(query)).all())

    async def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))

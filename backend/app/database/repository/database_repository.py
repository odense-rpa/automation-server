from typing import Generic, TypeVar
from datetime import datetime

from sqlalchemy import BinaryExpression
from sqlmodel import Session, select

from app.database.models import Base

Model = TypeVar("Model", bound=Base)


class AbstractRepository(Generic[Model]):
    def create(self, data: dict) -> Model:
        raise NotImplementedError

    def get(self, pk: int) -> Model | None:
        raise NotImplementedError

    def update(self, instance: Model, data: dict) -> Model:
        raise NotImplementedError

    def delete(self, instance: Model) -> Model:
        raise NotImplementedError

    def get_all(self) -> list[Model]:
        raise NotImplementedError

    def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        raise NotImplementedError

class DatabaseRepository(AbstractRepository[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: Session) -> None:
        self.model = model
        self.session = session

    def create(self, data: dict) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get(self, pk: int) -> Model | None:
        return self.session.get(self.model, pk)

    def update(self, instance: Model, data: dict) -> Model:
        for field, value in data.items():
            setattr(instance, field, value)

        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.now()

        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: Model) -> Model:
        # If self.model has a deleted field, set it to True
        if hasattr(instance, "deleted"):
            setattr(instance, "deleted", True)
            return self.update(
                instance, {"deleted": True, "updated_at": datetime.now()}
            )

        # Otherwise, delete the instance
        self.session.delete(instance)
        self.session.commit()
        return instance

    def get_all(self, include_deleted=False) -> list[Model]:
        query = select(self.model)

        if hasattr(self.model, "deleted") and not include_deleted:
            query = query.where(self.model.deleted == False)  # noqa: E712

        return self.session.scalars(query).all()

    def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(self.session.scalars(query))

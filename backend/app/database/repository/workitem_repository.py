import abc

from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, desc

from app.database.models import WorkItem
import app.enums as enums

from .database_repository import DatabaseRepository, AbstractRepository

class AbstractWorkItemRepository(AbstractRepository[WorkItem]):
    @abc.abstractmethod
    def get_next_item(self, queue_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_reference(self, reference: str, status: enums.WorkItemStatus | None = None) -> list[WorkItem]:
        raise NotImplementedError
  


class WorkItemRepository(DatabaseRepository[WorkItem]):
    def __init__(self, session: Session) -> None:
        super().__init__(WorkItem, session)

    def get_next_item(self, queue_id: int):
        """
        Retrieves and locks the next available work item from a specified queue.

        This method selects the next available work item based on the provided
        queue ID, marking the item as locked and updating its status to
        IN_PROGRESS. It ensures atomicity through transaction management and
        prioritizes items based on their creation timestamp.

        Parameters:
            queue_id (int): The ID of the queue to retrieve the next work item from.

        Returns:
            WorkItem | None: The next available work item if found; otherwise, None.

        Raises:
            Exception: Propagates any exceptions that occur during database access or
                    transaction handling, after rolling back any changes.
        """
        try:
            item = self.session.scalars(
                select(WorkItem)
                .where(WorkItem.workqueue_id == queue_id)
                .where(WorkItem.locked == False)  # noqa: E712
                .where(WorkItem.status == enums.WorkItemStatus.NEW)
                .order_by(WorkItem.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)  # Use skip_locked to avoid waiting for locked rows
            ).first()

            if item is None:
                return None

            item.locked = True
            item.status = enums.WorkItemStatus.IN_PROGRESS
            item.updated_at = datetime.now()
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
            return item
        except IntegrityError:
            self.session.rollback()
            raise

    def get_by_reference(self, reference: str, status: enums.WorkItemStatus | None = None) -> list[WorkItem]:
        """Get work items by reference value, optionally filtered by status, sorted newest to oldest."""
        if not reference or reference.strip() == "":
            return []
        
        query = select(WorkItem).where(
            WorkItem.reference == reference
        )
        
        if status is not None:
            query = query.where(WorkItem.status == status)
            
        query = query.order_by(desc(WorkItem.created_at))
        
        return list(self.session.scalars(query))


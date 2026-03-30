import pytest
from datetime import datetime, timedelta

from app.database.models import Session, Resource
from app.enums import SessionStatus
from app.services import SessionService


@pytest.fixture(params=["active", "orphaned"])
def session_repository(request):
    class MockSessionRepository:
        def __init__(self, variant):
            self.data = None
            self.variant = variant

        async def get_active_sessions(self):
            if self.variant == "active":
                return [
                    Session(
                        id=1,
                        status=SessionStatus.IN_PROGRESS,
                        dispatched_at=datetime.now() - timedelta(hours=5),
                        resource_id=1,
                    )
                ]
            return []

        async def get_new_sessions(self):
            if self.variant == "orphaned":
                return [
                    Session(
                        id=1,
                        resource_id=1,
                        status=SessionStatus.NEW,
                    )
                ]
            return []

        async def update(self, session, data):
            self.data = data

        async def get(self, id):
            return None

    return MockSessionRepository(request.param)

@pytest.fixture
def resource_repository():
    class MockResourceRepository:
        async def get(self, id):
            return Resource(id=1, available=False, deleted = True)
    return MockResourceRepository()

# Test for flushing active sessions
@pytest.mark.parametrize("session_repository", ["active"], indirect=True)
async def test_flush_dangling_sessions(session_repository, resource_repository):
    service = SessionService(session_repository, resource_repository)
    await service.flush_dangling_sessions()
    assert session_repository.data == {
        "status": SessionStatus.FAILED,
    }

# Test for rescheduling orphaned sessions
@pytest.mark.parametrize("session_repository", ["orphaned"], indirect=True)
async def test_reschedule_orphaned_sessions(session_repository, resource_repository):
    service = SessionService(session_repository, resource_repository)
    await service.reschedule_orphaned_sessions()
    assert session_repository.data == {
        "resource_id": None,
        "dispatched_at": None,
    }

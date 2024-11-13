from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models
import app.enums as enums


from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401

def test_get_session_logs(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/sessionlogs/525")
    assert response.status_code == 404

    
    response = client.get("/sessionlogs/1")
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["page"] == 1
    assert data["total_items"] == 2
    assert data["total_pages"] == 1

    response = client.get("/sessionlogs/1?size=1")
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["page"] == 1
    assert data["total_items"] == 2
    assert data["total_pages"] == 2


def test_get_sessionlog_by_workitem(session: Session, client: TestClient):
    generate_basic_data(session)
    
    response = client.get("/sessionlogs/by_workitem/525")
    assert response.status_code == 404
    
    response = client.get("/sessionlogs/by_workitem/1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1





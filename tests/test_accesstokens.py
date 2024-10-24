from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models

from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401


def test_get_accesstoken_no_token(session: Session, client: TestClient):
    generate_basic_data(session)
    response = client.get("/api/accesstokens/")

    assert response.text == '[]'
    assert response.status_code == 200

def test_create_and_access_without_token(session: Session, client: TestClient):
    generate_basic_data(session)

    # Create a new access token
    response = client.post(
        "/api/accesstokens",
        json={
            "identifier": "UnusedAccessToken",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["identifier"] == "UnusedAccessToken"

    # Try to access the API without using the created token
    response = client.get("/api/accesstokens/1")

    assert response.status_code == 401

def test_delete_accesstoken(session: Session, client: TestClient):
    generate_basic_data(session)

    # Create a new access token
    response = client.post(
        "/api/accesstokens",
        json={
            "identifier": "UnusedAccessToken",
        },
    )
    assert response.status_code == 200

    data = response.json()
    access_token = data["access_token"]

    # Delete the access token
    response = client.delete(
        "/api/accesstokens/1",
        headers={"Authorization": f"Bearer {access_token}"},)
    data = response.json()
    
    assert response.status_code == 200
    assert data["deleted"] is True



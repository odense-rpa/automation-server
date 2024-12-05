from fastapi.testclient import TestClient
from sqlmodel import Session

import app.database.models as models

from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401


def test_get_credentials(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/credentials/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Secret credential"
    assert data[0]["username"] == "Secret username"
    assert data[0]["deleted"] is False

    response = client.get("/credentials/?include_deleted=true")
    data = response.json()
    assert len(data) == 2

    assert data[1]["name"] == "Secret deleted credential"
    assert data[1]["username"] == "Secret deleted username"
    assert data[1]["deleted"] is True


def test_get_credential(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/credentials/1")

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Secret credential"
    assert data["username"] == "Secret username"
    assert data["deleted"] is False

    response = client.get("/credentials/2")

    assert response.status_code == 410


def test_update_credential(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/credentials/1",
        json={
            "name": "Secret credential",
            "username": "Secret username",
            "password": "New password",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Secret credential"
    assert data["username"] == "Secret username"
    assert data["password"] == "New password"

    response = client.put(
        "/credentials/2",
        json={
            "name": "Secret deleted credential",
            "username": "Secret deleted username",
            "password": "New password",
            "description": "New description",
        },
    )

    assert response.status_code == 410

def test_create_credential(session: Session, client: TestClient):
    generate_basic_data(session)   

    response = client.post(
        "/credentials/",
        json={
            "name": "New credential",
            "username": "New username",
            "password": "New password",
        },
    )

    assert response.status_code == 200
    
def test_delete_credential(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.delete("/credentials/1")

    assert response.status_code == 204

    # Verify against the database
    
    credential = session.get(models.Credential, 1)
    assert credential.deleted is True


    response = client.delete("/credentials/2")

    assert response.status_code == 410

def test_retrieve_existing_credential_by_name(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/credentials/by_name/Secret credential")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Secret credential"
    assert data["username"] == "Secret username"
    assert data["deleted"] is False

def test_credential_not_found(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/credentials/by_name/nonexistent_credential")

    assert response.status_code == 404
    assert response.json() == {"detail": "Credential not found"}

def test_credential_deleted(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/credentials/by_name/Secret deleted credential")

    assert response.status_code == 410
    assert response.json() == {"detail": "Credential is gone"}

def test_case_sensitivity(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/credential/by_name/SeCreT cRedeNtiAl")
    assert response.status_code == 404  # Assuming case-sensitive

def test_empty_credential_name(session: Session, client: TestClient):
    response = client.get("/credential/by_name/")
    assert response.status_code == 404  # Assuming FastAPI route validation catches this

def test_insert_non_unique_named_credential(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.post(
        "/credentials/",
        json={
            "name": "Secret credential",
            "username": "New username",
            "password": "New password",
        },
    )

    assert response.status_code == 422

def test_create_credential_with_invalid_json_data(session: Session, client: TestClient):
    response = client.post(
        "/credentials/",
        json={
            "name": "New credential",
            "username": "New username",
            "password": "New password",
            "data": "invalid json",
        },
    )

    assert response.status_code == 422    

def test_create_credential_with_empty_json_data(session: Session, client: TestClient):
    response = client.post(
        "/credentials/",
        json={
            "name": "New credential",
            "username": "New username",
            "password": "New password",
            "data": "",
        },
    )

    assert response.status_code == 200
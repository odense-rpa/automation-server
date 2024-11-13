from fastapi.testclient import TestClient
from sqlmodel import Session

from . import session_fixture, client_fixture, generate_basic_data  # noqa: F401


def test_get_resources(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/resources")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1

    assert data[0]["name"] == "resource"
    assert data[0]["fqdn"] == "resource.example.com"
    assert data[0]["deleted"] is False

    response = client.get("/resources/?include_expired=true")
    data = response.json()
    assert len(data) == 3

def test_get_resource(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/resources/1")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "resource"
    assert data["fqdn"] == "resource.example.com"
    assert data["deleted"] is False

def test_create_resource(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.post(
        "/resources",
        json={
            "name": "resource3",
            "fqdn": "resource3.example.com",
            "capabilities": "win32 chrome blueprism",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource3"
    assert data["fqdn"] == "resource3.example.com"
    assert data["available"] is True
    assert data["last_seen"] is not None

def test_resource_should_expire(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.get("/resources/3")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource-should-expire"
    assert data["available"] is True

    # This will trigger a full available resource update
    response = client.get("/resources")
    assert response.status_code == 200

    response = client.get("/resources/3")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource-should-expire"
    assert data["available"] is False




# def test_create_and_revive_resource(session: Session, client: TestClient):
#     generate_basic_data(session)

#     response = client.post(
#         "/api/resources",
#         json={
#             "name": "resource-old",
#             "fqdn": "resource-old.example.com",
#             "capabilities": "win32",
#         },
#     )

#     assert response.status_code == 200

#     data = response.json()
#     assert data["name"] == "resource-old"
#     assert data["fqdn"] == "resource-old.example.com"
#     assert data["capabilities"] == "win32"
#     assert data["available"] is True

#     #dt = datetime.fromisoformat(data["last_seen"]) a

#     #print(dt)

#     #assert dt > datetime.now() - timedelta(minutes=1)


def test_update_resource(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/resources/1",
        json={
            "name": "resource",
            "fqdn": "resource.example.com",
            "capabilities": "win32 chrome python",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource"
    assert data["fqdn"] == "resource.example.com"
    assert data["capabilities"] == "win32 chrome python"
    assert data["available"] is True
    assert data["last_seen"] is not None

def test_update_old_resource(session: Session, client: TestClient):
    generate_basic_data(session)

    response = client.put(
        "/resources/2",
        json={
            "name": "resource-old",
            "fqdn": "resource-old.example.com",
            "capabilities": "win32 chrome python blue_prism",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "resource-old"
    assert data["fqdn"] == "resource-old.example.com"
    assert data["capabilities"] == "win32 chrome python blue_prism"
    assert data["available"] is True
    assert data["last_seen"] is not None
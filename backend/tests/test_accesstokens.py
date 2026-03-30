from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession



from . import generate_basic_data  # noqa: F401


async def test_get_accesstoken_no_token(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)
    response = await client.get("/accesstokens/")

    assert response.text == '[]'
    assert response.status_code == 200

async def test_get_accesstokens(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Create a new access token
    response = await client.post(
        "/accesstokens",
        json={
            "identifier": "UnusedAccessToken",
        },
    )

    data = response.json()
    access_token = data["access_token"]

    # Get the access token
    response = await client.get(
        "/accesstokens/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Create a 2nd access token with returned token
    response = await client.post(
        "/accesstokens",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "identifier": "UnusedAccessToken2",
        },
    )

    # Get all access tokens
    response = await client.get(
        "/accesstokens/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    data = response.json()
    assert data[0]["identifier"] == "UnusedAccessToken"
    assert data[1]["identifier"] == "UnusedAccessToken2"
    assert len(data) == 2

async def test_create_and_access_without_token(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Create a new access token
    response = await client.post(
        "/accesstokens",
        json={
            "identifier": "UnusedAccessToken",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["identifier"] == "UnusedAccessToken"

    # Try to access the API without using the created token
    response = await client.get("/accesstokens/1")

    assert response.status_code == 401

async def test_delete_accesstoken(session: AsyncSession, client: AsyncClient):
    await generate_basic_data(session)

    # Create a new access token
    response = await client.post(
        "/accesstokens",
        json={
            "identifier": "UnusedAccessToken",
        },
    )
    assert response.status_code == 200

    data = response.json()
    access_token = data["access_token"]

    # Delete the access token
    response = await client.delete(
        "/accesstokens/1",
        headers={"Authorization": f"Bearer {access_token}"},)

    assert response.status_code == 204



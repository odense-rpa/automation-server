from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient

from app.config import cors_origins, settings


def test_cors_origins_empty_by_default(monkeypatch):
    monkeypatch.setattr(settings, "cors_allow_origins", "")
    assert cors_origins() == []


def test_cors_origins_parses_comma_separated_list(monkeypatch):
    monkeypatch.setattr(
        settings, "cors_allow_origins", "http://a.example, http://b.example"
    )
    assert cors_origins() == ["http://a.example", "http://b.example"]


def test_cors_origins_wildcard_is_an_explicit_opt_in(monkeypatch):
    monkeypatch.setattr(settings, "cors_allow_origins", "*")
    assert cors_origins() == ["*"]


def _build_app(origins):
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


async def test_default_sends_no_cross_origin_header():
    # No configured origins: same-origin requests are unaffected (browsers
    # don't send Origin/CORS preflights for those), but a cross-origin one
    # gets no access-control-allow-origin header and is refused by the browser.
    app = _build_app([])

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/ping", headers={"Origin": "http://evil.example"}
        )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


async def test_configured_origin_is_echoed_back():
    app = _build_app(["http://allowed.example"])

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/ping", headers={"Origin": "http://allowed.example"}
        )

    assert response.headers["access-control-allow-origin"] == "http://allowed.example"


async def test_configured_origin_rejects_other_origins():
    app = _build_app(["http://allowed.example"])

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/ping", headers={"Origin": "http://other.example"}
        )

    assert "access-control-allow-origin" not in response.headers

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from asgi_lifespan import LifespanManager

from phinder_api.main import app
from phinder_api.state import InMemoryStore


@pytest.mark.asyncio
async def test_upload_file():
    file_path = "data/eicar.com"

    transport = ASGITransport(app=app)

    async with LifespanManager(app):
        async with AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, "application/octet-stream")}
                response = await client.post("/update", files=files)

            assert response.status_code == 200
            data = response.json()
            assert "vt_id" in data["data"]


@pytest.mark.asyncio
async def test_list_files():
    state = InMemoryStore()
    # Pre-populate with dummy file
    state.add_file(sha256="dummyhash123", size="1.23 Mb", vt_id="dummy_vt_id")

    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            response = await client.get("/list_files")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "dummyhash123" in data["data"]

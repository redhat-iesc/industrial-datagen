from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.context import AppContext
from app.main import app
from app.rtsp.manager import RTSPStreamManager
from app.storage.memory import MemoryStorage


@pytest.fixture
async def client(tmp_path: Path) -> AsyncClient:
    storage = MemoryStorage()
    rtsp_manager = RTSPStreamManager(base_dir=tmp_path / "rtsp-streams")
    app.state.app_context = AppContext(storage, rtsp_manager)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await app.state.app_context.cleanup()

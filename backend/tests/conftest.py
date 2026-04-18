from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.rtsp.manager import RTSPStreamManager
from app.storage.memory import MemoryStorage


@pytest.fixture
async def client(tmp_path: Path):
    app.state.storage = MemoryStorage()
    app.state.active_simulations = {}
    app.state.simulation_tasks = {}
    app.state.rtsp_manager = RTSPStreamManager(base_dir=tmp_path / "rtsp-streams")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await app.state.rtsp_manager.stop_all()
    for task in app.state.simulation_tasks.values():
        task.cancel()

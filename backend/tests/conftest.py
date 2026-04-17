import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.storage.memory import MemoryStorage


@pytest.fixture
async def client():
    app.state.storage = MemoryStorage()
    app.state.active_simulations = {}
    app.state.simulation_tasks = {}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    for task in app.state.simulation_tasks.values():
        task.cancel()

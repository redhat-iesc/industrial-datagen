"""Tests for AppContext class."""

import asyncio

import pytest

from app.context import AppContext
from app.rtsp.manager import RTSPStreamManager
from app.storage.memory import MemoryStorage


class TestAppContextInit:
    """AppContext initialization validates state creation."""

    def test_creates_storage(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())
        assert ctx.storage is not None

    def test_creates_rtsp_manager(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())
        assert ctx.rtsp_manager is not None

    def test_creates_empty_sim_dict(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())
        assert ctx.active_simulations == {}

    def test_creates_empty_task_dict(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())
        assert ctx.simulation_tasks == {}


class TestAppContextCleanup:
    """AppContext cleanup runs cleanup protocol on all managed resources."""

    def test_cleanup_stops_rtsp(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())
        asyncio.run(ctx.cleanup())

    def test_cleanup_cancels_running_tasks(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())

        async def dummy() -> None:
            await asyncio.sleep(10)

        async def _run() -> None:
            task = asyncio.create_task(dummy())
            ctx.simulation_tasks["sim1"] = task
            await ctx.cleanup()
            # Task should now be in a cancelled state
            assert task.cancelled()

        asyncio.run(_run())


class TestStorageInterface:
    """Ensure AppContext provides access to core services."""

    def test_get_storage(self):
        storage = MemoryStorage()
        ctx = AppContext(storage, RTSPStreamManager())
        assert ctx.storage is storage

    def test_add_simulation(self):
        ctx = AppContext(MemoryStorage(), RTSPStreamManager())
        ctx.active_simulations["sim1"] = "sim"
        assert "sim1" in ctx.active_simulations


async def test_add_task():
    ctx = AppContext(MemoryStorage(), RTSPStreamManager())
    task = asyncio.create_task(asyncio.sleep(0))
    ctx.simulation_tasks["t1"] = task
    assert "t1" in ctx.simulation_tasks

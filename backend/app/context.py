"""Application context: dependency-injected shared state for FastAPI."""

from __future__ import annotations

import asyncio
import contextlib
from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Minimal storage interface for type-safe AppContext."""

    pass  # Full interface in app.storage.base


class AppContext:
    """Centralized, dependency-injected application state.

    Replaces direct ``app.state`` assignments so that:
    - Storage and simulator state have explicit lifecycle management
    - Each test gets an isolated context instance
    - Multi-worker deployments get per-worker state automatically
    - Cleanup follows a protocol instead of manual ``stop_all()`` calls
    """

    def __init__(self, storage: BaseStorage, rtsp_manager: object) -> None:
        self.storage = storage
        self.active_simulations: dict[str, object] = {}
        self.simulation_tasks: dict[str, asyncio.Task[None]] = {}
        self.rtsp_manager = rtsp_manager

    async def cleanup(self) -> None:
        """Cancel running simulations and stop RTSP streams."""
        for task in self.simulation_tasks.values():
            task.cancel()
        for task in self.simulation_tasks.values():
            with contextlib.suppress(asyncio.CancelledError):
                await task
        if hasattr(self.rtsp_manager, "stop_all"):
            await self.rtsp_manager.stop_all()


async def get_app_context() -> AppContext:
    """Create a fresh AppContext at application startup.

    In production the lifespan manages the single instance.
    Tests create instances in fixtures so each test gets isolation.
    """
    from app.rtsp.manager import RTSPStreamManager
    from app.storage.memory import MemoryStorage

    storage = MemoryStorage()
    rtsp_manager = RTSPStreamManager()
    return AppContext(storage, rtsp_manager)


async def get_context(request: object) -> AppContext:  # noqa: ANN101
    """FastAPI dependency that provides AppContext to route handlers."""
    # AppContext lives on app.state for now; depends on lifespan injection.
    ctx: AppContext = request.app.state.app_context
    return ctx

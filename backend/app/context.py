"""Application context: dependency-injected shared state for FastAPI.

Replaces direct ``app.state`` attribute assignments with a single
centralized context object that provides:
- Explicit lifecycle (init/cleanup)
- Per-test isolation
- Type-safe access to storage, simulations, and RTSP resources
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.rtsp.manager import RTSPStreamManager
    from app.storage.base import BaseStorage


class AppContext:
    """Centralized application state with explicit lifecycle management.

    Replaces direct ``app.state`` assignments so that:
    - Storage and simulator state have explicit lifecycle management
    - Each test gets an isolated context instance
    - Multi-worker deployments get per-worker state automatically
    - Cleanup follows a protocol instead of manual stop_all() calls
    """

    def __init__(self, storage: BaseStorage, rtsp_manager: RTSPStreamManager) -> None:
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


def create_app_context() -> tuple[BaseStorage, RTSPStreamManager]:  # noqa: PLR0911
    """Factory for production application context."""
    # Import here to avoid circular imports at module load time
    from app.rtsp.manager import RTSPStreamManager
    from app.storage.memory import MemoryStorage

    storage = MemoryStorage()
    rtsp_manager = RTSPStreamManager()
    return storage, rtsp_manager

import asyncio
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.datasets import router as datasets_router
from app.api.health import router as health_router
from app.api.processes import router as processes_router
from app.api.rtsp import router as rtsp_router
from app.api.simulations import router as simulations_router
from app.api.statistics import router as statistics_router
from app.api.streaming import router as streaming_router
from app.config import settings
from app.context import AppContext, create_app_context
from app.rtsp.manager import RTSPStreamManager
from app.storage.memory import MemoryStorage

start_time: float = 0.0


start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global start_time
    start_time = time.time()
    storage, rtsp_manager = create_app_context()
    app.state.app_context = AppContext(storage, rtsp_manager)
    yield
    await app.state.app_context.cleanup()


async def get_app_context(request: Request) -> AppContext:
    """FastAPI dependency providing centralized app state."""
    return request.app.state.app_context  # type: ignore[no-any-return]


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(processes_router, prefix="/api")
app.include_router(simulations_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(statistics_router, prefix="/api")
app.include_router(streaming_router, prefix="/api")
app.include_router(rtsp_router, prefix="/api")

static_dir = os.environ.get("INDGEN_STATIC_DIR", "")
if static_dir and Path(static_dir).is_dir():
    app.mount("/assets", StaticFiles(directory=Path(static_dir) / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        file_path = Path(static_dir) / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(Path(static_dir) / "index.html")

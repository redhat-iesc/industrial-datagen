import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.datasets import router as datasets_router
from app.api.health import router as health_router
from app.api.processes import router as processes_router
from app.api.simulations import router as simulations_router
from app.api.statistics import router as statistics_router
from app.api.streaming import router as streaming_router
from app.config import settings
from app.storage.memory import MemoryStorage

start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global start_time
    start_time = time.time()
    app.state.storage = MemoryStorage()
    app.state.active_simulations = {}
    app.state.simulation_tasks = {}
    yield
    for task in app.state.simulation_tasks.values():
        task.cancel()


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

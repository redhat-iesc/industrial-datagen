import time

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, object]:
    from app.main import start_time

    return {
        "status": "healthy",
        "uptime": time.time() - start_time,
        "version": "0.1.0",
    }

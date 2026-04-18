from typing import Any

from fastapi import APIRouter, HTTPException

from app.simulators import SIMULATOR_REGISTRY, get_simulator_class

router = APIRouter(tags=["processes"])


@router.get("/processes")
async def list_processes() -> list[dict[str, Any]]:
    processes = []
    for _name, cls in SIMULATOR_REGISTRY.items():
        sim = cls()
        processes.append(sim.get_schema())
    return processes


@router.get("/processes/{process_type}/schema")
async def get_process_schema(process_type: str) -> dict[str, Any]:
    cls = get_simulator_class(process_type)
    if cls is None:
        raise HTTPException(status_code=404, detail=f"Unknown process type: {process_type}")
    sim = cls()
    return sim.get_schema()

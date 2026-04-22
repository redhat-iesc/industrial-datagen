import asyncio
import contextlib
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.models.simulation import (
    FaultRequest,
    ParameterUpdateRequest,
    SimulationStatus,
    StartSimulationRequest,
)
from app.simulators import get_simulator_class
from app.simulators.base import BaseSimulator
from app.simulators.rotating import RotatingEquipmentSimulator
from app.storage.base import BaseStorage

router = APIRouter(tags=["simulations"])


def _get_storage(request: Request) -> BaseStorage:
    return request.app.state.app_context.storage  # type: ignore[no-any-return]


def _get_active_sims(request: Request) -> dict[str, BaseSimulator]:
    return request.app.state.app_context.active_simulations  # type: ignore[no-any-return]


def _get_sim_tasks(request: Request) -> dict[str, asyncio.Task[None]]:
    return request.app.state.app_context.simulation_tasks  # type: ignore[no-any-return]


@router.get("/simulations")
async def list_simulations(
    request: Request,
    status: str | None = None,
    processType: str | None = None,  # noqa: N803
) -> list[dict[str, Any]]:
    storage = _get_storage(request)
    sims = await storage.list_simulations()
    if status:
        sims = [s for s in sims if s.get("status") == status]
    if processType:
        sims = [s for s in sims if s.get("processType") == processType]
    return sims


@router.post("/simulation/start")
async def start_simulation(body: StartSimulationRequest, request: Request) -> dict[str, Any]:
    cls = get_simulator_class(body.process_type)
    if cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown process type: {body.process_type}")

    sim = cls(body.parameters if body.parameters else None)
    sim_id = str(uuid.uuid4())

    sim_info = {
        "id": sim_id,
        "processType": body.process_type,
        "status": SimulationStatus.RUNNING.value,
        "parameters": sim.parameters,
        "createdAt": time.time(),
        "stepCount": 0,
        "intervalMs": body.interval_ms,
    }

    storage = _get_storage(request)
    await storage.save_simulation(sim_id, sim_info)

    active_sims = _get_active_sims(request)
    active_sims[sim_id] = sim

    task = asyncio.create_task(_run_simulation(request, sim_id, sim, body.interval_ms))
    sim_tasks = _get_sim_tasks(request)
    sim_tasks[sim_id] = task

    return sim_info


async def _run_simulation(
    request: Request, sim_id: str, sim: BaseSimulator, interval_ms: int
) -> None:
    storage = _get_storage(request)
    try:
        while True:
            row = sim.step()
            await storage.append_simulation_data(sim_id, row)
            sim_info = await storage.get_simulation(sim_id)
            if sim_info:
                step_count: int = sim_info.get("stepCount", 0)  # type: ignore[assignment]
                sim_info["stepCount"] = step_count + 1
                await storage.save_simulation(sim_id, sim_info)
            await asyncio.sleep(interval_ms / 1000.0)
    except asyncio.CancelledError:
        pass


@router.get("/simulation/{sim_id}/current")
async def get_current(sim_id: str, request: Request) -> dict[str, Any]:
    storage = _get_storage(request)
    sim_info = await storage.get_simulation(sim_id)
    if not sim_info:
        raise HTTPException(status_code=404, detail="Simulation not found")

    latest = await storage.get_simulation_latest(sim_id)
    return {"simulation": sim_info, "current": latest}


@router.get("/simulation/{sim_id}/history")
async def get_history(
    sim_id: str, request: Request, limit: int = 100, offset: int = 0
) -> dict[str, Any]:
    storage = _get_storage(request)
    sim_info = await storage.get_simulation(sim_id)
    if not sim_info:
        raise HTTPException(status_code=404, detail="Simulation not found")

    rows = await storage.get_simulation_history(sim_id, limit, offset)
    return {"simulation": sim_info, "data": rows, "count": len(rows)}


@router.post("/simulation/{sim_id}/stop")
async def stop_simulation(sim_id: str, request: Request) -> dict[str, Any]:
    storage = _get_storage(request)
    sim_info = await storage.get_simulation(sim_id)
    if not sim_info:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim_tasks = _get_sim_tasks(request)
    task = sim_tasks.pop(sim_id, None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    active_sims = _get_active_sims(request)
    active_sims.pop(sim_id, None)

    sim_info["status"] = SimulationStatus.STOPPED.value
    await storage.save_simulation(sim_id, sim_info)

    return sim_info


@router.patch("/simulation/{sim_id}/parameters")
async def update_parameters(
    sim_id: str, body: ParameterUpdateRequest, request: Request
) -> dict[str, Any]:
    storage = _get_storage(request)
    sim_info = await storage.get_simulation(sim_id)
    if not sim_info:
        raise HTTPException(status_code=404, detail="Simulation not found")

    active_sims = _get_active_sims(request)
    sim = active_sims.get(sim_id)
    if not sim:
        raise HTTPException(status_code=400, detail="Simulation is not running")

    sim.parameters.update(body.parameters)
    sim_info["parameters"] = sim.parameters
    await storage.save_simulation(sim_id, sim_info)

    return sim_info


@router.post("/simulation/{sim_id}/fault")
async def inject_fault(sim_id: str, body: FaultRequest, request: Request) -> dict[str, str]:
    active_sims = _get_active_sims(request)
    sim = active_sims.get(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found or not running")

    if not isinstance(sim, RotatingEquipmentSimulator):
        raise HTTPException(
            status_code=400, detail="Fault injection only supported for rotating equipment"
        )

    try:
        sim.inject_fault(body.fault_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    return {"status": "ok", "faultType": body.fault_type}

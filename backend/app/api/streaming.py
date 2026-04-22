import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from starlette.responses import StreamingResponse

from app.storage.base import BaseStorage

router = APIRouter(tags=["streaming"])


@router.websocket("/ws/simulation/{sim_id}")
async def simulation_websocket(websocket: WebSocket, sim_id: str) -> None:
    await websocket.accept()
    storage: BaseStorage = websocket.app.state.app_context.storage
    sim_info = await storage.get_simulation(sim_id)
    if not sim_info:
        await websocket.close(code=4004, reason="Simulation not found")
        return

    last_step: int = -1
    try:
        while True:
            latest = await storage.get_simulation_latest(sim_id)
            if latest:
                ts = latest.get("timestamp")
                if ts is not None and isinstance(ts, int) and ts != last_step:
                    last_step = ts
                    await websocket.send_json(latest)

            sim_info = await storage.get_simulation(sim_id)
            if not sim_info or sim_info.get("status") != "running":
                await websocket.send_json({"type": "stopped"})
                break

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass


@router.get("/simulation/{sim_id}/feed")
async def simulation_sse(sim_id: str, request: Request) -> StreamingResponse:
    storage = request.app.state.app_context.storage
    sim_info = await storage.get_simulation(sim_id)
    if not sim_info:
        raise HTTPException(status_code=404, detail="Simulation not found")

    async def event_stream() -> AsyncGenerator[str, None]:
        last_step: int = -1
        while True:
            if await request.is_disconnected():
                break

            latest = await storage.get_simulation_latest(sim_id)
            if latest:
                ts = latest.get("timestamp")
                if ts is not None and isinstance(ts, int) and ts != last_step:  # noqa: E501
                    last_step = ts
                    yield f"data: {json.dumps(latest)}\n\n"

            sim_info = await storage.get_simulation(sim_id)
            if not sim_info or sim_info.get("status") != "running":
                yield f"data: {json.dumps({'type': 'stopped'})}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

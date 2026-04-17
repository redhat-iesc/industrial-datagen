from fastapi import APIRouter, HTTPException, Request

from app.simulators import get_simulator_class

router = APIRouter(tags=["statistics"])


@router.get("/statistics/{process_type}")
async def get_statistics(process_type: str, request: Request):
    cls = get_simulator_class(process_type)
    if cls is None:
        raise HTTPException(status_code=404, detail=f"Unknown process type: {process_type}")

    storage = request.app.state.storage
    sims = await storage.list_simulations()
    matching = [s for s in sims if s.get("processType") == process_type]

    total_steps = sum(s.get("stepCount", 0) for s in matching)

    return {
        "processType": process_type,
        "totalSimulations": len(matching),
        "totalSteps": total_steps,
        "activeSimulations": sum(
            1 for s in matching if s.get("status") == "running"
        ),
    }

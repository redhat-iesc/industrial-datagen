import csv
import io
import json
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.context import AppContext
from app.models.dataset import DatasetStatus, GenerateDatasetRequest
from app.simulators import get_simulator_class
from app.storage.base import BaseStorage

router = APIRouter(tags=["datasets"])


def _get_storage(request: Request) -> BaseStorage:
    return request.app.state.app_context.storage  # type: ignore[no-any-return]


@router.post("/datasets/generate")
async def generate_dataset(body: GenerateDatasetRequest, request: Request) -> dict[str, Any]:
    cls = get_simulator_class(body.process_type)
    if cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown process type: {body.process_type}")

    dataset_id = str(uuid.uuid4())
    storage = _get_storage(request)

    dataset_info = {
        "id": dataset_id,
        "processType": body.process_type,
        "status": DatasetStatus.GENERATING.value,
        "samples": body.samples,
        "includeAnomalies": body.include_anomalies,
        "format": body.format,
        "createdAt": time.time(),
        "fileSize": None,
    }
    await storage.save_dataset(dataset_id, dataset_info)

    sim = cls()
    rows = sim.generate_dataset(body.samples, include_anomalies=body.include_anomalies)
    await storage.save_dataset_rows(dataset_id, rows)

    dataset_info["status"] = DatasetStatus.READY.value
    dataset_info["fileSize"] = len(json.dumps(rows))
    await storage.save_dataset(dataset_id, dataset_info)

    return dataset_info


@router.get("/datasets")
async def list_datasets(request: Request) -> list[dict[str, Any]]:
    storage = _get_storage(request)
    return await storage.list_datasets()


@router.get("/datasets/{dataset_id}/status")
async def get_dataset_status(dataset_id: str, request: Request) -> dict[str, Any]:
    storage = _get_storage(request)
    info = await storage.get_dataset(dataset_id)
    if not info:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return info


@router.get("/datasets/{dataset_id}/download")
async def download_dataset(
    dataset_id: str, request: Request, format: str = "csv"
) -> StreamingResponse:
    storage = _get_storage(request)
    info = await storage.get_dataset(dataset_id)
    if not info:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if info["status"] != DatasetStatus.READY.value:
        raise HTTPException(status_code=400, detail="Dataset is not ready")

    rows = await storage.get_dataset_rows(dataset_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Dataset data not found")

    if format == "json":
        return StreamingResponse(
            io.BytesIO(json.dumps(rows, indent=2).encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={dataset_id}.json"},
        )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    content = output.getvalue().encode()

    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dataset_id}.csv"},
    )


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str, request: Request) -> dict[str, str]:
    storage = _get_storage(request)
    deleted = await storage.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": "deleted"}

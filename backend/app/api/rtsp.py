from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from app.models.rtsp import RTSPConfigEntry, SetRTSPUrlRequest, StreamActionResponse, StreamStatus
from app.rtsp.manager import RTSPStreamManager
from app.simulators import SIMULATOR_REGISTRY

router = APIRouter(prefix="/rtsp", tags=["rtsp"])

VALID_PROCESS_TYPES = set(SIMULATOR_REGISTRY.keys())


def _validate_process_type(process_type: str) -> None:
    if process_type not in VALID_PROCESS_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown process type: {process_type}")


def _get_manager(request: Request) -> RTSPStreamManager:
    return request.app.state.rtsp_manager


@router.get("/config")
async def get_rtsp_config(request: Request) -> dict[str, RTSPConfigEntry]:
    manager = _get_manager(request)
    configs = manager.get_all_configs(list(VALID_PROCESS_TYPES))
    return {pt: RTSPConfigEntry(**cfg) for pt, cfg in configs.items()}


@router.put("/config/{process_type}")
async def set_rtsp_url(process_type: str, body: SetRTSPUrlRequest, request: Request) -> RTSPConfigEntry:
    _validate_process_type(process_type)
    manager = _get_manager(request)
    manager.set_url(process_type, body.url)
    cfg = manager.get_config(process_type)
    return RTSPConfigEntry(**cfg)


@router.post("/{process_type}/start")
async def start_stream(process_type: str, request: Request) -> StreamActionResponse:
    _validate_process_type(process_type)
    manager = _get_manager(request)
    try:
        state = await manager.start_stream(process_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StreamActionResponse(
        processType=process_type,
        status=state.status,
        startedAt=state.started_at,
    )


@router.post("/{process_type}/stop")
async def stop_stream(process_type: str, request: Request) -> StreamActionResponse:
    _validate_process_type(process_type)
    manager = _get_manager(request)
    await manager.stop_stream(process_type)
    return StreamActionResponse(
        processType=process_type,
        status=StreamStatus.OFFLINE,
        startedAt=None,
    )


@router.get("/{process_type}/stream.m3u8")
async def get_playlist(process_type: str, request: Request) -> FileResponse:
    _validate_process_type(process_type)
    manager = _get_manager(request)
    playlist = manager.get_stream_dir(process_type) / "stream.m3u8"
    if not playlist.is_file():
        raise HTTPException(status_code=404, detail="Stream not available")
    return FileResponse(
        path=playlist,
        media_type="application/vnd.apple.mpegurl",
    )


@router.get("/{process_type}/{segment}")
async def get_segment(process_type: str, segment: str, request: Request) -> FileResponse:
    _validate_process_type(process_type)
    if not RTSPStreamManager.validate_segment_name(segment):
        raise HTTPException(status_code=400, detail="Invalid segment name")
    manager = _get_manager(request)
    seg_path = manager.get_stream_dir(process_type) / segment
    if not seg_path.is_file():
        raise HTTPException(status_code=404, detail="Segment not found")
    return FileResponse(path=seg_path, media_type="video/mp2t")

from enum import StrEnum

from pydantic import BaseModel, Field


class StreamStatus(StrEnum):
    OFFLINE = "offline"
    STARTING = "starting"
    STREAMING = "streaming"
    ERROR = "error"


class RTSPConfigEntry(BaseModel):
    url: str | None = None
    status: StreamStatus = StreamStatus.OFFLINE

    model_config = {"populate_by_name": True}


class SetRTSPUrlRequest(BaseModel):
    url: str | None = None


class StreamActionResponse(BaseModel):
    process_type: str = Field(alias="processType")
    status: StreamStatus
    started_at: str | None = Field(default=None, alias="startedAt")

    model_config = {"populate_by_name": True}

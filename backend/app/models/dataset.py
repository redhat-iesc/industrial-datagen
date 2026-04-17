from enum import Enum

from pydantic import BaseModel, Field


class DatasetStatus(str, Enum):
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


class GenerateDatasetRequest(BaseModel):
    process_type: str = Field(alias="processType")
    samples: int = Field(default=1000, ge=1, le=100000)
    include_anomalies: bool = Field(default=True, alias="includeAnomalies")
    format: str = Field(default="csv")

    model_config = {"populate_by_name": True}


class DatasetInfo(BaseModel):
    id: str
    process_type: str = Field(alias="processType")
    status: DatasetStatus
    samples: int
    include_anomalies: bool = Field(alias="includeAnomalies")
    format: str
    created_at: float = Field(alias="createdAt")
    file_size: int | None = Field(default=None, alias="fileSize")

    model_config = {"populate_by_name": True}

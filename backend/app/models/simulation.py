from enum import StrEnum

from pydantic import BaseModel, Field


class SimulationStatus(StrEnum):
    RUNNING = "running"
    STOPPED = "stopped"
    COMPLETED = "completed"


class StartSimulationRequest(BaseModel):
    process_type: str = Field(alias="processType")
    parameters: dict[str, float] = Field(default_factory=dict)
    interval_ms: int = Field(default=1000, alias="intervalMs")

    model_config = {"populate_by_name": True}


class FaultRequest(BaseModel):
    fault_type: str = Field(alias="faultType")

    model_config = {"populate_by_name": True}


class ParameterUpdateRequest(BaseModel):
    parameters: dict[str, float]


class SimulationInfo(BaseModel):
    id: str
    process_type: str = Field(alias="processType")
    status: SimulationStatus
    parameters: dict[str, float]
    created_at: float = Field(alias="createdAt")
    step_count: int = Field(default=0, alias="stepCount")

    model_config = {"populate_by_name": True}

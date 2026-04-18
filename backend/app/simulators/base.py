import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ParameterDef:
    name: str
    min_val: float
    max_val: float
    default: float
    unit: str


@dataclass
class OutputField:
    name: str
    unit: str
    description: str = ""


class BaseSimulator(ABC):
    name: str = ""
    description: str = ""

    def __init__(self, parameters: dict[str, float] | None = None):
        self.parameters: dict[str, float] = {p.name: p.default for p in self.parameter_defs()}
        if parameters:
            self.parameters.update(parameters)
        self.state: dict[str, Any] = {}
        self._init_state()

    @abstractmethod
    def parameter_defs(self) -> list[ParameterDef]:
        ...

    @abstractmethod
    def output_fields(self) -> list[OutputField]:
        ...

    @abstractmethod
    def step(self) -> dict[str, Any]:
        ...

    def _init_state(self) -> None:
        self.state["timeStep"] = 0

    def reset(self) -> None:
        self._init_state()

    def get_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "min": p.min_val,
                    "max": p.max_val,
                    "default": p.default,
                    "unit": p.unit,
                }
                for p in self.parameter_defs()
            ],
            "outputs": [
                {"name": o.name, "unit": o.unit, "description": o.description}
                for o in self.output_fields()
            ],
        }

    def generate_dataset(
        self, samples: int, include_anomalies: bool = True
    ) -> list[dict[str, Any]]:
        dataset = []
        for i in range(samples):
            sim = self.__class__()
            is_anomaly = include_anomalies and random.random() < self._anomaly_rate()
            params = self._anomaly_params(i) if is_anomaly else self._normal_params(i)
            sim.parameters.update(params)
            sim.state["timeStep"] = i
            row = sim.step()
            row["anomaly"] = 1 if is_anomaly else 0
            dataset.append(row)
        return dataset

    def _anomaly_rate(self) -> float:
        return 0.05

    @abstractmethod
    def _normal_params(self, index: int) -> dict[str, float]:
        ...

    @abstractmethod
    def _anomaly_params(self, index: int) -> dict[str, float]:
        ...

    @staticmethod
    def _noise(scale: float = 1.0) -> float:
        return (random.random() - 0.5) * 2 * scale

    @staticmethod
    def _gaussian(mean: float = 0.0, std: float = 1.0) -> float:
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
        return z * std + mean

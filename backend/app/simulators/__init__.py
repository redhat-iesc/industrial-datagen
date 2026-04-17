from app.simulators.base import BaseSimulator
from app.simulators.chemical import ChemicalSimulator
from app.simulators.pharma import PharmaSimulator
from app.simulators.pulp import PulpSimulator
from app.simulators.refinery import RefinerySimulator
from app.simulators.rotating import RotatingEquipmentSimulator

SIMULATOR_REGISTRY: dict[str, type[BaseSimulator]] = {
    "refinery": RefinerySimulator,
    "chemical": ChemicalSimulator,
    "pulp": PulpSimulator,
    "pharma": PharmaSimulator,
    "rotating": RotatingEquipmentSimulator,
}


def get_simulator_class(process_type: str) -> type[BaseSimulator] | None:
    return SIMULATOR_REGISTRY.get(process_type)


def list_process_types() -> list[str]:
    return list(SIMULATOR_REGISTRY.keys())

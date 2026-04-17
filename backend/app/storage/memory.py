from app.storage.base import BaseStorage


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self._simulations: dict[str, dict] = {}
        self._simulation_data: dict[str, list[dict]] = {}
        self._datasets: dict[str, dict] = {}
        self._dataset_rows: dict[str, list[dict]] = {}

    async def save_simulation(self, sim_id: str, data: dict) -> None:
        self._simulations[sim_id] = data

    async def get_simulation(self, sim_id: str) -> dict | None:
        return self._simulations.get(sim_id)

    async def list_simulations(self) -> list[dict]:
        return list(self._simulations.values())

    async def delete_simulation(self, sim_id: str) -> bool:
        if sim_id in self._simulations:
            del self._simulations[sim_id]
            self._simulation_data.pop(sim_id, None)
            return True
        return False

    async def append_simulation_data(self, sim_id: str, row: dict) -> None:
        if sim_id not in self._simulation_data:
            self._simulation_data[sim_id] = []
        self._simulation_data[sim_id].append(row)

    async def get_simulation_history(
        self, sim_id: str, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        data = self._simulation_data.get(sim_id, [])
        return data[offset : offset + limit]

    async def get_simulation_latest(self, sim_id: str) -> dict | None:
        data = self._simulation_data.get(sim_id, [])
        return data[-1] if data else None

    async def save_dataset(self, dataset_id: str, data: dict) -> None:
        self._datasets[dataset_id] = data

    async def get_dataset(self, dataset_id: str) -> dict | None:
        return self._datasets.get(dataset_id)

    async def list_datasets(self) -> list[dict]:
        return list(self._datasets.values())

    async def delete_dataset(self, dataset_id: str) -> bool:
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            self._dataset_rows.pop(dataset_id, None)
            return True
        return False

    async def save_dataset_rows(self, dataset_id: str, rows: list[dict]) -> None:
        self._dataset_rows[dataset_id] = rows

    async def get_dataset_rows(self, dataset_id: str) -> list[dict]:
        return self._dataset_rows.get(dataset_id, [])

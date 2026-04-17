from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    async def save_simulation(self, sim_id: str, data: dict) -> None: ...

    @abstractmethod
    async def get_simulation(self, sim_id: str) -> dict | None: ...

    @abstractmethod
    async def list_simulations(self) -> list[dict]: ...

    @abstractmethod
    async def delete_simulation(self, sim_id: str) -> bool: ...

    @abstractmethod
    async def append_simulation_data(self, sim_id: str, row: dict) -> None: ...

    @abstractmethod
    async def get_simulation_history(
        self, sim_id: str, limit: int = 100, offset: int = 0
    ) -> list[dict]: ...

    @abstractmethod
    async def get_simulation_latest(self, sim_id: str) -> dict | None: ...

    @abstractmethod
    async def save_dataset(self, dataset_id: str, data: dict) -> None: ...

    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> dict | None: ...

    @abstractmethod
    async def list_datasets(self) -> list[dict]: ...

    @abstractmethod
    async def delete_dataset(self, dataset_id: str) -> bool: ...

    @abstractmethod
    async def save_dataset_rows(self, dataset_id: str, rows: list[dict]) -> None: ...

    @abstractmethod
    async def get_dataset_rows(self, dataset_id: str) -> list[dict]: ...

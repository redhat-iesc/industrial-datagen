"""Cross-simulator tests validating temporal continuity of dataset generation."""

import pytest

from app.simulators import SIMULATOR_REGISTRY


@pytest.mark.parametrize("process_type", SIMULATOR_REGISTRY.keys())
def test_dataset_timestamps_are_sequential(process_type: str):
    """All simulators must produce sequential (0, 1, 2, ...) timestamps."""
    sim = SIMULATOR_REGISTRY[process_type]()
    dataset = sim.generate_dataset(10)
    timestamps = [r["timestamp"] for r in dataset]
    assert timestamps == list(range(10))


@pytest.mark.parametrize("process_type", SIMULATOR_REGISTRY.keys())
def test_dataset_row_count_matches_samples(process_type: str):
    """Dataset length must equal requested sample count."""
    sim = SIMULATOR_REGISTRY[process_type]()
    for n in [1, 10, 100]:
        dataset = sim.generate_dataset(n)
        assert len(dataset) == n


@pytest.mark.parametrize("process_type", SIMULATOR_REGISTRY.keys())
def test_dataset_rows_have_output_fields(process_type: str):
    """Every row must contain all simulator output fields."""
    sim = SIMULATOR_REGISTRY[process_type]()
    dataset = sim.generate_dataset(5)
    expected = {f.name for f in sim.output_fields()}
    for row in dataset:
        for field in expected:
            assert field in row, f"Row missing field '{field}'"


@pytest.mark.parametrize("process_type", SIMULATOR_REGISTRY.keys())
def test_dataset_anomaly_labels_present(process_type: str):
    """All rows must have an anomaly label when enabled."""
    sim = SIMULATOR_REGISTRY[process_type]()
    dataset = sim.generate_dataset(50, include_anomalies=True)
    for row in dataset:
        assert "anomaly" in row
        assert row["anomaly"] in (0, 1)


class TestDatasetTemporalCorrelation:
    """Tests that only some simulators implement meaningful accumulators."""

    def test_refinery_total_processed_accumulates(self):
        sim = SIMULATOR_REGISTRY["refinery"]()
        dataset = sim.generate_dataset(50)
        for i in range(1, len(dataset)):
            assert dataset[i]["totalProcessed"] >= dataset[i - 1]["totalProcessed"]

    def test_pharma_batch_consistent(self):
        sim = SIMULATOR_REGISTRY["pharma"]()
        dataset = sim.generate_dataset(10)
        batch_nums = {r["batchNumber"] for r in dataset}
        assert len(batch_nums) == 1

    def test_pharma_batch_progress_grows(self):
        sim = SIMULATOR_REGISTRY["pharma"]()
        dataset = sim.generate_dataset(20)
        for i in range(1, len(dataset)):
            assert dataset[i]["batchProgress"] >= dataset[i - 1]["batchProgress"]

    def test_pulp_total_wood_accumulates(self):
        sim = SIMULATOR_REGISTRY["pulp"]()
        dataset = sim.generate_dataset(50)
        for i in range(1, len(dataset)):
            assert dataset[i]["totalWoodProcessed"] >= dataset[i - 1]["totalWoodProcessed"]

    def test_rotating_running_hours_accumulate(self):
        sim = SIMULATOR_REGISTRY["rotating"]()
        dataset = sim.generate_dataset(50)
        for i in range(1, len(dataset)):
            assert dataset[i]["runningHours"] >= dataset[i - 1]["runningHours"]

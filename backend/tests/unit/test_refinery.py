import pytest

from app.simulators.refinery import RefinerySimulator


class TestRefinerySimulator:
    def setup_method(self):
        self.sim = RefinerySimulator()

    def test_default_parameters(self):
        assert self.sim.parameters["crudeTemp"] == 350
        assert self.sim.parameters["pressure"] == 15
        assert self.sim.parameters["feedRate"] == 100
        assert self.sim.parameters["catalystActivity"] == 1.0

    def test_step_returns_all_fields(self):
        result = self.sim.step()
        expected_fields = [
            "timestamp", "crudeInput", "temperature", "pressure",
            "gasolineYield", "dieselYield", "jetFuelYield", "residualYield",
            "gasolineOctane", "dieselCetane", "sulfurContent",
            "efficiency", "yieldEfficiency", "energyConsumption", "energyIntensity",
            "catalystLevel", "totalProcessed",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_step_values_in_valid_ranges(self):
        result = self.sim.step()
        assert 0 < result["gasolineYield"] < 200
        assert 0 < result["dieselYield"] < 200
        assert 0 < result["jetFuelYield"] < 100
        assert 0 < result["residualYield"] < 100
        assert 70 < result["gasolineOctane"] < 100
        assert 30 < result["dieselCetane"] < 65
        assert result["sulfurContent"] >= 0
        assert 0 < result["efficiency"] <= 1.0
        assert result["energyConsumption"] > 0

    def test_temperature_affects_efficiency(self):
        self.sim.parameters["crudeTemp"] = 350
        result_optimal = self.sim.step()

        sim2 = RefinerySimulator({"crudeTemp": 400})
        result_hot = sim2.step()

        assert result_optimal["efficiency"] > result_hot["efficiency"]

    def test_catalyst_degrades_over_time(self):
        results = [self.sim.step() for _ in range(100)]
        assert results[-1]["catalystLevel"] < results[0]["catalystLevel"]

    def test_total_processed_accumulates(self):
        self.sim.step()
        self.sim.step()
        result = self.sim.step()
        assert result["totalProcessed"] == pytest.approx(300, abs=5)

    def test_generate_dataset_count(self):
        dataset = self.sim.generate_dataset(50)
        assert len(dataset) == 50

    def test_generate_dataset_has_anomaly_labels(self):
        dataset = self.sim.generate_dataset(100, include_anomalies=True)
        for row in dataset:
            assert "anomaly" in row
            assert row["anomaly"] in (0, 1)

    def test_generate_dataset_anomaly_rate(self):
        dataset = self.sim.generate_dataset(10000, include_anomalies=True)
        anomaly_count = sum(1 for row in dataset if row["anomaly"] == 1)
        anomaly_rate = anomaly_count / len(dataset)
        assert 0.02 < anomaly_rate < 0.10

    def test_generate_dataset_no_anomalies_when_disabled(self):
        dataset = self.sim.generate_dataset(100, include_anomalies=False)
        anomaly_count = sum(1 for row in dataset if row["anomaly"] == 1)
        assert anomaly_count == 0

    def test_get_schema(self):
        schema = self.sim.get_schema()
        assert schema["name"] == "refinery"
        assert "parameters" in schema
        assert "outputs" in schema
        assert len(schema["parameters"]) == 4

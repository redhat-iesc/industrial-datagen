import pytest

from app.simulators.pulp import PulpSimulator


class TestPulpSimulator:
    def setup_method(self):
        self.sim = PulpSimulator()

    def test_default_parameters(self):
        assert self.sim.parameters["woodInput"] == 50
        assert self.sim.parameters["alkaliConc"] == 10
        assert self.sim.parameters["temperature"] == 165
        assert self.sim.parameters["pressure"] == 8
        assert self.sim.parameters["cookingTime"] == 180
        assert self.sim.parameters["whiteChipRatio"] == 0.95

    def test_step_returns_all_fields(self):
        result = self.sim.step()
        expected_fields = [
            "timestamp", "woodChipInput", "alkaliConcentration", "temperature",
            "pressure", "pH", "pulpYield", "blackLiquor", "blackLiquorSolids",
            "kappaNumber", "brightness", "ligninContent",
            "fiberLength", "fiberStrength", "tearStrength", "burstStrength", "viscosity",
            "hFactor", "delignification", "efficiency",
            "alkaliConsumption", "steamConsumption", "chemicalEfficiency",
            "totalWoodProcessed", "totalPulpProduced",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_step_values_in_valid_ranges(self):
        result = self.sim.step()
        assert 0 < result["pulpYield"] < 100
        assert 0 < result["kappaNumber"] < 120
        assert 0 < result["brightness"] < 110
        assert result["fiberLength"] > 0
        assert result["pH"] > 10

    def test_h_factor_calculation(self):
        result = self.sim.step()
        assert result["hFactor"] > 0

    def test_temperature_affects_delignification(self):
        sim_low = PulpSimulator({"temperature": 150})
        sim_high = PulpSimulator({"temperature": 180})
        r_low = sim_low.step()
        r_high = sim_high.step()
        assert r_high["delignification"] > r_low["delignification"]

    def test_total_wood_accumulates(self):
        self.sim.step()
        self.sim.step()
        result = self.sim.step()
        assert result["totalWoodProcessed"] == pytest.approx(150, abs=5)

    def test_generate_dataset_count(self):
        dataset = self.sim.generate_dataset(50)
        assert len(dataset) == 50

    def test_generate_dataset_anomaly_rate(self):
        dataset = self.sim.generate_dataset(10000, include_anomalies=True)
        anomaly_count = sum(1 for row in dataset if row["anomaly"] == 1)
        anomaly_rate = anomaly_count / len(dataset)
        assert 0.02 < anomaly_rate < 0.10

    def test_get_schema(self):
        schema = self.sim.get_schema()
        assert schema["name"] == "pulp"
        assert len(schema["parameters"]) == 6

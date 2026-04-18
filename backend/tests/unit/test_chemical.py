from app.simulators.chemical import ChemicalSimulator


class TestChemicalSimulator:
    def setup_method(self):
        self.sim = ChemicalSimulator()

    def test_default_parameters(self):
        assert self.sim.parameters["reactantA"] == 100
        assert self.sim.parameters["reactantB"] == 100
        assert self.sim.parameters["temperature"] == 350
        assert self.sim.parameters["pressure"] == 25
        assert self.sim.parameters["catalystConc"] == 1.0
        assert self.sim.parameters["stirringSpeed"] == 300

    def test_step_returns_all_fields(self):
        result = self.sim.step()
        expected_fields = [
            "timestamp", "temperature", "pressure", "stirringSpeed", "pH",
            "reactantAConc", "reactantBConc", "productConc", "byproductConc",
            "conversion", "selectivity", "yield", "spaceTimeYield",
            "catalystActivity", "heatGeneration", "massBalance", "mixingEfficiency",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_step_values_in_valid_ranges(self):
        result = self.sim.step()
        assert 0 <= result["conversion"] <= 1.0
        assert 0 <= result["selectivity"] <= 100
        assert 0 <= result["yield"] <= 100
        assert result["heatGeneration"] >= 0
        assert 50 < result["massBalance"] < 150

    def test_temperature_affects_conversion(self):
        result_optimal = self.sim.step()

        sim2 = ChemicalSimulator({"temperature": 400})
        result_hot = sim2.step()

        assert result_optimal["conversion"] != result_hot["conversion"]

    def test_catalyst_deactivates_over_time(self):
        results = [self.sim.step() for _ in range(100)]
        assert results[-1]["catalystActivity"] < results[0]["catalystActivity"]

    def test_arrhenius_temperature_dependence(self):
        sim_low = ChemicalSimulator({"temperature": 320})
        sim_high = ChemicalSimulator({"temperature": 380})
        r_low = sim_low.step()
        r_high = sim_high.step()
        assert r_low["conversion"] != r_high["conversion"]

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
        assert schema["name"] == "chemical"
        assert len(schema["parameters"]) == 6

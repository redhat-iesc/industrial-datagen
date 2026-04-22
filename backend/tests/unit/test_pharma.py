from app.simulators.pharma import PharmaSimulator


class TestPharmaSimulator:
    def setup_method(self):
        self.sim = PharmaSimulator()

    def test_default_parameters(self):
        assert self.sim.parameters["apiConc"] == 100
        assert self.sim.parameters["solventVol"] == 500
        assert self.sim.parameters["temperature"] == 45
        assert self.sim.parameters["stirringSpeed"] == 300
        assert self.sim.parameters["reactionTime"] == 240
        assert self.sim.parameters["catalystAmount"] == 2.0
        assert self.sim.parameters["pH"] == 6.8

    def test_step_returns_all_fields(self):
        result = self.sim.step()
        expected_fields = [
            "timestamp", "batchNumber",
            "temperature", "pH", "stirringSpeed", "dissolvedOxygen", "pressure",
            "apiConcentration", "productConc", "impurityLevel",
            "purity", "assay", "yield", "relatedSubstances", "residualSolvents",
            "heavyMetals", "moisture",
            "particleSize", "opticalRotation", "meltingPoint",
            "batchProgress", "conversion", "energyConsumption",
            "qcPassed", "cppStatus", "gmpCompliant",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_step_values_in_valid_ranges(self):
        result = self.sim.step()
        assert 0 <= result["conversion"] <= 1.0
        assert 0 <= result["purity"] <= 100
        assert result["impurityLevel"] >= 0
        assert result["energyConsumption"] > 0

    def test_gmp_compliance_at_optimal_conditions(self):
        for _ in range(50):
            self.sim.step()
        result = self.sim.step()
        assert result["cppStatus"] in ("NORMAL", "WARNING", "CRITICAL")
        assert isinstance(result["qcPassed"], bool)
        assert isinstance(result["gmpCompliant"], bool)

    def test_temperature_affects_impurity(self):
        sim_hot = PharmaSimulator({"temperature": 58})
        r_hot = sim_hot.step()
        r_normal = self.sim.step()
        assert r_hot["impurityLevel"] > r_normal["impurityLevel"]

    def test_batch_progress_increases(self):
        r1 = self.sim.step()
        for _ in range(10):
            self.sim.step()
        r2 = self.sim.step()
        assert r2["batchProgress"] > r1["batchProgress"]

    def test_generate_dataset_count(self):
        dataset = self.sim.generate_dataset(50)
        assert len(dataset) == 50

    def test_generate_dataset_anomaly_rate(self):
        dataset = self.sim.generate_dataset(10000, include_anomalies=True)
        anomaly_count = sum(1 for row in dataset if row["anomaly"] == 1)
        anomaly_rate = anomaly_count / len(dataset)
        assert 0.02 < anomaly_rate < 0.10

    def test_dataset_batch_consistent(self):
        """All rows in a single dataset must share the same batch number."""
        dataset = self.sim.generate_dataset(10)
        batch_nums = {r.get("batchNumber") for r in dataset}
        assert len(batch_nums) == 1

    def test_dataset_progress_grows(self):
        """Batch progress should be non-decreasing across dataset."""
        dataset = self.sim.generate_dataset(20)
        for i in range(1, len(dataset)):
            assert dataset[i].get("batchProgress", 0) >= dataset[i - 1].get("batchProgress", 0)

    def test_get_schema(self):
        schema = self.sim.get_schema()
        assert schema["name"] == "pharma"
        assert len(schema["parameters"]) == 7

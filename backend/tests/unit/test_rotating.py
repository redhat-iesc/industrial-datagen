import pytest

from app.simulators.rotating import RotatingEquipmentSimulator


class TestRotatingEquipmentSimulator:
    def setup_method(self):
        self.sim = RotatingEquipmentSimulator()

    def test_default_parameters(self):
        assert self.sim.parameters["nominalRPM"] == 3600
        assert self.sim.parameters["loadPercent"] == 75
        assert self.sim.parameters["ambientTemp"] == 35
        assert self.sim.parameters["bearingAge"] == 0.2
        assert self.sim.parameters["alignmentOffset"] == 0.02
        assert self.sim.parameters["balanceGrade"] == 2.5

    def test_step_returns_all_fields(self):
        result = self.sim.step()
        expected_fields = [
            "timestamp", "rpm",
            "vibrationX", "vibrationY", "vibrationZ", "vibrationOverall",
            "bearingTemp", "motorCurrent", "dischargePressure",
            "wpdBand1Energy", "wpdBand2Energy", "wpdBand3Energy",
            "wpdBand4Energy", "wpdBand5Energy",
            "loadPercent", "ambientTemp",
            "faultType", "maintenanceRequired", "faultSeverity", "runningHours",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_step_values_in_valid_ranges(self):
        result = self.sim.step()
        assert result["rpm"] > 0
        assert result["vibrationX"] >= 0
        assert result["vibrationY"] >= 0
        assert result["vibrationZ"] >= 0
        assert result["vibrationOverall"] >= 0
        assert result["bearingTemp"] > 0
        assert result["motorCurrent"] > 0
        assert result["dischargePressure"] > 0

    def test_fault_injection(self):
        self.sim.inject_fault("bearing_fault")
        assert self.sim.state["activeFault"] == "bearing_fault"
        for _ in range(50):
            self.sim.step()
        result = self.sim.step()
        assert result["faultType"] == "bearing_fault"
        assert result["faultSeverity"] > 0

    def test_load_affects_vibration(self):
        sim_low = RotatingEquipmentSimulator({"loadPercent": 40})
        sim_high = RotatingEquipmentSimulator({"loadPercent": 95})
        results_low = [sim_low.step()["vibrationOverall"] for _ in range(20)]
        results_high = [sim_high.step()["vibrationOverall"] for _ in range(20)]
        avg_low = sum(results_low) / len(results_low)
        avg_high = sum(results_high) / len(results_high)
        assert avg_high > avg_low

    def test_bearing_degrades_over_time(self):
        initial_degradation = self.sim.state["bearingDegradation"]
        for _ in range(100):
            self.sim.step()
        assert self.sim.state["bearingDegradation"] > initial_degradation

    def test_running_hours_accumulate(self):
        for _ in range(60):
            self.sim.step()
        result = self.sim.step()
        assert result["runningHours"] > 0

    def test_maintenance_required_on_severe_fault(self):
        self.sim.inject_fault("bearing_fault")
        self.sim.state["faultProgress"] = 0.5
        result = self.sim.step()
        assert result["maintenanceRequired"] is True

    def test_wpd_bands_present(self):
        result = self.sim.step()
        for i in range(1, 6):
            assert result[f"wpdBand{i}Energy"] >= 0

    def test_generate_dataset_count(self):
        dataset = self.sim.generate_dataset(50)
        assert len(dataset) == 50

    def test_generate_dataset_higher_anomaly_rate(self):
        dataset = self.sim.generate_dataset(10000, include_anomalies=True)
        anomaly_count = sum(1 for row in dataset if row["anomaly"] == 1)
        anomaly_rate = anomaly_count / len(dataset)
        assert 0.15 < anomaly_rate < 0.35

    def test_generate_dataset_fault_types(self):
        dataset = self.sim.generate_dataset(1000, include_anomalies=True)
        fault_types = {row["faultType"] for row in dataset if row["anomaly"] == 1}
        assert "bearing_fault" in fault_types or "rotor_imbalance" in fault_types or "misalignment" in fault_types

    def test_get_schema(self):
        schema = self.sim.get_schema()
        assert schema["name"] == "rotating"
        assert len(schema["parameters"]) == 6

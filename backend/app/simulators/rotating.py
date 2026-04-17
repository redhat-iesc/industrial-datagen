import math
import random

from app.simulators.base import BaseSimulator, OutputField, ParameterDef


class RotatingEquipmentSimulator(BaseSimulator):
    name = "rotating"
    description = "Rotating equipment predictive maintenance simulation"

    NORMAL_VIBRATION = {"x": (2.8, 0.4), "y": (3.2, 0.5), "z": (1.5, 0.3)}
    NORMAL_TEMP = (65, 5)
    NORMAL_CURRENT = (45, 3)
    NOMINAL_PRESSURE = 8.5
    MAX_TEMP = 120
    MAX_VIBRATION = 11.2

    FAULT_PROGRESSION = {
        "bearing_fault": 0.001,
        "rotor_imbalance": 0.0005,
        "misalignment": 0.0008,
    }
    VALID_FAULTS = ["no_fault", "bearing_fault", "rotor_imbalance", "misalignment"]

    def parameter_defs(self) -> list[ParameterDef]:
        return [
            ParameterDef("nominalRPM", 3000, 4000, 3600, "RPM"),
            ParameterDef("loadPercent", 40, 95, 75, "%"),
            ParameterDef("ambientTemp", 20, 50, 35, "°C"),
            ParameterDef("bearingAge", 0.0, 1.0, 0.2, "fraction"),
            ParameterDef("alignmentOffset", 0.0, 0.2, 0.02, "mm"),
            ParameterDef("balanceGrade", 0.5, 8.0, 2.5, "ISO G"),
        ]

    def output_fields(self) -> list[OutputField]:
        return [
            OutputField("timestamp", "step"),
            OutputField("rpm", "RPM"),
            OutputField("vibrationX", "mm/s"),
            OutputField("vibrationY", "mm/s"),
            OutputField("vibrationZ", "mm/s"),
            OutputField("vibrationOverall", "mm/s"),
            OutputField("bearingTemp", "°C"),
            OutputField("motorCurrent", "A"),
            OutputField("dischargePressure", "bar"),
            OutputField("wpdBand1Energy", ""),
            OutputField("wpdBand2Energy", ""),
            OutputField("wpdBand3Energy", ""),
            OutputField("wpdBand4Energy", ""),
            OutputField("wpdBand5Energy", ""),
            OutputField("loadPercent", "%"),
            OutputField("ambientTemp", "°C"),
            OutputField("faultType", ""),
            OutputField("maintenanceRequired", ""),
            OutputField("faultSeverity", ""),
            OutputField("runningHours", "hr"),
        ]

    def _init_state(self) -> None:
        super()._init_state()
        self.state["runningHours"] = 0.0
        self.state["bearingDegradation"] = 0.0
        self.state["activeFault"] = "no_fault"
        self.state["faultProgress"] = 0.0

    def inject_fault(self, fault_type: str) -> None:
        if fault_type not in self.VALID_FAULTS:
            raise ValueError(f"Invalid fault type: {fault_type}. Valid: {self.VALID_FAULTS}")
        self.state["activeFault"] = fault_type
        if fault_type == "no_fault":
            self.state["faultProgress"] = 0.0
        else:
            self.state["faultProgress"] = 0.05

    def _compute_wpd(
        self, vib_x: float, vib_y: float, vib_z: float, fault_type: str
    ) -> dict:
        wpd1 = (vib_x * 0.3 + vib_y * 0.3 + vib_z * 0.4) ** 2 * 0.1
        wpd2 = vib_x**2 * 0.15
        wpd3 = (vib_y * 0.7 + vib_z * 0.3) ** 2 * 0.08
        wpd4 = vib_z**2 * 0.05
        wpd5 = (vib_x**2 + vib_y**2 + vib_z**2) * 0.04

        fp = self.state["faultProgress"]
        if fault_type == "bearing_fault":
            wpd4 *= 1 + fp * 3
            wpd5 *= 1 + fp * 1.5
        elif fault_type == "rotor_imbalance":
            wpd2 *= 1 + fp * 4
            wpd5 *= 1 + fp * 2
        elif fault_type == "misalignment":
            wpd3 *= 1 + fp * 3.5
            wpd1 *= 1 + fp * 1.2
            wpd5 *= 1 + fp * 1.8

        wpd1 += abs(self._gaussian(0, 0.01))
        wpd2 += abs(self._gaussian(0, 0.008))
        wpd3 += abs(self._gaussian(0, 0.006))
        wpd4 += abs(self._gaussian(0, 0.005))
        wpd5 += abs(self._gaussian(0, 0.015))

        return {
            "wpdBand1Energy": round(wpd1, 6),
            "wpdBand2Energy": round(wpd2, 6),
            "wpdBand3Energy": round(wpd3, 6),
            "wpdBand4Energy": round(wpd4, 6),
            "wpdBand5Energy": round(wpd5, 6),
        }

    def step(self) -> dict:
        t = self.state["timeStep"]
        p = self.parameters

        self.state["runningHours"] += 1 / 60

        load = p["loadPercent"] / 100
        age_effect = p["bearingAge"] + self.state["bearingDegradation"]
        fault_type = self.state["activeFault"]
        fp = self.state["faultProgress"]

        rpm_base = p["nominalRPM"] * (0.95 + load * 0.05)
        rpm = rpm_base + self._gaussian(0, 5) + math.sin(t * 0.02) * 10
        if fault_type == "rotor_imbalance":
            rpm += self._gaussian(0, 8 * fp)

        vib_x = self._gaussian(*self.NORMAL_VIBRATION["x"])
        vib_y = self._gaussian(*self.NORMAL_VIBRATION["y"])
        vib_z = self._gaussian(*self.NORMAL_VIBRATION["z"])

        vib_x *= (0.8 + load * 0.4)
        vib_y *= (0.8 + load * 0.4)
        vib_z *= (0.8 + load * 0.3)

        age_factor = 1 + age_effect * 0.3
        vib_x *= age_factor
        vib_y *= age_factor
        vib_z *= age_factor

        if fault_type == "bearing_fault":
            vib_x += self._gaussian(fp * 4.0, fp * 1.5)
            vib_y += self._gaussian(fp * 5.0, fp * 2.0)
            vib_z += self._gaussian(fp * 1.5, fp * 0.5)
            if random.random() < fp * 0.3:
                vib_x += self._gaussian(fp * 8, 2)
                vib_y += self._gaussian(fp * 6, 2)
        elif fault_type == "rotor_imbalance":
            phase = (t * rpm / 60) * 2 * math.pi
            vib_x += fp * 3.5 * math.sin(phase) + self._gaussian(0, fp * 0.5)
            vib_y += fp * 3.5 * math.cos(phase) + self._gaussian(0, fp * 0.5)
            vib_z += fp * 0.8 * math.sin(phase * 0.5) + self._gaussian(0, fp * 0.2)
        elif fault_type == "misalignment":
            phase = (t * rpm / 60) * 2 * math.pi
            vib_x += fp * 2.0 * math.sin(2 * phase) + self._gaussian(0, fp * 0.4)
            vib_y += fp * 2.5 * math.cos(2 * phase) + self._gaussian(0, fp * 0.4)
            vib_z += fp * 4.0 * math.sin(2 * phase) + self._gaussian(0, fp * 1.0)

        vib_x = abs(vib_x)
        vib_y = abs(vib_y)
        vib_z = abs(vib_z)
        vib_overall = math.sqrt(vib_x**2 + vib_y**2 + vib_z**2)

        bearing_temp = self._gaussian(*self.NORMAL_TEMP)
        bearing_temp += load * 15
        bearing_temp += (p["ambientTemp"] - 35) * 0.3
        bearing_temp += math.sin(t * 0.005) * 2
        if fault_type == "bearing_fault":
            bearing_temp += fp * 25
        elif fault_type == "misalignment":
            bearing_temp += fp * 15

        motor_current = self._gaussian(*self.NORMAL_CURRENT)
        motor_current *= (0.6 + load * 0.6)
        if fault_type == "rotor_imbalance":
            motor_current += fp * 5 + self._gaussian(0, fp * 2)
        elif fault_type == "misalignment":
            motor_current += fp * 8
        elif fault_type == "bearing_fault":
            motor_current += fp * 3

        pressure = self.NOMINAL_PRESSURE * (0.85 + load * 0.2)
        pressure += self._gaussian(0, 0.15) + math.sin(t * 0.03) * 0.2
        if fault_type == "rotor_imbalance":
            pressure -= fp * 1.2

        wpd = self._compute_wpd(vib_x, vib_y, vib_z, fault_type)

        maintenance_required = (
            fp > 0.3
            or vib_overall > self.MAX_VIBRATION * 0.8
            or bearing_temp > self.MAX_TEMP * 0.85
        )

        if fault_type != "no_fault":
            rate = self.FAULT_PROGRESSION[fault_type]
            self.state["faultProgress"] = min(1.0, fp + rate * (1 + load))

        self.state["bearingDegradation"] += 0.00002 * load
        self.state["timeStep"] = t + 1

        return {
            "timestamp": t,
            "rpm": round(rpm, 1),
            "vibrationX": round(vib_x, 3),
            "vibrationY": round(vib_y, 3),
            "vibrationZ": round(vib_z, 3),
            "vibrationOverall": round(vib_overall, 3),
            "bearingTemp": round(bearing_temp, 1),
            "motorCurrent": round(motor_current, 2),
            "dischargePressure": round(pressure, 2),
            **wpd,
            "loadPercent": round(p["loadPercent"] + self._gaussian(0, 1), 1),
            "ambientTemp": round(p["ambientTemp"] + self._gaussian(0, 0.5), 1),
            "faultType": fault_type,
            "maintenanceRequired": maintenance_required,
            "faultSeverity": round(self.state["faultProgress"], 4),
            "runningHours": round(self.state["runningHours"], 2),
        }

    def _anomaly_rate(self) -> float:
        return 0.25

    def _normal_params(self, index: int) -> dict:
        return {
            "nominalRPM": 3500 + random.random() * 200,
            "loadPercent": 40 + random.random() * 55,
            "ambientTemp": 25 + random.random() * 20,
            "bearingAge": random.random() * 0.8,
            "alignmentOffset": 0.01 + random.random() * 0.03,
            "balanceGrade": 1.0 + random.random() * 2.5,
        }

    def _anomaly_params(self, index: int) -> dict:
        return {
            "nominalRPM": 3200 + random.random() * 800,
            "loadPercent": 40 + random.random() * 55,
            "ambientTemp": 25 + random.random() * 20,
            "bearingAge": random.random() * 0.8,
            "alignmentOffset": 0.05 + random.random() * 0.15,
            "balanceGrade": 4.0 + random.random() * 4.0,
        }

    def generate_dataset(
        self, samples: int, include_anomalies: bool = True
    ) -> list[dict]:
        fault_types = ["bearing_fault", "rotor_imbalance", "misalignment"]
        dataset = []
        for i in range(samples):
            sim = self.__class__()
            is_anomaly = include_anomalies and random.random() < self._anomaly_rate()
            params = self._anomaly_params(i) if is_anomaly else self._normal_params(i)
            sim.parameters.update(params)
            sim.state["timeStep"] = i

            if is_anomaly:
                fault = fault_types[random.randint(0, len(fault_types) - 1)]
                sim.state["activeFault"] = fault
                sim.state["faultProgress"] = 0.1 + random.random() * 0.8

            row = sim.step()
            row["anomaly"] = 1 if is_anomaly else 0
            dataset.append(row)
        return dataset

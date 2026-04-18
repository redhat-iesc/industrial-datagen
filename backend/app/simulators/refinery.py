import math
import random
from typing import Any

from app.simulators.base import BaseSimulator, OutputField, ParameterDef


class RefinerySimulator(BaseSimulator):
    name = "refinery"
    description = "Crude oil atmospheric distillation simulation"

    def parameter_defs(self) -> list[ParameterDef]:
        return [
            ParameterDef("crudeTemp", 320, 500, 350, "°C"),
            ParameterDef("pressure", 12, 20, 15, "bar"),
            ParameterDef("feedRate", 80, 160, 100, "bbl/hr"),
            ParameterDef("catalystActivity", 0.0, 1.0, 1.0, "fraction"),
        ]

    def output_fields(self) -> list[OutputField]:
        return [
            OutputField("timestamp", "step"),
            OutputField("crudeInput", "bbl/hr"),
            OutputField("temperature", "°C"),
            OutputField("pressure", "bar"),
            OutputField("gasolineYield", "bbl"),
            OutputField("dieselYield", "bbl"),
            OutputField("jetFuelYield", "bbl"),
            OutputField("residualYield", "bbl"),
            OutputField("gasolineOctane", "RON"),
            OutputField("dieselCetane", "cetane"),
            OutputField("sulfurContent", "%"),
            OutputField("efficiency", "fraction"),
            OutputField("yieldEfficiency", "%"),
            OutputField("energyConsumption", "kWh"),
            OutputField("energyIntensity", "kWh/bbl"),
            OutputField("catalystLevel", "fraction"),
            OutputField("totalProcessed", "bbl"),
        ]

    def _init_state(self) -> None:
        super()._init_state()
        self.state["totalProcessed"] = 0.0
        self.state["catalystDegradation"] = 0.0

    def step(self) -> dict[str, Any]:
        t = self.state["timeStep"]
        p = self.parameters

        temperature = p["crudeTemp"] + self._noise(2)
        pressure = p["pressure"] + self._noise(0.3)
        feed_rate = p["feedRate"] + self._noise(1)

        catalyst_activity = max(0, p["catalystActivity"] - self.state["catalystDegradation"])

        temp_delta = abs(temperature - 350)
        temp_efficiency = math.exp(-(temp_delta**2) / 1000)

        pressure_delta = abs(pressure - 15)
        pressure_efficiency = max(0.7, 1 - pressure_delta * 0.05)

        overall_efficiency = 0.85 * temp_efficiency * pressure_efficiency * catalyst_activity

        gasoline_yield = feed_rate * overall_efficiency * 0.45 + self._noise(0.5)
        diesel_yield = feed_rate * overall_efficiency * 0.35 + self._noise(0.3)
        jet_fuel_yield = feed_rate * overall_efficiency * 0.12 + self._noise(0.2)
        residual_yield = feed_rate * 0.15 + self._noise(0.15)

        total_yield = gasoline_yield + diesel_yield + jet_fuel_yield
        yield_efficiency = (total_yield / max(feed_rate, 0.1)) * 100

        gasoline_octane = 87 + temp_efficiency * 5 + self._noise(2)
        diesel_cetane = 45 + pressure_efficiency * 8 + self._noise(3)
        sulfur_content = max(0, (1 - catalyst_activity) * 0.5 + self._noise(0.1))

        energy_consumption = feed_rate * 12.5 * (1 / max(0.5, overall_efficiency))
        energy_intensity = energy_consumption / max(feed_rate, 0.1)

        self.state["totalProcessed"] += feed_rate
        self.state["catalystDegradation"] = min(1.0, self.state["catalystDegradation"] + 0.0001)
        self.state["timeStep"] = t + 1

        return {
            "timestamp": t,
            "crudeInput": round(feed_rate, 2),
            "temperature": round(temperature, 2),
            "pressure": round(pressure, 2),
            "gasolineYield": round(max(0, gasoline_yield), 2),
            "dieselYield": round(max(0, diesel_yield), 2),
            "jetFuelYield": round(max(0, jet_fuel_yield), 2),
            "residualYield": round(max(0, residual_yield), 2),
            "gasolineOctane": round(gasoline_octane, 2),
            "dieselCetane": round(diesel_cetane, 2),
            "sulfurContent": round(sulfur_content, 4),
            "efficiency": round(overall_efficiency, 4),
            "yieldEfficiency": round(yield_efficiency, 2),
            "energyConsumption": round(energy_consumption, 2),
            "energyIntensity": round(energy_intensity, 2),
            "catalystLevel": round(catalyst_activity, 4),
            "totalProcessed": round(self.state["totalProcessed"], 2),
        }

    def _normal_params(self, index: int) -> dict[str, float]:
        return {
            "crudeTemp": 345 + random.random() * 10,
            "pressure": 14 + random.random() * 2,
            "feedRate": 95 + random.random() * 10,
            "catalystActivity": max(0, 1.0 - index * 0.00001),
        }

    def _anomaly_params(self, index: int) -> dict[str, float]:
        return {
            "crudeTemp": 320 + random.random() * 80,
            "pressure": 12 + random.random() * 8,
            "feedRate": 80 + random.random() * 60,
            "catalystActivity": max(0, 1.0 - index * 0.00001),
        }

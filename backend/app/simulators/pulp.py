import math
import random
from typing import Any

from app.simulators.base import BaseSimulator, OutputField, ParameterDef


class PulpSimulator(BaseSimulator):
    name = "pulp"
    description = "Kraft pulping digester simulation"

    ACTIVATION_ENERGY = 134  # kJ/mol for lignin degradation
    GAS_CONSTANT = 8.314
    REF_TEMP = 100  # °C
    TARGET_LIGNIN_REMOVAL = 0.88
    TARGET_H_FACTOR = 1200
    OPTIMAL_TEMP = 165
    OPTIMAL_ALKALI = 10
    TARGET_BRIGHTNESS = 90
    BASE_YIELD = 0.48

    def parameter_defs(self) -> list[ParameterDef]:
        return [
            ParameterDef("woodInput", 35, 70, 50, "tons/hr"),
            ParameterDef("alkaliConc", 6, 14, 10, "%"),
            ParameterDef("temperature", 145, 185, 165, "°C"),
            ParameterDef("pressure", 5, 11, 8, "bar"),
            ParameterDef("cookingTime", 120, 240, 180, "min"),
            ParameterDef("whiteChipRatio", 0.85, 1.0, 0.95, "fraction"),
        ]

    def output_fields(self) -> list[OutputField]:
        return [
            OutputField("timestamp", "step"),
            OutputField("woodChipInput", "tons/hr"),
            OutputField("alkaliConcentration", "%"),
            OutputField("temperature", "°C"),
            OutputField("pressure", "bar"),
            OutputField("pH", ""),
            OutputField("pulpYield", "tons/hr"),
            OutputField("blackLiquor", "tons"),
            OutputField("blackLiquorSolids", "tons"),
            OutputField("kappaNumber", ""),
            OutputField("brightness", "ISO"),
            OutputField("ligninContent", "%"),
            OutputField("fiberLength", "mm"),
            OutputField("fiberStrength", ""),
            OutputField("tearStrength", "mN·m²/g"),
            OutputField("burstStrength", "kPa·m²/g"),
            OutputField("viscosity", "mPa·s"),
            OutputField("hFactor", ""),
            OutputField("delignification", "%"),
            OutputField("efficiency", "%"),
            OutputField("alkaliConsumption", "tons/hr"),
            OutputField("steamConsumption", "GJ/hr"),
            OutputField("chemicalEfficiency", "%"),
            OutputField("totalWoodProcessed", "tons"),
            OutputField("totalPulpProduced", "tons"),
        ]

    def _init_state(self) -> None:
        super()._init_state()
        self.state["totalWoodProcessed"] = 0.0
        self.state["totalPulpProduced"] = 0.0
        self.state["chemicalConsumption"] = 0.0

    def _calculate_h_factor(self, temperature: float, cooking_time: float) -> float:
        factor = math.exp(
            (self.ACTIVATION_ENERGY * 1000 / self.GAS_CONSTANT)
            * (1 / (self.REF_TEMP + 273.15) - 1 / (temperature + 273.15))
        )
        return factor * cooking_time / 60

    def _calculate_delignification(self, h_factor: float, alkali_conc: float) -> float:
        h_factor_effect = min(1, h_factor / self.TARGET_H_FACTOR)
        alkali_effect = min(1, alkali_conc / self.OPTIMAL_ALKALI)
        return self.TARGET_LIGNIN_REMOVAL * h_factor_effect * alkali_effect

    def step(self) -> dict[str, Any]:
        t = self.state["timeStep"]
        p = self.parameters

        wood_variation = self._noise(p["woodInput"] * 0.025)
        wood_input = p["woodInput"] + wood_variation

        heating_profile = min(1, t * 0.02)
        temp_noise = math.sin(t * 0.08) * 2 + self._noise(0.75)
        temperature = p["temperature"] * heating_profile + temp_noise

        pressure_noise = self._noise(0.15)
        pressure = p["pressure"] + pressure_noise + (temperature - self.OPTIMAL_TEMP) * 0.05

        alkali_depletion = t * 0.005
        alkali_conc = max(0, p["alkaliConc"] - alkali_depletion + self._noise(0.05))

        h_factor = self._calculate_h_factor(p["temperature"], p["cookingTime"])

        delignification = self._calculate_delignification(h_factor, alkali_conc)
        lignin_removal = delignification + self._noise(0.015)

        yield_factor = 1 - (lignin_removal - self.TARGET_LIGNIN_REMOVAL) * 0.5
        pulp_yield = (
            wood_input * self.BASE_YIELD * max(0.8, min(1.2, yield_factor))
            + random.random() * 0.5
        )

        kappa_number = (1 - lignin_removal) * 100 + random.random() * 2

        brightness = self.TARGET_BRIGHTNESS * lignin_removal + random.random() * 2

        fiber_length = 2.5 + (temperature - self.OPTIMAL_TEMP) * 0.01 + random.random() * 0.3
        fiber_strength = 80 + lignin_removal * 15 + random.random() * 5

        ph = 13.5 - alkali_depletion * 0.1 + random.random() * 0.15

        alkali_consumption = wood_input * 0.15 * (1 + (temperature - 165) * 0.005)
        steam_consumption = wood_input * 1.8 + (temperature - 165) * 0.5

        black_liquor = wood_input * 4.5
        black_liquor_solids = black_liquor * 0.15

        tear_strength = 8.5 + fiber_length * 0.8 + random.random() * 1.2
        burst_strength = 4.5 + fiber_strength * 0.03 + random.random() * 0.5

        viscosity = 25 + (1 - lignin_removal) * 10 + random.random() * 2

        self.state["totalWoodProcessed"] += wood_input
        self.state["totalPulpProduced"] += pulp_yield
        self.state["chemicalConsumption"] += alkali_consumption

        efficiency = (pulp_yield / wood_input) * 100
        chemical_efficiency = lignin_removal / (alkali_consumption / wood_input) * 100

        self.state["timeStep"] = t + 1

        return {
            "timestamp": t,
            "woodChipInput": round(wood_input, 2),
            "alkaliConcentration": round(alkali_conc, 2),
            "temperature": round(temperature, 2),
            "pressure": round(pressure, 2),
            "pH": round(ph, 2),
            "pulpYield": round(pulp_yield, 2),
            "blackLiquor": round(black_liquor, 2),
            "blackLiquorSolids": round(black_liquor_solids, 2),
            "kappaNumber": round(kappa_number, 1),
            "brightness": round(brightness, 1),
            "ligninContent": round((1 - lignin_removal) * 100, 2),
            "fiberLength": round(fiber_length, 2),
            "fiberStrength": round(fiber_strength, 1),
            "tearStrength": round(tear_strength, 2),
            "burstStrength": round(burst_strength, 2),
            "viscosity": round(viscosity, 1),
            "hFactor": round(h_factor),
            "delignification": round(lignin_removal * 100, 2),
            "efficiency": round(efficiency, 2),
            "alkaliConsumption": round(alkali_consumption, 2),
            "steamConsumption": round(steam_consumption, 2),
            "chemicalEfficiency": round(chemical_efficiency, 2),
            "totalWoodProcessed": round(self.state["totalWoodProcessed"], 2),
            "totalPulpProduced": round(self.state["totalPulpProduced"], 2),
        }

    def _normal_params(self, index: int) -> dict[str, float]:
        return {
            "woodInput": 47 + random.random() * 6,
            "alkaliConc": 9 + random.random() * 2,
            "temperature": 160 + random.random() * 10,
            "pressure": 7 + random.random() * 2,
            "cookingTime": 180 + index * 0.1,
            "whiteChipRatio": 0.93 + random.random() * 0.05,
        }

    def _anomaly_params(self, index: int) -> dict[str, float]:
        return {
            "woodInput": 35 + random.random() * 35,
            "alkaliConc": 6 + random.random() * 8,
            "temperature": 145 + random.random() * 40,
            "pressure": 5 + random.random() * 6,
            "cookingTime": 180 + index * 0.1,
            "whiteChipRatio": 0.93 + random.random() * 0.05,
        }

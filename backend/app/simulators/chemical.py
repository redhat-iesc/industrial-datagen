import math
import random

from app.simulators.base import BaseSimulator, OutputField, ParameterDef


class ChemicalSimulator(BaseSimulator):
    name = "chemical"
    description = "Continuous stirred-tank reactor (CSTR) simulation"

    ACTIVATION_ENERGY = 75000  # J/mol
    GAS_CONSTANT = 8.314  # J/(mol·K)
    PRE_EXPONENTIAL = 1e10
    HEAT_OF_REACTION = -75  # kJ/mol (exothermic)
    RESIDENCE_TIME = 2.5  # hours

    def parameter_defs(self) -> list[ParameterDef]:
        return [
            ParameterDef("reactantA", 80, 180, 100, "mol/L"),
            ParameterDef("reactantB", 80, 180, 100, "mol/L"),
            ParameterDef("temperature", 320, 400, 350, "°C"),
            ParameterDef("pressure", 15, 35, 25, "bar"),
            ParameterDef("catalystConc", 0.0, 2.0, 1.0, "mol/L"),
            ParameterDef("stirringSpeed", 150, 500, 300, "RPM"),
        ]

    def output_fields(self) -> list[OutputField]:
        return [
            OutputField("timestamp", "step"),
            OutputField("temperature", "°C"),
            OutputField("pressure", "bar"),
            OutputField("stirringSpeed", "RPM"),
            OutputField("pH", ""),
            OutputField("reactantAConc", "mol/L"),
            OutputField("reactantBConc", "mol/L"),
            OutputField("productConc", "mol/L"),
            OutputField("byproductConc", "mol/L"),
            OutputField("conversion", "fraction"),
            OutputField("selectivity", "%"),
            OutputField("yield", "%"),
            OutputField("spaceTimeYield", "mol/L/hr"),
            OutputField("catalystActivity", "mol/L"),
            OutputField("heatGeneration", "kW"),
            OutputField("massBalance", "%"),
            OutputField("mixingEfficiency", "fraction"),
        ]

    def _init_state(self) -> None:
        super()._init_state()
        self.state["totalConversion"] = 0.0
        self.state["catalystDeactivation"] = 0.0

    def step(self) -> dict:
        t = self.state["timeStep"]
        p = self.parameters

        temperature = p["temperature"] + self._noise(1)
        pressure = p["pressure"] + self._noise(0.5)
        stirring_speed = p["stirringSpeed"] + self._noise(5)

        catalyst_activity = max(0, p["catalystConc"] - self.state["catalystDeactivation"])

        temp_delta = abs(temperature - 350)
        temp_efficiency = math.exp(-(temp_delta**2) / 800)

        if stirring_speed < 100:
            mixing_eff = 0.6
        elif stirring_speed > 500:
            mixing_eff = 0.8
        else:
            speed_delta = abs(stirring_speed - 300)
            mixing_eff = max(0.7, 1 - speed_delta * 0.001)

        base_conversion = 0.92
        conversion_rate = (
            base_conversion * temp_efficiency * (pressure / 25)
            * catalyst_activity * mixing_eff
        )

        reactant_a_conc = p["reactantA"] * (1 - conversion_rate) + self._noise(0.4)
        reactant_b_conc = p["reactantB"] * (1 - conversion_rate) + self._noise(0.4)
        product_conc = p["reactantA"] * conversion_rate * (1 + self._noise(0.025))

        byproduct_rate = (1 - temp_efficiency) * 0.08
        byproduct_conc = max(0, p["reactantA"] * byproduct_rate + self._noise(0.075))

        selectivity = (product_conc / max(product_conc + byproduct_conc, 0.01)) * 100
        yield_val = conversion_rate * selectivity / 100 * 100
        space_time_yield = product_conc / self.RESIDENCE_TIME

        heat_generation = abs(self.HEAT_OF_REACTION) * product_conc * 0.1

        total_mass_in = p["reactantA"] + p["reactantB"]
        total_mass_out = reactant_a_conc + reactant_b_conc + product_conc + byproduct_conc
        mass_balance = (total_mass_out / max(total_mass_in, 0.01)) * 100

        ph = 7.0 + (temperature - 350) * 0.01 + self._noise(0.15)

        self.state["totalConversion"] += conversion_rate
        self.state["catalystDeactivation"] = min(
            p["catalystConc"], self.state["catalystDeactivation"] + 0.0002
        )
        self.state["timeStep"] = t + 1

        return {
            "timestamp": t,
            "temperature": round(temperature, 2),
            "pressure": round(pressure, 2),
            "stirringSpeed": round(stirring_speed, 2),
            "pH": round(ph, 2),
            "reactantAConc": round(max(0, reactant_a_conc), 2),
            "reactantBConc": round(max(0, reactant_b_conc), 2),
            "productConc": round(max(0, product_conc), 2),
            "byproductConc": round(byproduct_conc, 2),
            "conversion": round(min(1.0, max(0, conversion_rate)), 4),
            "selectivity": round(min(100, max(0, selectivity)), 2),
            "yield": round(min(100, max(0, yield_val)), 2),
            "spaceTimeYield": round(max(0, space_time_yield), 2),
            "catalystActivity": round(catalyst_activity, 4),
            "heatGeneration": round(max(0, heat_generation), 2),
            "massBalance": round(mass_balance, 2),
            "mixingEfficiency": round(mixing_eff, 4),
        }

    def _normal_params(self, index: int) -> dict:
        return {
            "reactantA": 95 + random.random() * 10,
            "reactantB": 95 + random.random() * 10,
            "temperature": 345 + random.random() * 10,
            "pressure": 23 + random.random() * 4,
            "catalystConc": max(0, 1.0 - index * 0.00001),
            "stirringSpeed": 280 + random.random() * 40,
        }

    def _anomaly_params(self, index: int) -> dict:
        return {
            "reactantA": 80 + random.random() * 80,
            "reactantB": 80 + random.random() * 80,
            "temperature": 320 + random.random() * 80,
            "pressure": 15 + random.random() * 20,
            "catalystConc": max(0, 1.0 - index * 0.00001),
            "stirringSpeed": 150 + random.random() * 350,
        }

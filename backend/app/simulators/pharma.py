import math
import random

from app.simulators.base import BaseSimulator, OutputField, ParameterDef


class PharmaSimulator(BaseSimulator):
    name = "pharma"
    description = "GMP-compliant pharmaceutical batch reactor simulation"

    OPTIMAL_TEMP = 45
    OPTIMAL_PH = 6.8
    TARGET_PURITY = 99.5
    TARGET_YIELD = 94
    MAX_IMPURITIES = 0.5
    MAX_CONVERSION = 0.94
    RATE_CONSTANT = 0.015  # min^-1

    CQA_LIMITS = {
        "purity": {"min": 99.0, "max": 100.0},
        "assay": {"min": 98.0, "max": 102.0},
        "relatedSubstances": {"max": 0.5},
        "residualSolvents": {"max": 0.05},
        "heavyMetals": {"max": 10},
    }

    def parameter_defs(self) -> list[ParameterDef]:
        return [
            ParameterDef("apiConc", 80, 130, 100, "g/L"),
            ParameterDef("solventVol", 300, 700, 500, "L"),
            ParameterDef("temperature", 35, 60, 45, "°C"),
            ParameterDef("stirringSpeed", 200, 450, 300, "RPM"),
            ParameterDef("reactionTime", 120, 360, 240, "min"),
            ParameterDef("catalystAmount", 1.0, 4.0, 2.0, "g"),
            ParameterDef("pH", 5.5, 8.5, 6.8, ""),
        ]

    def output_fields(self) -> list[OutputField]:
        return [
            OutputField("timestamp", "step"),
            OutputField("batchNumber", ""),
            OutputField("temperature", "°C"),
            OutputField("pH", ""),
            OutputField("stirringSpeed", "RPM"),
            OutputField("dissolvedOxygen", "mg/L"),
            OutputField("pressure", "bar"),
            OutputField("apiConcentration", "g/L"),
            OutputField("productConc", "g/L"),
            OutputField("impurityLevel", "%"),
            OutputField("purity", "%"),
            OutputField("assay", "%"),
            OutputField("yield", "%"),
            OutputField("relatedSubstances", "%"),
            OutputField("residualSolvents", "%"),
            OutputField("heavyMetals", "ppm"),
            OutputField("moisture", "%"),
            OutputField("particleSize", "μm"),
            OutputField("opticalRotation", "°"),
            OutputField("meltingPoint", "°C"),
            OutputField("batchProgress", "%"),
            OutputField("conversion", "fraction"),
            OutputField("energyConsumption", "kW"),
            OutputField("qcPassed", ""),
            OutputField("cppStatus", ""),
            OutputField("gmpCompliant", ""),
        ]

    def _init_state(self) -> None:
        super()._init_state()
        self.state["batchNumber"] = f"BATCH-{random.randint(100000, 999999)}"
        self.state["reactionProgress"] = 0.0

    def _calculate_kinetics(self, temperature: float, ph: float, time: float) -> float:
        temp_effect = math.exp(-((temperature - self.OPTIMAL_TEMP) ** 2) / 50)
        ph_effect = math.exp(-((ph - self.OPTIMAL_PH) ** 2) / 2)
        conversion = self.MAX_CONVERSION * (1 - math.exp(-self.RATE_CONSTANT * time))
        return conversion * temp_effect * ph_effect

    def _calculate_impurities(
        self, temperature: float, ph: float, stirring_speed: float
    ) -> float:
        temp_stress = abs(temperature - self.OPTIMAL_TEMP)
        ph_stress = abs(ph - self.OPTIMAL_PH)
        mixing_stress = max(0, (stirring_speed - 400) * 0.001)
        base_impurity = 0.1
        return min(5.0, base_impurity + temp_stress * 0.015 + ph_stress * 0.02 + mixing_stress)

    def _check_qc(
        self,
        purity: float,
        assay: float,
        impurity: float,
        solvents: float,
        metals: float,
    ) -> bool:
        return (
            purity >= self.CQA_LIMITS["purity"]["min"]
            and self.CQA_LIMITS["assay"]["min"] <= assay <= self.CQA_LIMITS["assay"]["max"]
            and impurity <= self.CQA_LIMITS["relatedSubstances"]["max"]
            and solvents <= self.CQA_LIMITS["residualSolvents"]["max"]
            and metals <= self.CQA_LIMITS["heavyMetals"]["max"]
        )

    def _monitor_cpp(
        self, temperature: float, ph: float, stirring_speed: float
    ) -> str:
        temp_delta = abs(temperature - self.OPTIMAL_TEMP)
        ph_delta = abs(ph - self.OPTIMAL_PH)
        stirring_in_range = 250 < stirring_speed < 350

        if temp_delta < 5 and ph_delta < 0.5 and stirring_in_range:
            return "NORMAL"
        elif temp_delta > 10 or ph_delta > 1.0:
            return "CRITICAL"
        else:
            return "WARNING"

    def step(self) -> dict:
        t = self.state["timeStep"]
        p = self.parameters

        progress = min(1, t / (p["reactionTime"] * 2))
        self.state["reactionProgress"] = progress

        temp_noise = math.sin(t * 0.12) * 0.5 + self._noise(0.2)
        temperature = p["temperature"] + temp_noise

        ph_drift = -0.002 * t
        ph_noise = self._noise(0.075)
        ph = max(4.0, min(9.0, p["pH"] + ph_drift + ph_noise))

        stirring_noise = self._noise(7.5)
        stirring_speed = p["stirringSpeed"] + stirring_noise

        conversion = self._calculate_kinetics(temperature, ph, t * 0.5)

        api_conc = p["apiConc"] * (1 - conversion) + self._noise(0.4)
        product_conc = p["apiConc"] * conversion + random.random() * 0.5

        impurity_level = self._calculate_impurities(temperature, ph, stirring_speed)
        related_substances = impurity_level * 0.1 + random.random() * 0.05

        total_substances = product_conc + impurity_level + related_substances
        purity = min(100, (product_conc / total_substances) * 100)

        theoretical_yield = p["apiConc"] * p["solventVol"]
        actual_yield = product_conc * p["solventVol"]
        yield_percent = (actual_yield / theoretical_yield) * 100

        assay = 100 + (conversion - 0.94) * 10 + self._noise(0.75)

        dissolved_oxygen = 7.5 + stirring_speed * 0.005 + self._noise(0.3)

        residual_solvents = max(
            0, 0.3 - progress * 0.25 - (temperature - 45) * 0.005 + random.random() * 0.02
        )
        heavy_metals = p["catalystAmount"] * 0.5 + random.random() * 2
        moisture = max(0, 0.5 - progress * 0.4 + random.random() * 0.1)

        particle_size = 50 + progress * 30 + random.random() * 10
        optical_rotation = -25 + (purity - 99.5) * 0.5 + random.random() * 1.5
        melting_point = 178 + (purity - 99.5) * 0.8 + random.random() * 1.2

        qc_passed = self._check_qc(purity, assay, impurity_level, residual_solvents, heavy_metals)
        cpp_status = self._monitor_cpp(temperature, ph, stirring_speed)
        gmp_compliant = qc_passed and cpp_status == "NORMAL"

        heating_power = (temperature - 25) * 0.5
        stirring_power = stirring_speed * 0.002
        energy_consumption = heating_power + stirring_power

        pressure = 1.0 + random.random() * 0.05

        self.state["timeStep"] = t + 1

        return {
            "timestamp": t,
            "batchNumber": self.state["batchNumber"],
            "temperature": round(temperature, 2),
            "pH": round(ph, 2),
            "stirringSpeed": round(stirring_speed),
            "dissolvedOxygen": round(dissolved_oxygen, 2),
            "pressure": round(pressure, 3),
            "apiConcentration": round(max(0, api_conc), 2),
            "productConc": round(product_conc, 2),
            "impurityLevel": round(impurity_level, 3),
            "purity": round(purity, 3),
            "assay": round(assay, 2),
            "yield": round(yield_percent, 2),
            "relatedSubstances": round(related_substances, 3),
            "residualSolvents": round(residual_solvents, 4),
            "heavyMetals": round(heavy_metals, 2),
            "moisture": round(moisture, 3),
            "particleSize": round(particle_size, 1),
            "opticalRotation": round(optical_rotation, 2),
            "meltingPoint": round(melting_point, 2),
            "batchProgress": round(progress * 100, 1),
            "conversion": round(conversion, 4),
            "energyConsumption": round(energy_consumption, 2),
            "qcPassed": qc_passed,
            "cppStatus": cpp_status,
            "gmpCompliant": gmp_compliant,
        }

    def _normal_params(self, index: int) -> dict:
        return {
            "apiConc": 98 + random.random() * 4,
            "solventVol": 500,
            "temperature": 43 + random.random() * 4,
            "stirringSpeed": 285 + random.random() * 30,
            "reactionTime": 240,
            "catalystAmount": 2 + random.random() * 0.5,
            "pH": 6.6 + random.random() * 0.4,
        }

    def _anomaly_params(self, index: int) -> dict:
        return {
            "apiConc": 80 + random.random() * 50,
            "solventVol": 500,
            "temperature": 35 + random.random() * 25,
            "stirringSpeed": 200 + random.random() * 250,
            "reactionTime": 240,
            "catalystAmount": 2 + random.random() * 0.5,
            "pH": 5.5 + random.random() * 3,
        }

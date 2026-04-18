import type { DataPoint } from '../types';
import { BaseSimulator } from './base';

export class ChemicalSimulator extends BaseSimulator {
  constructor() {
    super({ reactantA: 2.0, reactantB: 1.5, temperature: 350, pressure: 10, catalystConc: 0.05, flowRate: 100 });
    this.state = { catalystActivity: 1.0 };
  }

  step(): DataPoint {
    const p = this.parameters;
    const t = this.timeStep++;
    const activity = Math.max(0.1, (this.state.catalystActivity ?? 1.0) - 0.0002);
    this.state.catalystActivity = activity;

    const k = 0.1 * Math.exp(-5000 * (1 / (p.temperature + 273.15) - 1 / 623.15)) * activity;
    const conversion = Math.min(0.98, k * p.reactantA * p.catalystConc * 10);
    const selectivity = 0.95 * Math.exp(-((p.temperature - 350) ** 2) / 2000);

    return {
      timestamp: t,
      temperature: +this.noise(p.temperature, 0.01).toFixed(1),
      pressure: +this.noise(p.pressure, 0.02).toFixed(2),
      reactantAConc: +this.noise(p.reactantA * (1 - conversion), 0.02).toFixed(3),
      reactantBConc: +this.noise(p.reactantB * (1 - conversion * 0.8), 0.02).toFixed(3),
      productConc: +this.noise(p.reactantA * conversion * selectivity, 0.02).toFixed(3),
      conversion: +(conversion * 100).toFixed(1),
      selectivity: +(selectivity * 100).toFixed(1),
      catalystActivity: +(activity * 100).toFixed(1),
      heatDuty: +this.noise(75 * conversion * p.flowRate / 100, 0.03).toFixed(1),
      byproduct: +this.noise(p.reactantA * conversion * (1 - selectivity), 0.05).toFixed(4),
    };
  }
}

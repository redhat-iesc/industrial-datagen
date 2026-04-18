import type { DataPoint } from '../types';
import { BaseSimulator } from './base';

export class RefinerySimulator extends BaseSimulator {
  constructor() {
    super({ crudeTemp: 350, pressure: 2.5, feedRate: 1000, catalystActivity: 0.95 });
    this.state = { catalystLevel: 0.95 };
  }

  step(): DataPoint {
    const p = this.parameters;
    const t = this.timeStep++;
    const catalyst = Math.max(0.1, (this.state.catalystLevel ?? 0.95) - 0.0001);
    this.state.catalystLevel = catalyst;

    const tempDelta = p.crudeTemp - 350;
    const efficiency = Math.exp(-(tempDelta * tempDelta) / 1000) * catalyst;
    const temperature = this.noise(p.crudeTemp, 0.02);
    const pressure = this.noise(p.pressure, 0.03);
    const feedRate = this.noise(p.feedRate, 0.01);

    const gasolineYield = this.noise(0.35 * efficiency * feedRate, 0.02);
    const dieselYield = this.noise(0.28 * efficiency * feedRate, 0.02);
    const keroseneYield = this.noise(0.15 * efficiency * feedRate, 0.02);
    const residualYield = this.noise(0.22 * (1 - efficiency * 0.5) * feedRate, 0.03);

    return {
      timestamp: t,
      temperature: +temperature.toFixed(1),
      pressure: +pressure.toFixed(2),
      feedRate: +feedRate.toFixed(1),
      gasolineYield: +gasolineYield.toFixed(1),
      dieselYield: +dieselYield.toFixed(1),
      keroseneYield: +keroseneYield.toFixed(1),
      residualYield: +residualYield.toFixed(1),
      efficiency: +(efficiency * 100).toFixed(1),
      energyConsumption: +this.noise(450 * feedRate / 1000, 0.03).toFixed(1),
      catalystLevel: +catalyst.toFixed(4),
    };
  }
}

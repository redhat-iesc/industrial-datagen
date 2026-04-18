import type { DataPoint } from '../types';
import { BaseSimulator } from './base';

export class PulpSimulator extends BaseSimulator {
  constructor() {
    super({ woodInput: 100, alkaliConc: 15, temperature: 170, pressure: 8, cookingTime: 120, sulfidity: 30 });
  }

  step(): DataPoint {
    const p = this.parameters;
    const t = this.timeStep++;

    const hFactor = Math.exp(43200 * (1 / 443.15 - 1 / (p.temperature + 273.15))) * p.cookingTime / 60;
    const delignification = Math.min(0.95, 0.5 * (1 - Math.exp(-0.01 * hFactor)));
    const pulpYield = 45 + 10 * (1 - delignification);
    const kappa = 80 * (1 - delignification) + 10;

    return {
      timestamp: t,
      temperature: +this.noise(p.temperature, 0.01).toFixed(1),
      pressure: +this.noise(p.pressure, 0.02).toFixed(2),
      woodChipInput: +this.noise(p.woodInput, 0.01).toFixed(1),
      alkaliConcentration: +this.noise(p.alkaliConc, 0.02).toFixed(2),
      hFactor: +hFactor.toFixed(1),
      delignification: +(delignification * 100).toFixed(1),
      pulpYield: +this.noise(pulpYield, 0.02).toFixed(1),
      kappaNumber: +this.noise(kappa, 0.03).toFixed(1),
      brightness: +this.noise(30 + 20 * delignification, 0.02).toFixed(1),
      fiberLength: +this.noise(2.5, 0.05).toFixed(2),
    };
  }
}

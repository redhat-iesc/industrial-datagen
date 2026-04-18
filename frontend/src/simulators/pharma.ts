import type { DataPoint } from '../types';
import { BaseSimulator } from './base';

export class PharmaSimulator extends BaseSimulator {
  constructor() {
    super({ apiConc: 50, solventVol: 500, temperature: 37, stirringSpeed: 200, reactionTime: 120, pH: 7.0, dissolvedO2: 6.0 });
  }

  step(): DataPoint {
    const p = this.parameters;
    const t = this.timeStep++;

    const tempEffect = Math.exp(-((p.temperature - 37) ** 2) / 50);
    const phEffect = Math.exp(-((p.pH - 7.0) ** 2) / 2);
    const conversion = 0.95 * (1 - Math.exp(-0.02 * p.reactionTime)) * tempEffect * phEffect;
    const purity = Math.min(99.9, 98 + conversion);
    const impurity = Math.max(0.01, 2 - conversion * 1.5 + Math.abs(p.temperature - 37) * 0.05);
    const batchProgress = Math.min(100, t * 2);

    return {
      timestamp: t,
      temperature: +this.noise(p.temperature, 0.005).toFixed(2),
      pH: +this.noise(p.pH, 0.01).toFixed(2),
      apiConcentration: +this.noise(p.apiConc * conversion, 0.02).toFixed(2),
      productConcentration: +this.noise(p.apiConc * conversion * 0.9, 0.02).toFixed(2),
      purity: +purity.toFixed(2),
      yield: +(conversion * 100).toFixed(1),
      impurityLevel: +this.noise(impurity, 0.05).toFixed(3),
      dissolvedOxygen: +this.noise(p.dissolvedO2, 0.03).toFixed(2),
      stirringSpeed: +this.noise(p.stirringSpeed, 0.01).toFixed(0),
      batchProgress: +batchProgress.toFixed(1),
    };
  }
}

import type { DataPoint } from '../types';

export abstract class BaseSimulator {
  protected timeStep = 0;
  protected state: Record<string, number> = {};
  parameters: Record<string, number>;

  constructor(defaults: Record<string, number>) {
    this.parameters = { ...defaults };
  }

  abstract step(): DataPoint;

  reset(): void {
    this.timeStep = 0;
    this.state = {};
  }

  protected noise(base: number, pct: number): number {
    return base * (1 + (Math.random() - 0.5) * 2 * pct);
  }

  protected gaussian(mean: number, std: number): number {
    const u1 = Math.random();
    const u2 = Math.random();
    return mean + std * Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }
}

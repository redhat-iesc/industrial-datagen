import { describe, it, expect } from 'vitest';
import { RefinerySimulator } from '../../src/simulators/refinery';

describe('RefinerySimulator', () => {
  it('produces data points with all expected fields', () => {
    const sim = new RefinerySimulator();
    const point = sim.step();
    expect(point).toHaveProperty('timestamp', 0);
    expect(point).toHaveProperty('temperature');
    expect(point).toHaveProperty('pressure');
    expect(point).toHaveProperty('feedRate');
    expect(point).toHaveProperty('gasolineYield');
    expect(point).toHaveProperty('dieselYield');
    expect(point).toHaveProperty('keroseneYield');
    expect(point).toHaveProperty('residualYield');
    expect(point).toHaveProperty('efficiency');
    expect(point).toHaveProperty('energyConsumption');
    expect(point).toHaveProperty('catalystLevel');
  });

  it('increments timestamp on each step', () => {
    const sim = new RefinerySimulator();
    expect(sim.step().timestamp).toBe(0);
    expect(sim.step().timestamp).toBe(1);
    expect(sim.step().timestamp).toBe(2);
  });

  it('produces values within physics-valid ranges', () => {
    const sim = new RefinerySimulator();
    for (let i = 0; i < 100; i++) {
      const point = sim.step();
      expect(point.temperature).toBeGreaterThan(200);
      expect(point.temperature).toBeLessThan(600);
      expect(point.pressure).toBeGreaterThan(0);
      expect(point.efficiency).toBeGreaterThanOrEqual(0);
      expect(point.efficiency).toBeLessThanOrEqual(100);
      expect(point.catalystLevel).toBeGreaterThan(0);
      expect(point.catalystLevel).toBeLessThanOrEqual(1);
    }
  });

  it('degrades catalyst over time', () => {
    const sim = new RefinerySimulator();
    const first = sim.step();
    for (let i = 0; i < 50; i++) sim.step();
    const later = sim.step();
    expect(later.catalystLevel).toBeLessThan(first.catalystLevel as number);
  });

  it('responds to parameter changes', () => {
    const sim1 = new RefinerySimulator();
    sim1.parameters.feedRate = 500;
    const low = sim1.step();

    const sim2 = new RefinerySimulator();
    sim2.parameters.feedRate = 2000;
    const high = sim2.step();

    expect(high.gasolineYield).toBeGreaterThan(low.gasolineYield as number);
  });

  it('resets state correctly', () => {
    const sim = new RefinerySimulator();
    for (let i = 0; i < 10; i++) sim.step();
    sim.reset();
    const point = sim.step();
    expect(point.timestamp).toBe(0);
  });
});

import { describe, it, expect } from 'vitest';
import { PharmaSimulator } from '../../src/simulators/pharma';

describe('PharmaSimulator', () => {
  it('produces data points with all expected fields', () => {
    const sim = new PharmaSimulator();
    const point = sim.step();
    expect(point).toHaveProperty('timestamp', 0);
    expect(point).toHaveProperty('temperature');
    expect(point).toHaveProperty('pH');
    expect(point).toHaveProperty('apiConcentration');
    expect(point).toHaveProperty('productConcentration');
    expect(point).toHaveProperty('purity');
    expect(point).toHaveProperty('yield');
    expect(point).toHaveProperty('impurityLevel');
    expect(point).toHaveProperty('dissolvedOxygen');
    expect(point).toHaveProperty('stirringSpeed');
    expect(point).toHaveProperty('batchProgress');
  });

  it('purity stays within GMP-valid range', () => {
    const sim = new PharmaSimulator();
    for (let i = 0; i < 50; i++) {
      const point = sim.step();
      expect(point.purity).toBeGreaterThan(90);
      expect(point.purity).toBeLessThanOrEqual(99.9);
    }
  });

  it('batch progress increases over time', () => {
    const sim = new PharmaSimulator();
    const first = sim.step();
    for (let i = 0; i < 20; i++) sim.step();
    const later = sim.step();
    expect(later.batchProgress).toBeGreaterThan(first.batchProgress as number);
  });

  it('temperature deviation increases impurity', () => {
    const optimal = new PharmaSimulator();
    optimal.parameters.temperature = 37;
    const optPoint = optimal.step();

    const offTemp = new PharmaSimulator();
    offTemp.parameters.temperature = 55;
    const offPoint = offTemp.step();

    expect(offPoint.impurityLevel).toBeGreaterThan(optPoint.impurityLevel as number);
  });

  it('resets correctly', () => {
    const sim = new PharmaSimulator();
    for (let i = 0; i < 10; i++) sim.step();
    sim.reset();
    expect(sim.step().timestamp).toBe(0);
  });
});

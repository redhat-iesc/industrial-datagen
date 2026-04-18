import { describe, it, expect } from 'vitest';
import { ChemicalSimulator } from '../../src/simulators/chemical';

describe('ChemicalSimulator', () => {
  it('produces data points with all expected fields', () => {
    const sim = new ChemicalSimulator();
    const point = sim.step();
    expect(point).toHaveProperty('timestamp', 0);
    expect(point).toHaveProperty('temperature');
    expect(point).toHaveProperty('pressure');
    expect(point).toHaveProperty('reactantAConc');
    expect(point).toHaveProperty('reactantBConc');
    expect(point).toHaveProperty('productConc');
    expect(point).toHaveProperty('conversion');
    expect(point).toHaveProperty('selectivity');
    expect(point).toHaveProperty('catalystActivity');
    expect(point).toHaveProperty('heatDuty');
    expect(point).toHaveProperty('byproduct');
  });

  it('degrades catalyst activity over time', () => {
    const sim = new ChemicalSimulator();
    const first = sim.step();
    for (let i = 0; i < 50; i++) sim.step();
    const later = sim.step();
    expect(later.catalystActivity).toBeLessThan(first.catalystActivity as number);
  });

  it('produces conversion within valid range', () => {
    const sim = new ChemicalSimulator();
    for (let i = 0; i < 50; i++) {
      const point = sim.step();
      expect(point.conversion).toBeGreaterThanOrEqual(0);
      expect(point.conversion).toBeLessThanOrEqual(100);
      expect(point.selectivity).toBeGreaterThanOrEqual(0);
      expect(point.selectivity).toBeLessThanOrEqual(100);
    }
  });

  it('responds to temperature changes via Arrhenius kinetics', () => {
    const low = new ChemicalSimulator();
    low.parameters.temperature = 280;
    const lowPoint = low.step();

    const high = new ChemicalSimulator();
    high.parameters.temperature = 400;
    const highPoint = high.step();

    expect(highPoint.conversion).toBeGreaterThan(lowPoint.conversion as number);
  });

  it('resets state correctly', () => {
    const sim = new ChemicalSimulator();
    for (let i = 0; i < 10; i++) sim.step();
    sim.reset();
    expect(sim.step().timestamp).toBe(0);
  });
});

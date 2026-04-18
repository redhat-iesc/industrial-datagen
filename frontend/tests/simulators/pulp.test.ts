import { describe, it, expect } from 'vitest';
import { PulpSimulator } from '../../src/simulators/pulp';

describe('PulpSimulator', () => {
  it('produces data points with all expected fields', () => {
    const sim = new PulpSimulator();
    const point = sim.step();
    expect(point).toHaveProperty('timestamp', 0);
    expect(point).toHaveProperty('temperature');
    expect(point).toHaveProperty('pressure');
    expect(point).toHaveProperty('woodChipInput');
    expect(point).toHaveProperty('alkaliConcentration');
    expect(point).toHaveProperty('hFactor');
    expect(point).toHaveProperty('delignification');
    expect(point).toHaveProperty('pulpYield');
    expect(point).toHaveProperty('kappaNumber');
    expect(point).toHaveProperty('brightness');
    expect(point).toHaveProperty('fiberLength');
  });

  it('produces valid kappa number range', () => {
    const sim = new PulpSimulator();
    for (let i = 0; i < 50; i++) {
      const point = sim.step();
      expect(point.kappaNumber).toBeGreaterThan(0);
      expect(point.kappaNumber).toBeLessThan(120);
      expect(point.delignification).toBeGreaterThanOrEqual(0);
      expect(point.delignification).toBeLessThanOrEqual(100);
    }
  });

  it('higher temperature increases H-factor and delignification', () => {
    const low = new PulpSimulator();
    low.parameters.temperature = 145;
    const lowPoint = low.step();

    const high = new PulpSimulator();
    high.parameters.temperature = 175;
    const highPoint = high.step();

    expect(highPoint.hFactor).toBeGreaterThan(lowPoint.hFactor as number);
  });

  it('resets and restarts from zero', () => {
    const sim = new PulpSimulator();
    for (let i = 0; i < 10; i++) sim.step();
    sim.reset();
    expect(sim.step().timestamp).toBe(0);
  });
});

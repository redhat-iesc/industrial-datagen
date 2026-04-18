import { describe, it, expect } from 'vitest';
import { createSimulator } from '../../src/simulators';
import { RefinerySimulator } from '../../src/simulators/refinery';
import { ChemicalSimulator } from '../../src/simulators/chemical';
import { PulpSimulator } from '../../src/simulators/pulp';
import { PharmaSimulator } from '../../src/simulators/pharma';
import { RotatingSimulator } from '../../src/simulators/rotating';
import type { ProcessType } from '../../src/types';

describe('createSimulator', () => {
  const cases: [ProcessType, unknown][] = [
    ['refinery', RefinerySimulator],
    ['chemical', ChemicalSimulator],
    ['pulp', PulpSimulator],
    ['pharma', PharmaSimulator],
    ['rotating', RotatingSimulator],
  ];

  it.each(cases)('creates correct simulator for %s', (type, expected) => {
    const sim = createSimulator(type);
    expect(sim).toBeInstanceOf(expected);
  });

  it('all simulators produce valid data points with timestamp', () => {
    const types: ProcessType[] = ['refinery', 'chemical', 'pulp', 'pharma', 'rotating'];
    for (const type of types) {
      const sim = createSimulator(type);
      const point = sim.step();
      expect(point.timestamp).toBe(0);
      expect(typeof point.timestamp).toBe('number');
    }
  });
});

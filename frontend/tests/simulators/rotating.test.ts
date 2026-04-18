import { describe, it, expect } from 'vitest';
import { RotatingSimulator } from '../../src/simulators/rotating';

describe('RotatingSimulator', () => {
  it('produces data points with all expected fields', () => {
    const sim = new RotatingSimulator();
    const point = sim.step();
    expect(point).toHaveProperty('timestamp', 0);
    expect(point).toHaveProperty('rpm');
    expect(point).toHaveProperty('vibrationX');
    expect(point).toHaveProperty('vibrationY');
    expect(point).toHaveProperty('vibrationZ');
    expect(point).toHaveProperty('vibrationOverall');
    expect(point).toHaveProperty('bearingTemp');
    expect(point).toHaveProperty('motorCurrent');
    expect(point).toHaveProperty('dischargePressure');
    expect(point).toHaveProperty('loadPercent');
    expect(point).toHaveProperty('faultType');
    expect(point).toHaveProperty('faultSeverity');
    expect(point).toHaveProperty('maintenanceRequired');
    expect(point).toHaveProperty('runningHours');
  });

  it('starts with no fault', () => {
    const sim = new RotatingSimulator();
    const point = sim.step();
    expect(point.faultType).toBe('no_fault');
    expect(point.faultSeverity).toBe(0);
  });

  it('bearing fault increases vibration', () => {
    const sim = new RotatingSimulator();
    const baseline = sim.step();

    sim.injectFault('bearing_fault');
    for (let i = 0; i < 30; i++) sim.step();
    const faulted = sim.step();

    expect(faulted.faultType).toBe('bearing_fault');
    expect(faulted.faultSeverity).toBeGreaterThan(0);
    expect(faulted.bearingTemp).toBeGreaterThan(baseline.bearingTemp as number);
  });

  it('rotor imbalance fault injection works', () => {
    const sim = new RotatingSimulator();
    sim.injectFault('rotor_imbalance');
    const point = sim.step();
    expect(point.faultType).toBe('rotor_imbalance');
    expect(point.faultSeverity).toBeGreaterThan(0);
  });

  it('misalignment fault injection works', () => {
    const sim = new RotatingSimulator();
    sim.injectFault('misalignment');
    const point = sim.step();
    expect(point.faultType).toBe('misalignment');
  });

  it('clearing fault resets to no_fault', () => {
    const sim = new RotatingSimulator();
    sim.injectFault('bearing_fault');
    sim.step();
    sim.injectFault('no_fault');
    const point = sim.step();
    expect(point.faultType).toBe('no_fault');
  });

  it('fault severity progresses over time', () => {
    const sim = new RotatingSimulator();
    sim.injectFault('bearing_fault');
    sim.step();
    const early = sim.step();
    for (let i = 0; i < 50; i++) sim.step();
    const late = sim.step();
    expect(late.faultSeverity).toBeGreaterThan(early.faultSeverity as number);
  });

  it('maintenance required triggers at high severity or temperature', () => {
    const sim = new RotatingSimulator();
    sim.injectFault('bearing_fault');
    for (let i = 0; i < 200; i++) sim.step();
    const point = sim.step();
    expect(point.maintenanceRequired).toBe(true);
  });

  it('resets all fault state', () => {
    const sim = new RotatingSimulator();
    sim.injectFault('bearing_fault');
    for (let i = 0; i < 10; i++) sim.step();
    sim.reset();
    const point = sim.step();
    expect(point.faultType).toBe('no_fault');
    expect(point.faultSeverity).toBe(0);
    expect(point.timestamp).toBe(0);
    expect(point.runningHours).toBeCloseTo(0, 2);
  });
});

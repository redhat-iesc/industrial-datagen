import type { DataPoint, FaultType } from '../types';
import { BaseSimulator } from './base';

export class RotatingSimulator extends BaseSimulator {
  private activeFault: FaultType = 'no_fault';
  private faultProgress = 0;
  private bearingDegradation = 0;
  private runningHours = 0;

  constructor() {
    super({ nominalRPM: 3600, loadPercent: 75, ambientTemp: 25, bearingAge: 1000, coolingEfficiency: 0.85, lubricantQuality: 0.9 });
  }

  injectFault(faultType: FaultType): void {
    this.activeFault = faultType;
    this.faultProgress = faultType === 'no_fault' ? 0 : 0.05;
  }

  step(): DataPoint {
    const p = this.parameters;
    const t = this.timeStep++;
    this.runningHours += 1 / 3600;
    const load = p.loadPercent / 100;

    const rpm = this.noise(p.nominalRPM * (1 - load * 0.02), 0.005);
    let vibX = this.gaussian(0, 0.5 + load * 0.3);
    let vibY = this.gaussian(0, 0.4 + load * 0.25);
    let vibZ = this.gaussian(0, 0.3 + load * 0.2);

    if (this.activeFault === 'bearing_fault') {
      vibX += this.faultProgress * 5;
      vibY += this.faultProgress * 4;
    } else if (this.activeFault === 'rotor_imbalance') {
      vibX += this.faultProgress * 6 * Math.sin(t * 0.1);
    } else if (this.activeFault === 'misalignment') {
      vibZ += this.faultProgress * 7;
      vibX += this.faultProgress * 3;
    }

    const vibOverall = Math.sqrt(vibX ** 2 + vibY ** 2 + vibZ ** 2);
    const bearingTemp = p.ambientTemp + 40 * load + this.faultProgress * 30 + this.bearingDegradation * 10;
    const motorCurrent = this.noise(50 * (0.3 + load * 0.7), 0.02);

    if (this.activeFault !== 'no_fault') {
      this.faultProgress = Math.min(1, this.faultProgress + 0.005 * (1 + load));
    }
    this.bearingDegradation += 0.00002 * load;

    return {
      timestamp: t,
      rpm: +rpm.toFixed(1),
      vibrationX: +vibX.toFixed(3),
      vibrationY: +vibY.toFixed(3),
      vibrationZ: +vibZ.toFixed(3),
      vibrationOverall: +vibOverall.toFixed(3),
      bearingTemp: +bearingTemp.toFixed(1),
      motorCurrent: +motorCurrent.toFixed(2),
      dischargePressure: +this.noise(8.5, 0.03).toFixed(2),
      loadPercent: +this.noise(p.loadPercent, 0.01).toFixed(1),
      faultType: this.activeFault,
      faultSeverity: +this.faultProgress.toFixed(4),
      maintenanceRequired: this.faultProgress > 0.5 || bearingTemp > 85,
      runningHours: +this.runningHours.toFixed(2),
    };
  }

  reset(): void {
    super.reset();
    this.activeFault = 'no_fault';
    this.faultProgress = 0;
    this.bearingDegradation = 0;
    this.runningHours = 0;
  }
}

import type { ProcessType } from '../types';
import type { BaseSimulator } from './base';
import { RefinerySimulator } from './refinery';
import { ChemicalSimulator } from './chemical';
import { PulpSimulator } from './pulp';
import { PharmaSimulator } from './pharma';
import { RotatingSimulator } from './rotating';

export { RefinerySimulator } from './refinery';
export { ChemicalSimulator } from './chemical';
export { PulpSimulator } from './pulp';
export { PharmaSimulator } from './pharma';
export { RotatingSimulator } from './rotating';

const SIMULATOR_FACTORIES: Record<ProcessType, () => BaseSimulator> = {
  refinery: () => new RefinerySimulator(),
  chemical: () => new ChemicalSimulator(),
  pulp: () => new PulpSimulator(),
  pharma: () => new PharmaSimulator(),
  rotating: () => new RotatingSimulator(),
};

export function createSimulator(processType: ProcessType): BaseSimulator {
  return SIMULATOR_FACTORIES[processType]();
}

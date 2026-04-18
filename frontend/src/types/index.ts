export type ProcessType = 'refinery' | 'chemical' | 'pulp' | 'pharma' | 'rotating';

export interface ParameterDef {
  name: string;
  label: string;
  min: number;
  max: number;
  default: number;
  unit: string;
}

export interface OutputField {
  name: string;
  description: string;
}

export interface ProcessSchema {
  name: ProcessType;
  description: string;
  parameters: ParameterDef[];
  outputs: OutputField[];
}

export interface SimulationInfo {
  id: string;
  processType: ProcessType;
  status: 'running' | 'stopped' | 'completed';
  parameters: Record<string, number>;
  startedAt: string;
  steps: number;
}

export interface DataPoint {
  timestamp: number;
  [key: string]: number | string | boolean;
}

export interface DatasetInfo {
  id: string;
  processType: ProcessType;
  status: 'generating' | 'ready' | 'failed';
  samples: number;
  includeAnomalies: boolean;
  format: string;
  createdAt: string;
}

export interface HealthInfo {
  status: string;
  uptime: number;
  version: string;
  activeSimulations: number;
}

export type FaultType = 'bearing_fault' | 'rotor_imbalance' | 'misalignment' | 'no_fault';

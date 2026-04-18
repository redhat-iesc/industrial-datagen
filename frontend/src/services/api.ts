import axios from 'axios';
import type {
  DataPoint,
  DatasetInfo,
  FaultType,
  HealthInfo,
  ProcessSchema,
  ProcessType,
  RTSPConfigMap,
  SimulationInfo,
  StreamStatus,
} from '../types';

const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export async function getHealth(): Promise<HealthInfo> {
  const { data } = await client.get('/health');
  return data;
}

export async function getProcesses(): Promise<ProcessSchema[]> {
  const { data } = await client.get('/processes');
  return data;
}

export async function getProcessSchema(processType: ProcessType): Promise<ProcessSchema> {
  const { data } = await client.get(`/processes/${processType}/schema`);
  return data;
}

export async function startSimulation(
  processType: ProcessType,
  parameters?: Record<string, number>,
  intervalMs = 500,
): Promise<SimulationInfo> {
  const { data } = await client.post('/simulation/start', {
    processType,
    parameters: parameters ?? {},
    intervalMs,
  });
  return data;
}

export async function stopSimulation(simId: string): Promise<SimulationInfo> {
  const { data } = await client.post(`/simulation/${simId}/stop`);
  return data;
}

export async function getSimulationCurrent(
  simId: string,
): Promise<{ simulation: SimulationInfo; current: DataPoint | null }> {
  const { data } = await client.get(`/simulation/${simId}/current`);
  return data;
}

export async function getSimulationHistory(
  simId: string,
  limit = 200,
  offset = 0,
): Promise<{ data: DataPoint[]; total: number }> {
  const { data } = await client.get(`/simulation/${simId}/history`, {
    params: { limit, offset },
  });
  return data;
}

export async function updateParameters(
  simId: string,
  parameters: Record<string, number>,
): Promise<SimulationInfo> {
  const { data } = await client.patch(`/simulation/${simId}/parameters`, { parameters });
  return data;
}

export async function injectFault(
  simId: string,
  faultType: FaultType,
): Promise<{ faultType: string }> {
  const { data } = await client.post(`/simulation/${simId}/fault`, { faultType });
  return data;
}

export async function listSimulations(): Promise<SimulationInfo[]> {
  const { data } = await client.get('/simulations');
  return data;
}

export async function generateDataset(
  processType: ProcessType,
  samples: number,
  includeAnomalies = true,
  format = 'csv',
): Promise<DatasetInfo> {
  const { data } = await client.post('/datasets/generate', {
    processType,
    samples,
    includeAnomalies,
    format,
  });
  return data;
}

export async function listDatasets(): Promise<DatasetInfo[]> {
  const { data } = await client.get('/datasets');
  return data;
}

export async function getDatasetStatus(datasetId: string): Promise<DatasetInfo> {
  const { data } = await client.get(`/datasets/${datasetId}/status`);
  return data;
}

export function getDatasetDownloadUrl(datasetId: string, format = 'csv'): string {
  return `/api/datasets/${datasetId}/download?format=${format}`;
}

export async function deleteDataset(datasetId: string): Promise<void> {
  await client.delete(`/datasets/${datasetId}`);
}

export async function getRTSPConfig(): Promise<RTSPConfigMap> {
  const { data } = await client.get('/rtsp/config');
  return data;
}

export async function setRTSPUrl(processType: ProcessType, url: string | null): Promise<void> {
  await client.put(`/rtsp/config/${processType}`, { url });
}

export async function startRTSPStream(
  processType: ProcessType,
): Promise<{ processType: string; status: StreamStatus }> {
  const { data } = await client.post(`/rtsp/${processType}/start`);
  return data;
}

export async function stopRTSPStream(
  processType: ProcessType,
): Promise<{ processType: string; status: string }> {
  const { data } = await client.post(`/rtsp/${processType}/stop`);
  return data;
}

export function getRTSPStreamUrl(processType: ProcessType): string {
  return `/api/rtsp/${processType}/stream.m3u8`;
}

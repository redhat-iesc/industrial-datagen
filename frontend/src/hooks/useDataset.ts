import { useCallback, useState } from 'react';
import type { DatasetInfo, ProcessType } from '../types';
import * as api from '../services/api';

export function useDataset() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const fetchDatasets = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listDatasets();
      setDatasets(data);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, []);

  const generate = useCallback(async (
    processType: ProcessType,
    samples: number,
    includeAnomalies: boolean,
    format: string,
  ) => {
    setGenerating(true);
    try {
      const dataset = await api.generateDataset(processType, samples, includeAnomalies, format);
      setDatasets(prev => [dataset, ...prev]);
      return dataset;
    } finally {
      setGenerating(false);
    }
  }, []);

  const remove = useCallback(async (datasetId: string) => {
    await api.deleteDataset(datasetId);
    setDatasets(prev => prev.filter(d => d.id !== datasetId));
  }, []);

  return { datasets, loading, generating, fetchDatasets, generate, remove };
}

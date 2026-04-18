import { useCallback, useEffect, useRef, useState } from 'react';
import { getRTSPConfig, setRTSPUrl, startRTSPStream, stopRTSPStream } from '../services/api';
import type { ProcessType, RTSPConfigMap } from '../types';

const DEFAULT_CONFIGS: RTSPConfigMap = {
  refinery: { url: null, status: 'offline' },
  chemical: { url: null, status: 'offline' },
  pulp: { url: null, status: 'offline' },
  pharma: { url: null, status: 'offline' },
  rotating: { url: null, status: 'offline' },
};

export function useRTSPStream() {
  const [configs, setConfigs] = useState<RTSPConfigMap>(DEFAULT_CONFIGS);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadConfig = useCallback(async () => {
    try {
      const data = await getRTSPConfig();
      setConfigs(data);
    } catch {
      // keep current state on error
    }
  }, []);

  const setUrl = useCallback(
    async (processType: ProcessType, url: string | null) => {
      await setRTSPUrl(processType, url);
      await loadConfig();
    },
    [loadConfig],
  );

  const startStream = useCallback(
    async (processType: ProcessType) => {
      await startRTSPStream(processType);
      await loadConfig();
    },
    [loadConfig],
  );

  const stopStream = useCallback(
    async (processType: ProcessType) => {
      await stopRTSPStream(processType);
      await loadConfig();
    },
    [loadConfig],
  );

  useEffect(() => {
    let cancelled = false;
    getRTSPConfig()
      .then((data) => {
        if (!cancelled) setConfigs(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const hasStarting = Object.values(configs).some((c) => c.status === 'starting');
    if (hasStarting && !pollRef.current) {
      pollRef.current = setInterval(loadConfig, 2000);
    } else if (!hasStarting && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [configs, loadConfig]);

  return { configs, setUrl, startStream, stopStream, loadConfig };
}

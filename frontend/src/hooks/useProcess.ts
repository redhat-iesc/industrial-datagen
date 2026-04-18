import { useCallback, useEffect, useState } from 'react';
import type { ProcessSchema } from '../types';
import { getProcesses } from '../services/api';

export function useProcess() {
  const [processes, setProcesses] = useState<ProcessSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProcesses = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProcesses();
      setProcesses(data);
    } catch {
      setError('Failed to load processes');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    getProcesses()
      .then(data => { if (!cancelled) setProcesses(data); })
      .catch(() => { if (!cancelled) setError('Failed to load processes'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return { processes, loading, error, refetch: fetchProcesses };
}

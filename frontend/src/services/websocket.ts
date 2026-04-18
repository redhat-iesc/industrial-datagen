import type { DataPoint } from '../types';

export function connectSSE(
  simId: string,
  onData: (point: DataPoint) => void,
  onStop: () => void,
  onError: (err: Event) => void,
): EventSource {
  const source = new EventSource(`/api/simulation/${simId}/feed`);

  source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'stopped') {
      onStop();
      source.close();
    } else {
      onData(data as DataPoint);
    }
  };

  source.onerror = (err) => {
    onError(err);
    source.close();
  };

  return source;
}

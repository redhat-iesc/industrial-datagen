import { useCallback, useEffect, useRef, useState } from 'react';
import type { DataPoint, FaultType, ProcessType, SimulationInfo } from '../types';
import * as api from '../services/api';
import { connectSSE } from '../services/websocket';
import { createSimulator } from '../simulators';
import type { BaseSimulator } from '../simulators/base';
import type { RotatingSimulator } from '../simulators/rotating';

const MAX_POINTS = 200;

export function useSimulation() {
  const [selectedProcess, setSelectedProcess] = useState<ProcessType>('refinery');
  const [isRunning, setIsRunning] = useState(false);
  const [data, setData] = useState<DataPoint[]>([]);
  const [backendMode, setBackendMode] = useState(false);
  const [simInfo, setSimInfo] = useState<SimulationInfo | null>(null);
  const [simulator, setSimulator] = useState<BaseSimulator>(() => createSimulator(selectedProcess));
  const [parameters, setParameters] = useState<Record<string, number>>(() => ({ ...createSimulator(selectedProcess).parameters }));

  const simulatorRef = useRef<BaseSimulator>(simulator);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [prevProcess, setPrevProcess] = useState(selectedProcess);

  if (selectedProcess !== prevProcess) {
    setPrevProcess(selectedProcess);
    const sim = createSimulator(selectedProcess);
    setSimulator(sim);
    setParameters({ ...sim.parameters });
    setData([]);
    setIsRunning(false);
  }

  useEffect(() => {
    simulatorRef.current = simulator;
  }, [simulator]);

  const updateParameter = useCallback((name: string, value: number) => {
    setParameters(prev => {
      const next = { ...prev, [name]: value };
      if (simulatorRef.current) {
        simulatorRef.current.parameters[name] = value;
      }
      if (backendMode && simInfo) {
        api.updateParameters(simInfo.id, { [name]: value }).catch(() => {});
      }
      return next;
    });
  }, [backendMode, simInfo]);

  const addPoint = useCallback((point: DataPoint) => {
    setData(prev => {
      const next = [...prev, point];
      return next.length > MAX_POINTS ? next.slice(-MAX_POINTS) : next;
    });
  }, []);

  const startLocal = useCallback(() => {
    if (intervalRef.current) return;
    setIsRunning(true);
    intervalRef.current = setInterval(() => {
      if (simulatorRef.current) {
        addPoint(simulatorRef.current.step());
      }
    }, 500);
  }, [addPoint]);

  const stopLocal = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsRunning(false);
  }, []);

  const startBackend = useCallback(async () => {
    try {
      const info = await api.startSimulation(selectedProcess, parameters);
      setSimInfo(info);
      setIsRunning(true);

      eventSourceRef.current = connectSSE(
        info.id,
        addPoint,
        () => setIsRunning(false),
        () => setIsRunning(false),
      );
    } catch {
      setIsRunning(false);
    }
  }, [selectedProcess, parameters, addPoint]);

  const stopBackend = useCallback(async () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (simInfo) {
      await api.stopSimulation(simInfo.id).catch(() => {});
    }
    setIsRunning(false);
  }, [simInfo]);

  const start = useCallback(() => {
    if (backendMode) {
      startBackend();
    } else {
      startLocal();
    }
  }, [backendMode, startBackend, startLocal]);

  const stop = useCallback(() => {
    if (backendMode) {
      stopBackend();
    } else {
      stopLocal();
    }
  }, [backendMode, stopBackend, stopLocal]);

  const reset = useCallback(() => {
    stop();
    setData([]);
    if (simulatorRef.current) {
      simulatorRef.current.reset();
      setParameters({ ...simulatorRef.current.parameters });
    }
    setSimInfo(null);
  }, [stop]);

  const injectFault = useCallback(async (faultType: FaultType) => {
    if (backendMode && simInfo) {
      await api.injectFault(simInfo.id, faultType);
    } else if (simulatorRef.current && 'injectFault' in simulatorRef.current) {
      (simulatorRef.current as RotatingSimulator).injectFault(faultType);
    }
  }, [backendMode, simInfo]);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (eventSourceRef.current) eventSourceRef.current.close();
    };
  }, []);

  return {
    selectedProcess,
    setSelectedProcess,
    isRunning,
    data,
    parameters,
    updateParameter,
    backendMode,
    setBackendMode,
    simInfo,
    start,
    stop,
    reset,
    injectFault,
  };
}

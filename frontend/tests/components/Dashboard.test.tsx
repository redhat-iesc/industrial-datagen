import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Dashboard from '../../src/pages/Dashboard';

vi.mock('../../src/hooks/useSimulation', () => ({
  useSimulation: () => ({
    selectedProcess: 'refinery' as const,
    setSelectedProcess: vi.fn(),
    isRunning: false,
    data: [],
    parameters: { crudeTemp: 350, pressure: 2.5, feedRate: 1000, catalystActivity: 0.95 },
    updateParameter: vi.fn(),
    backendMode: false,
    setBackendMode: vi.fn(),
    simInfo: null,
    start: vi.fn(),
    stop: vi.fn(),
    reset: vi.fn(),
    injectFault: vi.fn(),
  }),
}));

vi.mock('../../src/hooks/useRTSPStream', () => ({
  useRTSPStream: () => ({
    configs: {
      refinery: { url: null, status: 'offline' },
      chemical: { url: null, status: 'offline' },
      pulp: { url: null, status: 'offline' },
      pharma: { url: null, status: 'offline' },
      rotating: { url: null, status: 'offline' },
    },
    setUrl: vi.fn(),
    startStream: vi.fn(),
    stopStream: vi.fn(),
    loadConfig: vi.fn(),
  }),
}));

vi.mock('../../src/services/api', () => ({
  getRTSPStreamUrl: (pt: string) => `/api/rtsp/${pt}/stream.m3u8`,
}));

describe('Dashboard', () => {
  it('renders the simulation dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText('Simulation Dashboard')).toBeInTheDocument();
  });

  it('renders process selector with all 5 types', () => {
    render(<Dashboard />);
    expect(screen.getAllByText('Refinery Distillation').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Chemical Reactor').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Pulp Digester').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Pharma Reactor').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Rotating Equipment').length).toBeGreaterThanOrEqual(1);
  });

  it('renders simulation controls', () => {
    render(<Dashboard />);
    expect(screen.getAllByText('Start').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Reset')).toBeInTheDocument();
    expect(screen.getByText('Backend Mode')).toBeInTheDocument();
  });

  it('renders parameter panel for selected process', () => {
    render(<Dashboard />);
    expect(screen.getByText(/Crude Temperature/)).toBeInTheDocument();
  });

  it('renders live chart area', () => {
    render(<Dashboard />);
    expect(screen.getByText('Process Trend Analysis')).toBeInTheDocument();
  });

  it('renders statistics panel', () => {
    render(<Dashboard />);
    expect(screen.getByText('No data available.')).toBeInTheDocument();
  });
});

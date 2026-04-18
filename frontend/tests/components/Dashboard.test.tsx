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

describe('Dashboard', () => {
  it('renders the simulation dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText('Simulation Dashboard')).toBeInTheDocument();
  });

  it('renders process selector with all 5 types', () => {
    render(<Dashboard />);
    expect(screen.getByText('Refinery Distillation')).toBeInTheDocument();
    expect(screen.getByText('Chemical Reactor')).toBeInTheDocument();
    expect(screen.getByText('Pulp Digester')).toBeInTheDocument();
    expect(screen.getByText('Pharma Reactor')).toBeInTheDocument();
    expect(screen.getByText('Rotating Equipment')).toBeInTheDocument();
  });

  it('renders simulation controls', () => {
    render(<Dashboard />);
    expect(screen.getByText('Start')).toBeInTheDocument();
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

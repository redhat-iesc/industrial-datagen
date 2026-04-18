import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import LiveChart from '../../src/components/LiveChart';
import type { DataPoint } from '../../src/types';

describe('LiveChart', () => {
  it('shows empty state when no data', () => {
    render(<LiveChart data={[]} title="Test Chart" />);
    expect(screen.getByText('No data yet. Start a simulation to see live charts.')).toBeInTheDocument();
  });

  it('renders the chart title', () => {
    render(<LiveChart data={[]} title="Process Trend Analysis" />);
    expect(screen.getByText('Process Trend Analysis')).toBeInTheDocument();
  });

  it('renders chart when data is provided', () => {
    const data: DataPoint[] = [
      { timestamp: 0, temperature: 350, pressure: 2.5 },
      { timestamp: 1, temperature: 351, pressure: 2.6 },
      { timestamp: 2, temperature: 349, pressure: 2.4 },
    ];
    render(<LiveChart data={data} title="Test Chart" />);
    expect(screen.queryByText('No data yet. Start a simulation to see live charts.')).not.toBeInTheDocument();
    expect(screen.getByText('Test Chart')).toBeInTheDocument();
  });

  it('renders with explicit fields', () => {
    const data: DataPoint[] = [
      { timestamp: 0, temperature: 350, pressure: 2.5, feedRate: 1000 },
    ];
    render(<LiveChart data={data} title="Selected Fields" fields={['temperature']} />);
    expect(screen.getByText('Selected Fields')).toBeInTheDocument();
  });
});

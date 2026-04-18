import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import StatisticsPanel from '../../src/components/StatisticsPanel';
import type { DataPoint } from '../../src/types';

describe('StatisticsPanel', () => {
  it('shows empty state when no data', () => {
    render(<StatisticsPanel data={[]} />);
    expect(screen.getByText('No data available.')).toBeInTheDocument();
  });

  it('computes and displays statistics for numeric fields', () => {
    const data: DataPoint[] = [
      { timestamp: 0, temperature: 100 },
      { timestamp: 1, temperature: 200 },
      { timestamp: 2, temperature: 300 },
    ];
    render(<StatisticsPanel data={data} />);
    expect(screen.getByText('temperature')).toBeInTheDocument();
    expect(screen.getByText('300.00')).toBeInTheDocument();
    expect(screen.getByText(/min: 100.00/)).toBeInTheDocument();
    expect(screen.getByText(/max: 300.00/)).toBeInTheDocument();
    expect(screen.getByText(/avg: 200.00/)).toBeInTheDocument();
  });

  it('limits to 8 fields max', () => {
    const fields: Record<string, number> = {};
    for (let i = 0; i < 12; i++) {
      fields[`field${i}`] = i * 10;
    }
    const data: DataPoint[] = [{ timestamp: 0, ...fields }];
    const { container } = render(<StatisticsPanel data={data} />);
    const cards = container.querySelectorAll('.pf-v6-c-card');
    expect(cards.length).toBeLessThanOrEqual(8);
  });

  it('excludes timestamp from displayed stats', () => {
    const data: DataPoint[] = [
      { timestamp: 0, value: 42 },
    ];
    render(<StatisticsPanel data={data} />);
    expect(screen.queryByText('timestamp')).not.toBeInTheDocument();
    expect(screen.getByText('value')).toBeInTheDocument();
  });
});

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DatasetManager from '../../src/components/DatasetManager';
import * as api from '../../src/services/api';

vi.mock('../../src/services/api', () => ({
  listDatasets: vi.fn().mockResolvedValue([]),
  generateDataset: vi.fn().mockResolvedValue({
    id: 'ds-1',
    processType: 'refinery',
    status: 'ready',
    samples: 1000,
    includeAnomalies: true,
    format: 'csv',
    createdAt: new Date().toISOString(),
  }),
  deleteDataset: vi.fn().mockResolvedValue(undefined),
  getDatasetDownloadUrl: vi.fn((id: string, format: string) => `/api/datasets/${id}/download?format=${format}`),
}));

vi.mock('@patternfly/react-core', async () => {
  const actual = await vi.importActual<typeof import('@patternfly/react-core')>('@patternfly/react-core');
  return {
    ...actual,
    Select: ({ children, selected, onSelect, id }: {
      children: React.ReactNode;
      selected: string;
      onSelect: (_e: unknown, val: string) => void;
      id: string;
    }) => (
      <select
        data-testid={id}
        value={selected}
        onChange={(e) => onSelect(null, e.target.value)}
      >
        {children}
      </select>
    ),
    SelectOption: ({ value, children }: { value: string; children: React.ReactNode }) => (
      <option value={value}>{children}</option>
    ),
  };
});

describe('DatasetManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders generate dataset form', () => {
    render(<DatasetManager />);
    expect(screen.getAllByText('Generate Dataset').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Process Type')).toBeInTheDocument();
    expect(screen.getByText('Samples')).toBeInTheDocument();
    expect(screen.getByText('Format')).toBeInTheDocument();
    expect(screen.getByText('Include Anomalies')).toBeInTheDocument();
  });

  it('renders generate button', () => {
    render(<DatasetManager />);
    expect(screen.getByRole('button', { name: /generate dataset/i })).toBeInTheDocument();
  });

  it('shows empty state when no datasets', async () => {
    render(<DatasetManager />);
    expect(await screen.findByText('No datasets generated yet.')).toBeInTheDocument();
  });

  it('calls generateDataset on form submit', async () => {
    const user = userEvent.setup();
    render(<DatasetManager />);
    await user.click(screen.getByRole('button', { name: /generate dataset/i }));
    expect(api.generateDataset).toHaveBeenCalled();
  });

  it('renders generated datasets section', () => {
    render(<DatasetManager />);
    expect(screen.getByText('Generated Datasets')).toBeInTheDocument();
  });
});

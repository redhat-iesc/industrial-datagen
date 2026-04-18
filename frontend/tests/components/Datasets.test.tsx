import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Datasets from '../../src/pages/Datasets';

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

describe('Datasets page', () => {
  it('renders the page title', () => {
    render(<Datasets />);
    expect(screen.getByText('Datasets')).toBeInTheDocument();
  });

  it('renders the dataset manager component', () => {
    render(<Datasets />);
    expect(screen.getAllByText('Generate Dataset').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Generated Datasets')).toBeInTheDocument();
  });
});

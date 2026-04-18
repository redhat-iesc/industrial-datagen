import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import ProcessSelector from '../../src/components/ProcessSelector';

describe('ProcessSelector', () => {
  const defaultProps = {
    selected: 'refinery' as const,
    onSelect: vi.fn(),
  };

  it('renders all 5 process types', () => {
    render(<ProcessSelector {...defaultProps} />);
    expect(screen.getByText('Refinery Distillation')).toBeInTheDocument();
    expect(screen.getByText('Chemical Reactor')).toBeInTheDocument();
    expect(screen.getByText('Pulp Digester')).toBeInTheDocument();
    expect(screen.getByText('Pharma Reactor')).toBeInTheDocument();
    expect(screen.getByText('Rotating Equipment')).toBeInTheDocument();
  });

  it('shows descriptions for each process', () => {
    render(<ProcessSelector {...defaultProps} />);
    expect(screen.getByText('Crude oil atmospheric distillation')).toBeInTheDocument();
    expect(screen.getByText('CSTR with Arrhenius kinetics')).toBeInTheDocument();
    expect(screen.getByText('Kraft process H-factor model')).toBeInTheDocument();
    expect(screen.getByText('GMP-compliant batch reactor')).toBeInTheDocument();
    expect(screen.getByText('Predictive maintenance & vibration')).toBeInTheDocument();
  });

  it('calls onSelect when clicking a process card', async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(<ProcessSelector {...defaultProps} onSelect={onSelect} />);
    await user.click(screen.getByText('Chemical Reactor'));
    expect(onSelect).toHaveBeenCalledWith('chemical');
  });

  it('does not call onSelect when disabled', async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(<ProcessSelector {...defaultProps} onSelect={onSelect} disabled />);
    await user.click(screen.getByText('Chemical Reactor'));
    expect(onSelect).not.toHaveBeenCalled();
  });
});

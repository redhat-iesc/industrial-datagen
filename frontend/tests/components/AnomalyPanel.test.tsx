import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import AnomalyPanel from '../../src/components/AnomalyPanel';

describe('AnomalyPanel', () => {
  const defaultProps = {
    onInjectFault: vi.fn(),
    isRunning: true,
  };

  it('renders fault injection title', () => {
    render(<AnomalyPanel {...defaultProps} />);
    expect(screen.getByText('Fault Injection')).toBeInTheDocument();
  });

  it('renders all 3 fault types', () => {
    render(<AnomalyPanel {...defaultProps} />);
    expect(screen.getByText('Bearing Fault')).toBeInTheDocument();
    expect(screen.getByText('Rotor Imbalance')).toBeInTheDocument();
    expect(screen.getByText('Misalignment')).toBeInTheDocument();
  });

  it('renders fault descriptions', () => {
    render(<AnomalyPanel {...defaultProps} />);
    expect(screen.getByText(/High-frequency radial vibration/)).toBeInTheDocument();
    expect(screen.getByText(/1x RPM vibration/)).toBeInTheDocument();
    expect(screen.getByText(/2x RPM.*axial vibration/)).toBeInTheDocument();
  });

  it('calls onInjectFault with correct type when clicking Inject', async () => {
    const onInjectFault = vi.fn();
    const user = userEvent.setup();
    render(<AnomalyPanel onInjectFault={onInjectFault} isRunning />);
    const injectButtons = screen.getAllByText('Inject');
    await user.click(injectButtons[0]);
    expect(onInjectFault).toHaveBeenCalledWith('bearing_fault');
  });

  it('calls onInjectFault with no_fault when clearing', async () => {
    const onInjectFault = vi.fn();
    const user = userEvent.setup();
    render(<AnomalyPanel onInjectFault={onInjectFault} isRunning />);
    await user.click(screen.getByText('Clear Faults'));
    expect(onInjectFault).toHaveBeenCalledWith('no_fault');
  });

  it('disables inject buttons when not running', () => {
    render(<AnomalyPanel onInjectFault={vi.fn()} isRunning={false} />);
    const injectButtons = screen.getAllByText('Inject');
    injectButtons.forEach(btn => {
      expect(btn.closest('button')).toBeDisabled();
    });
    expect(screen.getByText('Clear Faults').closest('button')).toBeDisabled();
  });
});

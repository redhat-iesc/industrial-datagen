import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import SimulationControls from '../../src/components/SimulationControls';

describe('SimulationControls', () => {
  const defaultProps = {
    isRunning: false,
    backendMode: false,
    onStart: vi.fn(),
    onStop: vi.fn(),
    onReset: vi.fn(),
    onBackendModeChange: vi.fn(),
  };

  it('shows Start button when not running', () => {
    render(<SimulationControls {...defaultProps} />);
    expect(screen.getByText('Start')).toBeInTheDocument();
    expect(screen.queryByText('Stop')).not.toBeInTheDocument();
  });

  it('shows Stop button when running', () => {
    render(<SimulationControls {...defaultProps} isRunning />);
    expect(screen.getByText('Stop')).toBeInTheDocument();
    expect(screen.queryByText('Start')).not.toBeInTheDocument();
  });

  it('calls onStart when clicking Start', async () => {
    const onStart = vi.fn();
    const user = userEvent.setup();
    render(<SimulationControls {...defaultProps} onStart={onStart} />);
    await user.click(screen.getByText('Start'));
    expect(onStart).toHaveBeenCalledOnce();
  });

  it('calls onStop when clicking Stop', async () => {
    const onStop = vi.fn();
    const user = userEvent.setup();
    render(<SimulationControls {...defaultProps} isRunning onStop={onStop} />);
    await user.click(screen.getByText('Stop'));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it('calls onReset when clicking Reset', async () => {
    const onReset = vi.fn();
    const user = userEvent.setup();
    render(<SimulationControls {...defaultProps} onReset={onReset} />);
    await user.click(screen.getByText('Reset'));
    expect(onReset).toHaveBeenCalledOnce();
  });

  it('disables Reset while running', () => {
    render(<SimulationControls {...defaultProps} isRunning />);
    expect(screen.getByText('Reset').closest('button')).toBeDisabled();
  });

  it('renders Backend Mode switch', () => {
    render(<SimulationControls {...defaultProps} />);
    expect(screen.getByText('Backend Mode')).toBeInTheDocument();
  });

  it('disables Backend Mode switch while running', () => {
    render(<SimulationControls {...defaultProps} isRunning />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl).toBeDisabled();
  });
});

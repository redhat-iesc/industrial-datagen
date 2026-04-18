import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import RTSPConfigPanel from '../../src/components/RTSPConfigPanel';
import type { RTSPConfigMap } from '../../src/types';

const offlineConfigs: RTSPConfigMap = {
  refinery: { url: null, status: 'offline' },
  chemical: { url: null, status: 'offline' },
  pulp: { url: null, status: 'offline' },
  pharma: { url: null, status: 'offline' },
  rotating: { url: null, status: 'offline' },
};

const mixedConfigs: RTSPConfigMap = {
  refinery: { url: 'rtsp://cam1:554/stream', status: 'streaming' },
  chemical: { url: 'rtsp://cam2:554/stream', status: 'starting' },
  pulp: { url: null, status: 'offline' },
  pharma: { url: 'rtsp://cam4:554/stream', status: 'error' },
  rotating: { url: null, status: 'offline' },
};

describe('RTSPConfigPanel', () => {
  it('renders all 5 process type labels', () => {
    render(
      <RTSPConfigPanel
        configs={offlineConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    expect(screen.getByText('Refinery Distillation')).toBeInTheDocument();
    expect(screen.getByText('Chemical Reactor')).toBeInTheDocument();
    expect(screen.getByText('Pulp Digester')).toBeInTheDocument();
    expect(screen.getByText('Pharma Reactor')).toBeInTheDocument();
    expect(screen.getByText('Rotating Equipment')).toBeInTheDocument();
  });

  it('renders card title', () => {
    render(
      <RTSPConfigPanel
        configs={offlineConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    expect(screen.getByText('RTSP Camera Feeds')).toBeInTheDocument();
  });

  it('shows status labels for each process', () => {
    render(
      <RTSPConfigPanel
        configs={mixedConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    expect(screen.getByText('streaming')).toBeInTheDocument();
    expect(screen.getByText('starting')).toBeInTheDocument();
    expect(screen.getByText('error')).toBeInTheDocument();
    expect(screen.getAllByText('offline')).toHaveLength(2);
  });

  it('shows Stop button for streaming/starting, Start for others', () => {
    render(
      <RTSPConfigPanel
        configs={mixedConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const stopButtons = screen.getAllByText('Stop');
    const startButtons = screen.getAllByText('Start');
    expect(stopButtons).toHaveLength(2);
    expect(startButtons).toHaveLength(3);
  });

  it('disables Start button when no URL configured', () => {
    render(
      <RTSPConfigPanel
        configs={offlineConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const startButtons = screen.getAllByText('Start');
    startButtons.forEach((btn) => {
      expect(btn.closest('button')).toBeDisabled();
    });
  });

  it('calls onStart when Start is clicked', async () => {
    const onStart = vi.fn();
    const configs: RTSPConfigMap = {
      ...offlineConfigs,
      refinery: { url: 'rtsp://cam:554/s', status: 'offline' },
    };
    render(
      <RTSPConfigPanel
        configs={configs}
        onSaveUrl={vi.fn()}
        onStart={onStart}
        onStop={vi.fn()}
      />,
    );
    const startButtons = screen.getAllByText('Start');
    await userEvent.click(startButtons[0]);
    expect(onStart).toHaveBeenCalledWith('refinery');
  });

  it('calls onStop when Stop is clicked', async () => {
    const onStop = vi.fn();
    render(
      <RTSPConfigPanel
        configs={mixedConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={onStop}
      />,
    );
    const stopButtons = screen.getAllByText('Stop');
    await userEvent.click(stopButtons[0]);
    expect(onStop).toHaveBeenCalledWith('refinery');
  });

  it('calls onSaveUrl when Save is clicked', async () => {
    const onSaveUrl = vi.fn();
    render(
      <RTSPConfigPanel
        configs={offlineConfigs}
        onSaveUrl={onSaveUrl}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const input = screen.getByLabelText('RTSP URL for Refinery Distillation');
    await userEvent.type(input, 'rtsp://new:554/s');
    const saveButtons = screen.getAllByText('Save');
    await userEvent.click(saveButtons[0]);
    expect(onSaveUrl).toHaveBeenCalledWith('refinery', 'rtsp://new:554/s');
  });

  it('disables input and Save for streaming processes', () => {
    render(
      <RTSPConfigPanel
        configs={mixedConfigs}
        onSaveUrl={vi.fn()}
        onStart={vi.fn()}
        onStop={vi.fn()}
      />,
    );
    const refineryInput = screen.getByLabelText('RTSP URL for Refinery Distillation');
    expect(refineryInput).toBeDisabled();
  });
});

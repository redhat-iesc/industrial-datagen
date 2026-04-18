import { render, screen, cleanup } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import RTSPVideoPlayer from '../../src/components/RTSPVideoPlayer';

const mockDestroy = vi.fn();
const mockLoadSource = vi.fn();
const mockAttachMedia = vi.fn();
const mockOn = vi.fn();

vi.mock('hls.js', () => {
  class HlsMock {
    loadSource = mockLoadSource;
    attachMedia = mockAttachMedia;
    on = mockOn;
    destroy = mockDestroy;
    static isSupported = vi.fn().mockReturnValue(true);
    static Events = { MANIFEST_PARSED: 'hlsManifestParsed' };
  }
  return { default: HlsMock };
});

describe('RTSPVideoPlayer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct test id', () => {
    render(
      <RTSPVideoPlayer
        processType="refinery"
        streamUrl="/api/rtsp/refinery/stream.m3u8"
        processName="Refinery Distillation"
      />,
    );
    expect(screen.getByTestId('rtsp-player-refinery')).toBeInTheDocument();
  });

  it('renders process name and Live Feed label', () => {
    render(
      <RTSPVideoPlayer
        processType="refinery"
        streamUrl="/api/rtsp/refinery/stream.m3u8"
        processName="Refinery Distillation"
      />,
    );
    expect(screen.getByText(/Refinery Distillation — Live Feed/)).toBeInTheDocument();
    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('renders a video element', () => {
    render(
      <RTSPVideoPlayer
        processType="chemical"
        streamUrl="/api/rtsp/chemical/stream.m3u8"
        processName="Chemical Reactor"
      />,
    );
    const video = document.querySelector('video');
    expect(video).toBeInTheDocument();
    expect((video as HTMLVideoElement).muted).toBe(true);
  });

  it('initializes hls.js with stream URL', () => {
    render(
      <RTSPVideoPlayer
        processType="refinery"
        streamUrl="/api/rtsp/refinery/stream.m3u8"
        processName="Refinery Distillation"
      />,
    );
    expect(mockLoadSource).toHaveBeenCalledWith('/api/rtsp/refinery/stream.m3u8');
    expect(mockAttachMedia).toHaveBeenCalled();
    expect(mockOn).toHaveBeenCalledWith('hlsManifestParsed', expect.any(Function));
  });

  it('destroys hls.js instance on unmount', () => {
    render(
      <RTSPVideoPlayer
        processType="refinery"
        streamUrl="/api/rtsp/refinery/stream.m3u8"
        processName="Refinery Distillation"
      />,
    );
    cleanup();
    expect(mockDestroy).toHaveBeenCalled();
  });
});

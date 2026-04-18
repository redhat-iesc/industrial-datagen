import { useEffect, useRef } from 'react';
import { Card, CardBody, CardTitle, Flex, FlexItem, Label } from '@patternfly/react-core';
import Hls from 'hls.js';

interface Props {
  processType: string;
  streamUrl: string;
  processName: string;
}

export default function RTSPVideoPlayer({ processType, streamUrl, processName }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (Hls.isSupported()) {
      const hls = new Hls({
        liveSyncDurationCount: 3,
        liveMaxLatencyDurationCount: 5,
        enableWorker: true,
      });
      hls.loadSource(streamUrl);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(() => {});
      });
      hlsRef.current = hls;

      return () => {
        hls.destroy();
        hlsRef.current = null;
      };
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = streamUrl;
      video.addEventListener('loadedmetadata', () => {
        video.play().catch(() => {});
      });

      return () => {
        video.src = '';
      };
    }
  }, [streamUrl]);

  return (
    <Card data-testid={`rtsp-player-${processType}`}>
      <CardTitle>
        <Flex alignItems={{ default: 'alignItemsCenter' }} gap={{ default: 'gapSm' }}>
          <FlexItem>{processName} — Live Feed</FlexItem>
          <FlexItem>
            <Label color="red" icon={<span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--pf-t--global--color--status--danger--default)', animation: 'pulse 1.5s infinite' }} />}>
              LIVE
            </Label>
          </FlexItem>
        </Flex>
      </CardTitle>
      <CardBody>
        <video
          ref={videoRef}
          style={{ width: '100%', maxHeight: 400, backgroundColor: '#000' }}
          controls
          muted
          playsInline
        />
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
          }
        `}</style>
      </CardBody>
    </Card>
  );
}

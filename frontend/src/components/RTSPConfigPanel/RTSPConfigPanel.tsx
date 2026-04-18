import { useState } from 'react';
import {
  Button,
  Card,
  CardBody,
  CardTitle,
  Flex,
  FlexItem,
  Label,
  Stack,
  StackItem,
  TextInput,
} from '@patternfly/react-core';
import type { ProcessType, RTSPConfigMap, StreamStatus } from '../../types';

const PROCESS_LABELS: Record<ProcessType, string> = {
  refinery: 'Refinery Distillation',
  chemical: 'Chemical Reactor',
  pulp: 'Pulp Digester',
  pharma: 'Pharma Reactor',
  rotating: 'Rotating Equipment',
};

const STATUS_COLORS: Record<StreamStatus, 'grey' | 'blue' | 'green' | 'red'> = {
  offline: 'grey',
  starting: 'blue',
  streaming: 'green',
  error: 'red',
};

interface Props {
  configs: RTSPConfigMap;
  onSaveUrl: (processType: ProcessType, url: string | null) => Promise<void>;
  onStart: (processType: ProcessType) => Promise<void>;
  onStop: (processType: ProcessType) => Promise<void>;
}

export default function RTSPConfigPanel({ configs, onSaveUrl, onStart, onStop }: Props) {
  const [urls, setUrls] = useState<Record<string, string>>({});

  const getInputUrl = (pt: ProcessType) => urls[pt] ?? configs[pt]?.url ?? '';

  return (
    <Card>
      <CardTitle>RTSP Camera Feeds</CardTitle>
      <CardBody>
        <Stack hasGutter>
          {(Object.keys(PROCESS_LABELS) as ProcessType[]).map((pt) => {
            const config = configs[pt];
            const status = config?.status ?? 'offline';

            return (
              <StackItem key={pt}>
                <Flex alignItems={{ default: 'alignItemsCenter' }} gap={{ default: 'gapSm' }}>
                  <FlexItem>
                    <strong>{PROCESS_LABELS[pt]}</strong>
                  </FlexItem>
                  <FlexItem>
                    <Label color={STATUS_COLORS[status]}>{status}</Label>
                  </FlexItem>
                  <FlexItem grow={{ default: 'grow' }}>
                    <TextInput
                      aria-label={`RTSP URL for ${PROCESS_LABELS[pt]}`}
                      placeholder="rtsp://camera:554/stream"
                      value={getInputUrl(pt)}
                      onChange={(_e, val) => setUrls((prev) => ({ ...prev, [pt]: val }))}
                      isDisabled={status === 'streaming' || status === 'starting'}
                    />
                  </FlexItem>
                  <FlexItem>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        const url = getInputUrl(pt).trim();
                        onSaveUrl(pt, url || null);
                      }}
                      isDisabled={status === 'streaming' || status === 'starting'}
                    >
                      Save
                    </Button>
                  </FlexItem>
                  <FlexItem>
                    {status === 'streaming' || status === 'starting' ? (
                      <Button variant="danger" size="sm" onClick={() => onStop(pt)}>
                        Stop
                      </Button>
                    ) : (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => onStart(pt)}
                        isDisabled={!config?.url}
                      >
                        Start
                      </Button>
                    )}
                  </FlexItem>
                </Flex>
              </StackItem>
            );
          })}
        </Stack>
      </CardBody>
    </Card>
  );
}

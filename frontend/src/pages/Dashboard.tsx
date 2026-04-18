import { useState } from 'react';
import {
  Button,
  Grid,
  GridItem,
  PageSection,
  Stack,
  StackItem,
  Title,
} from '@patternfly/react-core';
import ProcessSelector from '../components/ProcessSelector';
import ParameterPanel from '../components/ParameterPanel';
import SimulationControls from '../components/SimulationControls';
import LiveChart from '../components/LiveChart';
import StatisticsPanel from '../components/StatisticsPanel';
import AnomalyPanel from '../components/AnomalyPanel';
import RTSPConfigPanel from '../components/RTSPConfigPanel';
import RTSPVideoPlayer from '../components/RTSPVideoPlayer';
import { useSimulation } from '../hooks/useSimulation';
import { useRTSPStream } from '../hooks/useRTSPStream';
import { getRTSPStreamUrl } from '../services/api';

const PROCESS_NAMES: Record<string, string> = {
  refinery: 'Refinery Distillation',
  chemical: 'Chemical Reactor',
  pulp: 'Pulp Digester',
  pharma: 'Pharma Reactor',
  rotating: 'Rotating Equipment',
};

export default function Dashboard() {
  const sim = useSimulation();
  const rtsp = useRTSPStream();
  const [showRTSP, setShowRTSP] = useState(false);

  return (
    <>
      <PageSection className="rh-page-header">
        <Title headingLevel="h1">Simulation Dashboard</Title>
      </PageSection>
      <PageSection className="rh-section-compact">
        <Stack hasGutter>
          <StackItem>
            <ProcessSelector
              selected={sim.selectedProcess}
              onSelect={sim.setSelectedProcess}
              disabled={sim.isRunning}
            />
          </StackItem>
          <StackItem>
            <SimulationControls
              isRunning={sim.isRunning}
              backendMode={sim.backendMode}
              onStart={sim.start}
              onStop={sim.stop}
              onReset={sim.reset}
              onBackendModeChange={sim.setBackendMode}
            />
          </StackItem>
          <StackItem>
            <Button
              variant="secondary"
              onClick={() => setShowRTSP((prev) => !prev)}
            >
              {showRTSP ? 'Hide Camera Feeds' : 'Show Camera Feeds'}
            </Button>
          </StackItem>
          {showRTSP && (
            <StackItem>
              <RTSPConfigPanel
                configs={rtsp.configs}
                onSaveUrl={rtsp.setUrl}
                onStart={rtsp.startStream}
                onStop={rtsp.stopStream}
              />
            </StackItem>
          )}
          {rtsp.configs[sim.selectedProcess]?.status === 'streaming' && (
            <StackItem>
              <RTSPVideoPlayer
                processType={sim.selectedProcess}
                streamUrl={getRTSPStreamUrl(sim.selectedProcess)}
                processName={PROCESS_NAMES[sim.selectedProcess] ?? sim.selectedProcess}
              />
            </StackItem>
          )}
          <StackItem>
            <Grid hasGutter>
              <GridItem span={8}>
                <Stack hasGutter>
                  <StackItem>
                    <LiveChart data={sim.data} title="Process Trend Analysis" />
                  </StackItem>
                  <StackItem>
                    <StatisticsPanel data={sim.data} />
                  </StackItem>
                </Stack>
              </GridItem>
              <GridItem span={4}>
                <Stack hasGutter>
                  <StackItem>
                    <ParameterPanel
                      processType={sim.selectedProcess}
                      parameters={sim.parameters}
                      onParameterChange={sim.updateParameter}
                    />
                  </StackItem>
                  {sim.selectedProcess === 'rotating' && (
                    <StackItem>
                      <AnomalyPanel
                        onInjectFault={sim.injectFault}
                        isRunning={sim.isRunning}
                      />
                    </StackItem>
                  )}
                </Stack>
              </GridItem>
            </Grid>
          </StackItem>
        </Stack>
      </PageSection>
    </>
  );
}

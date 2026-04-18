import {
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
import { useSimulation } from '../hooks/useSimulation';

export default function Dashboard() {
  const sim = useSimulation();

  return (
    <>
      <PageSection>
        <Title headingLevel="h1">Simulation Dashboard</Title>
      </PageSection>
      <PageSection>
        <ProcessSelector
          selected={sim.selectedProcess}
          onSelect={sim.setSelectedProcess}
          disabled={sim.isRunning}
        />
      </PageSection>
      <PageSection>
        <SimulationControls
          isRunning={sim.isRunning}
          backendMode={sim.backendMode}
          onStart={sim.start}
          onStop={sim.stop}
          onReset={sim.reset}
          onBackendModeChange={sim.setBackendMode}
        />
      </PageSection>
      <PageSection>
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
      </PageSection>
    </>
  );
}

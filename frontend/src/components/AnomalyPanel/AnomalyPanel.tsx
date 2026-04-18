import {
  Button,
  Card,
  CardBody,
  CardTitle,
  DescriptionList,
  DescriptionListDescription,
  DescriptionListGroup,
  DescriptionListTerm,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import type { FaultType } from '../../types';

const FAULTS: { type: FaultType; label: string; description: string }[] = [
  { type: 'bearing_fault', label: 'Bearing Fault', description: 'High-frequency radial vibration + heat generation' },
  { type: 'rotor_imbalance', label: 'Rotor Imbalance', description: '1x RPM vibration + current swing' },
  { type: 'misalignment', label: 'Misalignment', description: '2x RPM + strong axial vibration' },
];

interface Props {
  onInjectFault: (faultType: FaultType) => void;
  isRunning: boolean;
}

export default function AnomalyPanel({ onInjectFault, isRunning }: Props) {
  return (
    <Card isCompact>
      <CardTitle>Fault Injection</CardTitle>
      <CardBody>
        <Stack hasGutter>
          <StackItem>
            <DescriptionList isCompact>
              {FAULTS.map(f => (
                <DescriptionListGroup key={f.type}>
                  <DescriptionListTerm>{f.label}</DescriptionListTerm>
                  <DescriptionListDescription>
                    {f.description}
                    <div style={{ marginTop: '0.5rem' }}>
                      <Button
                        variant="warning"
                        size="sm"
                        onClick={() => onInjectFault(f.type)}
                        isDisabled={!isRunning}
                      >
                        Inject
                      </Button>
                    </div>
                  </DescriptionListDescription>
                </DescriptionListGroup>
              ))}
            </DescriptionList>
          </StackItem>
          <StackItem>
            <Button
              variant="secondary"
              onClick={() => onInjectFault('no_fault')}
              isDisabled={!isRunning}
            >
              Clear Faults
            </Button>
          </StackItem>
        </Stack>
      </CardBody>
    </Card>
  );
}

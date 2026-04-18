import {
  Card,
  CardBody,
  CardTitle,
} from '@patternfly/react-core';
import type { ProcessType } from '../../types';

interface ProcessInfo {
  type: ProcessType;
  label: string;
  description: string;
}

const PROCESSES: ProcessInfo[] = [
  { type: 'refinery', label: 'Refinery Distillation', description: 'Crude oil atmospheric distillation' },
  { type: 'chemical', label: 'Chemical Reactor', description: 'CSTR with Arrhenius kinetics' },
  { type: 'pulp', label: 'Pulp Digester', description: 'Kraft process H-factor model' },
  { type: 'pharma', label: 'Pharma Reactor', description: 'GMP-compliant batch reactor' },
  { type: 'rotating', label: 'Rotating Equipment', description: 'Predictive maintenance & vibration' },
];

interface Props {
  selected: ProcessType;
  onSelect: (type: ProcessType) => void;
  disabled?: boolean;
}

export default function ProcessSelector({ selected, onSelect, disabled }: Props) {
  return (
    <div className="rh-process-grid">
      {PROCESSES.map(p => (
        <Card
          key={p.type}
          isSelectable
          isSelected={selected === p.type}
          isDisabled={disabled}
          onClick={() => !disabled && onSelect(p.type)}
          isCompact
          isFullHeight
          className="rh-process-card"
        >
          <CardTitle>{p.label}</CardTitle>
          <CardBody>{p.description}</CardBody>
        </Card>
      ))}
    </div>
  );
}

import {
  Form,
  FormGroup,
  NumberInput,
  Slider,
  Stack,
  StackItem,
} from '@patternfly/react-core';

interface ParameterDef {
  name: string;
  label: string;
  min: number;
  max: number;
  unit: string;
}

const PARAMETER_DEFS: Record<string, ParameterDef[]> = {
  refinery: [
    { name: 'crudeTemp', label: 'Crude Temperature', min: 200, max: 500, unit: '°C' },
    { name: 'pressure', label: 'Pressure', min: 1, max: 5, unit: 'atm' },
    { name: 'feedRate', label: 'Feed Rate', min: 500, max: 2000, unit: 'kg/h' },
    { name: 'catalystActivity', label: 'Catalyst Activity', min: 0.1, max: 1.0, unit: '' },
  ],
  chemical: [
    { name: 'reactantA', label: 'Reactant A', min: 0.5, max: 5.0, unit: 'mol/L' },
    { name: 'reactantB', label: 'Reactant B', min: 0.5, max: 5.0, unit: 'mol/L' },
    { name: 'temperature', label: 'Temperature', min: 250, max: 450, unit: '°C' },
    { name: 'pressure', label: 'Pressure', min: 5, max: 20, unit: 'atm' },
    { name: 'catalystConc', label: 'Catalyst Conc.', min: 0.01, max: 0.1, unit: 'mol/L' },
  ],
  pulp: [
    { name: 'woodInput', label: 'Wood Input', min: 50, max: 200, unit: 'tons' },
    { name: 'alkaliConc', label: 'Alkali Concentration', min: 10, max: 25, unit: 'g/L' },
    { name: 'temperature', label: 'Temperature', min: 140, max: 180, unit: '°C' },
    { name: 'pressure', label: 'Pressure', min: 5, max: 12, unit: 'atm' },
    { name: 'cookingTime', label: 'Cooking Time', min: 60, max: 240, unit: 'min' },
  ],
  pharma: [
    { name: 'apiConc', label: 'API Concentration', min: 10, max: 100, unit: 'g/L' },
    { name: 'solventVol', label: 'Solvent Volume', min: 200, max: 1000, unit: 'mL' },
    { name: 'temperature', label: 'Temperature', min: 20, max: 60, unit: '°C' },
    { name: 'stirringSpeed', label: 'Stirring Speed', min: 50, max: 500, unit: 'RPM' },
    { name: 'pH', label: 'pH', min: 4, max: 10, unit: '' },
  ],
  rotating: [
    { name: 'nominalRPM', label: 'Nominal RPM', min: 1000, max: 6000, unit: 'RPM' },
    { name: 'loadPercent', label: 'Load', min: 10, max: 100, unit: '%' },
    { name: 'ambientTemp', label: 'Ambient Temp', min: 10, max: 45, unit: '°C' },
    { name: 'bearingAge', label: 'Bearing Age', min: 0, max: 10000, unit: 'hours' },
  ],
};

interface Props {
  processType: string;
  parameters: Record<string, number>;
  onParameterChange: (name: string, value: number) => void;
}

export default function ParameterPanel({ processType, parameters, onParameterChange }: Props) {
  const defs = PARAMETER_DEFS[processType] ?? [];

  return (
    <Form>
      <Stack hasGutter>
        {defs.map(def => {
          const value = parameters[def.name] ?? def.min;
          const step = (def.max - def.min) <= 1 ? 0.01 : (def.max - def.min) <= 10 ? 0.1 : 1;
          return (
            <StackItem key={def.name}>
              <FormGroup
                label={`${def.label}${def.unit ? ` (${def.unit})` : ''}`}
                fieldId={`param-${def.name}`}
              >
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <Slider
                      id={`slider-${def.name}`}
                      value={value}
                      min={def.min}
                      max={def.max}
                      step={step}
                      onChange={(_e, val) => onParameterChange(def.name, val)}
                      showTicks={false}
                    />
                  </div>
                  <NumberInput
                    id={`param-${def.name}`}
                    value={value}
                    min={def.min}
                    max={def.max}
                    onMinus={() => onParameterChange(def.name, Math.max(def.min, value - step))}
                    onPlus={() => onParameterChange(def.name, Math.min(def.max, value + step))}
                    onChange={(event) => {
                      const v = parseFloat((event.target as HTMLInputElement).value);
                      if (!isNaN(v)) onParameterChange(def.name, Math.min(def.max, Math.max(def.min, v)));
                    }}
                    widthChars={6}
                  />
                </div>
              </FormGroup>
            </StackItem>
          );
        })}
      </Stack>
    </Form>
  );
}

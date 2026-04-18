import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ParameterPanel from '../../src/components/ParameterPanel';

describe('ParameterPanel', () => {
  it('renders refinery parameters', () => {
    render(
      <ParameterPanel
        processType="refinery"
        parameters={{ crudeTemp: 350, pressure: 2.5, feedRate: 1000, catalystActivity: 0.95 }}
        onParameterChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/Crude Temperature/)).toBeInTheDocument();
    expect(screen.getByText(/Pressure/)).toBeInTheDocument();
    expect(screen.getByText(/Feed Rate/)).toBeInTheDocument();
    expect(screen.getByText(/Catalyst Activity/)).toBeInTheDocument();
  });

  it('renders chemical parameters', () => {
    render(
      <ParameterPanel
        processType="chemical"
        parameters={{ reactantA: 2.0, reactantB: 1.5, temperature: 350, pressure: 10, catalystConc: 0.05 }}
        onParameterChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/Reactant A/)).toBeInTheDocument();
    expect(screen.getByText(/Reactant B/)).toBeInTheDocument();
    expect(screen.getByText(/Catalyst Conc/)).toBeInTheDocument();
  });

  it('renders pulp parameters', () => {
    render(
      <ParameterPanel
        processType="pulp"
        parameters={{ woodInput: 100, alkaliConc: 15, temperature: 170, pressure: 8, cookingTime: 120 }}
        onParameterChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/Wood Input/)).toBeInTheDocument();
    expect(screen.getByText(/Alkali Concentration/)).toBeInTheDocument();
    expect(screen.getByText(/Cooking Time/)).toBeInTheDocument();
  });

  it('renders pharma parameters', () => {
    render(
      <ParameterPanel
        processType="pharma"
        parameters={{ apiConc: 50, solventVol: 500, temperature: 37, stirringSpeed: 200, pH: 7.0 }}
        onParameterChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/API Concentration/)).toBeInTheDocument();
    expect(screen.getByText(/Solvent Volume/)).toBeInTheDocument();
    expect(screen.getByText(/Stirring Speed/)).toBeInTheDocument();
  });

  it('renders rotating parameters', () => {
    render(
      <ParameterPanel
        processType="rotating"
        parameters={{ nominalRPM: 3600, loadPercent: 75, ambientTemp: 25, bearingAge: 1000 }}
        onParameterChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/Nominal RPM/)).toBeInTheDocument();
    expect(screen.getByText(/Load/)).toBeInTheDocument();
    expect(screen.getByText(/Ambient Temp/)).toBeInTheDocument();
    expect(screen.getByText(/Bearing Age/)).toBeInTheDocument();
  });

  it('renders nothing for unknown process type', () => {
    const { container } = render(
      <ParameterPanel
        processType="unknown"
        parameters={{}}
        onParameterChange={vi.fn()}
      />,
    );
    const form = container.querySelector('form');
    expect(form).toBeInTheDocument();
  });
});

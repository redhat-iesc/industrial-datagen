import {
  Button,
  Switch,
  Toolbar,
  ToolbarContent,
  ToolbarGroup,
  ToolbarItem,
} from '@patternfly/react-core';
import { PlayIcon, StopIcon, UndoIcon } from '@patternfly/react-icons';

interface Props {
  isRunning: boolean;
  backendMode: boolean;
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
  onBackendModeChange: (enabled: boolean) => void;
}

export default function SimulationControls({
  isRunning,
  backendMode,
  onStart,
  onStop,
  onReset,
  onBackendModeChange,
}: Props) {
  return (
    <Toolbar>
      <ToolbarContent>
        <ToolbarGroup>
          <ToolbarItem>
            {isRunning ? (
              <Button variant="danger" icon={<StopIcon />} onClick={onStop}>
                Stop
              </Button>
            ) : (
              <Button variant="primary" icon={<PlayIcon />} onClick={onStart}>
                Start
              </Button>
            )}
          </ToolbarItem>
          <ToolbarItem>
            <Button variant="secondary" icon={<UndoIcon />} onClick={onReset} isDisabled={isRunning}>
              Reset
            </Button>
          </ToolbarItem>
        </ToolbarGroup>
        <ToolbarGroup align={{ default: 'alignEnd' }}>
          <ToolbarItem>
            <Switch
              id="backend-mode"
              label="Backend Mode"
              isChecked={backendMode}
              onChange={(_e, checked) => onBackendModeChange(checked)}
              isDisabled={isRunning}
            />
          </ToolbarItem>
        </ToolbarGroup>
      </ToolbarContent>
    </Toolbar>
  );
}

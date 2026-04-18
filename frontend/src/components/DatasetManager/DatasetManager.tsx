import { useEffect, useState } from 'react';
import {
  Button,
  Card,
  CardBody,
  CardTitle,
  EmptyState,
  EmptyStateBody,
  Form,
  FormGroup,
  MenuToggle,
  NumberInput,
  Select,
  SelectList,
  SelectOption,
  Slider,
  Stack,
  StackItem,
  Switch,
} from '@patternfly/react-core';
import { DownloadIcon, TrashIcon } from '@patternfly/react-icons';
import { Table, Tbody, Td, Th, Thead, Tr } from '@patternfly/react-table';
import type { DatasetInfo, ProcessType } from '../../types';
import { getDatasetDownloadUrl } from '../../services/api';
import { useDataset } from '../../hooks/useDataset';

const PROCESS_TYPES: ProcessType[] = ['refinery', 'chemical', 'pulp', 'pharma', 'rotating'];

export default function DatasetManager() {
  const { datasets, loading, generating, fetchDatasets, generate, remove } = useDataset();
  const [processType, setProcessType] = useState<ProcessType>('refinery');
  const [samples, setSamples] = useState(1000);
  const [includeAnomalies, setIncludeAnomalies] = useState(true);
  const [format, setFormat] = useState('csv');
  const [processSelectOpen, setProcessSelectOpen] = useState(false);
  const [formatSelectOpen, setFormatSelectOpen] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  const handleGenerate = async () => {
    await generate(processType, samples, includeAnomalies, format);
  };

  return (
    <Stack hasGutter>
      <StackItem>
        <Card>
          <CardTitle>Generate Dataset</CardTitle>
          <CardBody>
            <Form isHorizontal>
              <FormGroup label="Process Type" fieldId="ds-process">
                <Select
                  id="ds-process"
                  isOpen={processSelectOpen}
                  selected={processType}
                  onSelect={(_e, val) => {
                    setProcessType(val as ProcessType);
                    setProcessSelectOpen(false);
                  }}
                  onOpenChange={setProcessSelectOpen}
                  toggle={(toggleRef) => (
                    <MenuToggle
                      ref={toggleRef}
                      onClick={() => setProcessSelectOpen(prev => !prev)}
                      isExpanded={processSelectOpen}
                    >
                      {processType}
                    </MenuToggle>
                  )}
                >
                  <SelectList>
                    {PROCESS_TYPES.map(pt => (
                      <SelectOption key={pt} value={pt}>
                        {pt}
                      </SelectOption>
                    ))}
                  </SelectList>
                </Select>
              </FormGroup>
              <FormGroup label="Samples" fieldId="ds-samples">
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <Slider
                      id="ds-samples-slider"
                      value={samples}
                      min={100}
                      max={10000}
                      step={100}
                      onChange={(_e, val) => setSamples(val)}
                    />
                  </div>
                  <NumberInput
                    id="ds-samples"
                    value={samples}
                    min={100}
                    max={10000}
                    onMinus={() => setSamples(s => Math.max(100, s - 100))}
                    onPlus={() => setSamples(s => Math.min(10000, s + 100))}
                    onChange={(e) => {
                      const v = parseInt((e.target as HTMLInputElement).value);
                      if (!isNaN(v)) setSamples(Math.min(10000, Math.max(100, v)));
                    }}
                    widthChars={6}
                  />
                </div>
              </FormGroup>
              <FormGroup label="Format" fieldId="ds-format">
                <Select
                  id="ds-format"
                  isOpen={formatSelectOpen}
                  selected={format}
                  onSelect={(_e, val) => {
                    setFormat(val as string);
                    setFormatSelectOpen(false);
                  }}
                  onOpenChange={setFormatSelectOpen}
                  toggle={(toggleRef) => (
                    <MenuToggle
                      ref={toggleRef}
                      onClick={() => setFormatSelectOpen(prev => !prev)}
                      isExpanded={formatSelectOpen}
                    >
                      {format.toUpperCase()}
                    </MenuToggle>
                  )}
                >
                  <SelectList>
                    <SelectOption value="csv">CSV</SelectOption>
                    <SelectOption value="json">JSON</SelectOption>
                  </SelectList>
                </Select>
              </FormGroup>
              <FormGroup label="Include Anomalies" fieldId="ds-anomalies">
                <Switch
                  id="ds-anomalies"
                  isChecked={includeAnomalies}
                  onChange={(_e, checked) => setIncludeAnomalies(checked)}
                />
              </FormGroup>
              <FormGroup>
                <Button
                  variant="primary"
                  onClick={handleGenerate}
                  isLoading={generating}
                  isDisabled={generating}
                >
                  Generate Dataset
                </Button>
              </FormGroup>
            </Form>
          </CardBody>
        </Card>
      </StackItem>

      <StackItem>
        <Card>
          <CardTitle>Generated Datasets</CardTitle>
          <CardBody>
            {datasets.length === 0 ? (
              <EmptyState>
                <EmptyStateBody>
                  {loading ? 'Loading datasets...' : 'No datasets generated yet.'}
                </EmptyStateBody>
              </EmptyState>
            ) : (
              <Table variant="compact">
                <Thead>
                  <Tr>
                    <Th>Process</Th>
                    <Th>Samples</Th>
                    <Th>Format</Th>
                    <Th>Status</Th>
                    <Th>Created</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {datasets.map((ds: DatasetInfo) => (
                    <Tr key={ds.id}>
                      <Td>{ds.processType}</Td>
                      <Td>{ds.samples}</Td>
                      <Td>{ds.format}</Td>
                      <Td>{ds.status}</Td>
                      <Td>{new Date(ds.createdAt).toLocaleString()}</Td>
                      <Td>
                        <Button
                          variant="link"
                          icon={<DownloadIcon />}
                          component="a"
                          href={getDatasetDownloadUrl(ds.id, ds.format)}
                          isDisabled={ds.status !== 'ready'}
                        >
                          Download
                        </Button>
                        <Button
                          variant="link"
                          isDanger
                          icon={<TrashIcon />}
                          onClick={() => remove(ds.id)}
                        >
                          Delete
                        </Button>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  );
}

import { PageSection, Title } from '@patternfly/react-core';
import DatasetManager from '../components/DatasetManager';

export default function Datasets() {
  return (
    <>
      <PageSection>
        <Title headingLevel="h1">Datasets</Title>
      </PageSection>
      <PageSection>
        <DatasetManager />
      </PageSection>
    </>
  );
}

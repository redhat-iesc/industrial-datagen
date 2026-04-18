import { PageSection, Title } from '@patternfly/react-core';
import DatasetManager from '../components/DatasetManager';

export default function Datasets() {
  return (
    <>
      <PageSection className="rh-page-header">
        <Title headingLevel="h1">Datasets</Title>
      </PageSection>
      <PageSection className="rh-section-compact">
        <DatasetManager />
      </PageSection>
    </>
  );
}

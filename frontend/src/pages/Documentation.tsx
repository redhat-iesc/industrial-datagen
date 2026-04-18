import {
  Card,
  CardBody,
  CardTitle,
  Gallery,
  GalleryItem,
  PageSection,
  Title,
} from '@patternfly/react-core';
import { BookOpenIcon } from '@patternfly/react-icons';

const DOCS = [
  {
    title: 'Architecture',
    description: 'System design, data flow, and project structure.',
    file: 'ARCHITECTURE.md',
  },
  {
    title: 'API Reference',
    description: 'REST, WebSocket, and SSE endpoint specifications.',
    file: 'API_REFERENCE.md',
  },
  {
    title: 'Simulators',
    description: 'Physics models, parameters, and output fields for all five simulators.',
    file: 'SIMULATORS.md',
  },
  {
    title: 'Data Model',
    description: 'TypeScript and Pydantic types, storage contract.',
    file: 'DATA_MODEL.md',
  },
  {
    title: 'Development',
    description: 'Setup, testing, code conventions, and dependencies.',
    file: 'DEVELOPMENT.md',
  },
  {
    title: 'Deployment',
    description: 'Container builds, Docker Compose, OpenShift, and bootc.',
    file: 'DEPLOYMENT.md',
  },
  {
    title: 'CI/CD',
    description: 'GitHub Actions workflows, release process, and local verification.',
    file: 'CI_CD.md',
  },
  {
    title: 'Roadmap',
    description: 'Planned features and project milestones.',
    file: 'ROADMAP.md',
  },
];

export default function Documentation() {
  return (
    <>
      <PageSection className="rh-page-header">
        <Title headingLevel="h1">Documentation</Title>
      </PageSection>
      <PageSection className="rh-section-compact">
        <Gallery hasGutter minWidths={{ default: '300px' }}>
          {DOCS.map((doc) => (
            <GalleryItem key={doc.file}>
              <Card isFullHeight>
                <CardTitle>
                  <BookOpenIcon style={{ marginRight: 8 }} />
                  {doc.title}
                </CardTitle>
                <CardBody>
                  <p>{doc.description}</p>
                  <p style={{ marginTop: 12 }}>
                    <code style={{ fontSize: '0.85rem', color: 'var(--rh-red)' }}>
                      docs/{doc.file}
                    </code>
                  </p>
                </CardBody>
              </Card>
            </GalleryItem>
          ))}
        </Gallery>
      </PageSection>
    </>
  );
}

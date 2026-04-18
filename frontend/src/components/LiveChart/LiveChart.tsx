import { useMemo } from 'react';
import {
  Chart,
  ChartAxis,
  ChartGroup,
  ChartLine,
  ChartThemeColor,
  ChartVoronoiContainer,
} from '@patternfly/react-charts/victory';
import { Card, CardBody, CardTitle } from '@patternfly/react-core';
import type { DataPoint } from '../../types';

interface Props {
  data: DataPoint[];
  title: string;
  fields?: string[];
}

export default function LiveChart({ data, title, fields }: Props) {
  const numericFields = useMemo(() => {
    if (fields) return fields;
    if (data.length === 0) return [];
    const sample = data[data.length - 1];
    return Object.keys(sample)
      .filter(k => typeof sample[k] === 'number' && k !== 'timestamp')
      .slice(0, 4);
  }, [data, fields]);

  if (data.length === 0 || numericFields.length === 0) {
    return (
      <Card isCompact>
        <CardTitle>{title}</CardTitle>
        <CardBody>No data yet. Start a simulation to see live charts.</CardBody>
      </Card>
    );
  }

  const recent = data.slice(-50);

  return (
    <Card isCompact>
      <CardTitle>{title}</CardTitle>
      <CardBody>
        <div style={{ height: '300px' }}>
          <Chart
            containerComponent={
              <ChartVoronoiContainer
                labels={({ datum }: { datum: { name: string; y: number } }) =>
                  `${datum.name}: ${datum.y}`
                }
              />
            }
            height={300}
            padding={{ top: 20, right: 30, bottom: 50, left: 60 }}
            themeColor={ChartThemeColor.multiOrdered}
          >
            <ChartAxis
              tickFormat={(t: number) => `${t}`}
              label="Time Step"
            />
            <ChartAxis dependentAxis />
            <ChartGroup>
              {numericFields.map(field => (
                <ChartLine
                  key={field}
                  name={field}
                  data={recent.map(d => ({
                    x: d.timestamp as number,
                    y: d[field] as number,
                    name: field,
                  }))}
                />
              ))}
            </ChartGroup>
          </Chart>
        </div>
      </CardBody>
    </Card>
  );
}

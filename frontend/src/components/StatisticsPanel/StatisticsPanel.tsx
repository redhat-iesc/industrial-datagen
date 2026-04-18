import { useMemo } from 'react';
import { Card, CardBody, CardTitle, Grid, GridItem } from '@patternfly/react-core';
import type { DataPoint } from '../../types';

interface Props {
  data: DataPoint[];
}

export default function StatisticsPanel({ data }: Props) {
  const stats = useMemo(() => {
    if (data.length === 0) return [];
    const latest = data[data.length - 1];
    const numericKeys = Object.keys(latest).filter(
      k => typeof latest[k] === 'number' && k !== 'timestamp',
    );
    return numericKeys.slice(0, 8).map(key => {
      const values = data.map(d => d[key] as number).filter(v => typeof v === 'number');
      const current = values[values.length - 1];
      const min = Math.min(...values);
      const max = Math.max(...values);
      const avg = values.reduce((a, b) => a + b, 0) / values.length;
      return { key, current, min, max, avg };
    });
  }, [data]);

  if (stats.length === 0) {
    return (
      <Card isCompact>
        <CardTitle>Statistics</CardTitle>
        <CardBody>No data available.</CardBody>
      </Card>
    );
  }

  return (
    <Grid hasGutter>
      {stats.map(s => (
        <GridItem key={s.key} span={3} sm={6} md={3}>
          <Card isCompact isPlain>
            <CardTitle style={{ fontSize: '0.85rem' }}>{s.key}</CardTitle>
            <CardBody>
              <div className="rh-stat-value">
                {s.current.toFixed(2)}
              </div>
              <div className="rh-stat-meta">
                min: {s.min.toFixed(2)} / max: {s.max.toFixed(2)} / avg: {s.avg.toFixed(2)}
              </div>
            </CardBody>
          </Card>
        </GridItem>
      ))}
    </Grid>
  );
}

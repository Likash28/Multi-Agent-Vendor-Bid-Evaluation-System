"use client"

import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface RadarChartProps {
  data: Array<{
    criterion: string;
    [key: string]: string | number;
  }>;
  dataKeys: Array<{
    key: string;
    color: string;
    name: string;
  }>;
}

export function RadarChart({ data, dataKeys }: RadarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <RechartsRadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="criterion" />
        <PolarRadiusAxis angle={90} domain={[0, 100]} />
        <Tooltip />
        <Legend />
        {dataKeys.map((dk) => (
          <Radar
            key={dk.key}
            name={dk.name}
            dataKey={dk.key}
            stroke={dk.color}
            fill={dk.color}
            fillOpacity={0.3}
          />
        ))}
      </RechartsRadarChart>
    </ResponsiveContainer>
  );
}

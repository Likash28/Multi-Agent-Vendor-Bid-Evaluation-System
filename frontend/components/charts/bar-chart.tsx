"use client"

import {
  Bar,
  BarChart as RechartsBarChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface BarChartProps {
  data: Array<{
    name: string;
    [key: string]: string | number;
  }>;
  dataKeys: Array<{
    key: string;
    color: string;
    name: string;
  }>;
  xAxisKey?: string;
}

export function BarChart({ data, dataKeys, xAxisKey = 'name' }: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <RechartsBarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxisKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        {dataKeys.map((dk) => (
          <Bar key={dk.key} dataKey={dk.key} name={dk.name} fill={dk.color} />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}

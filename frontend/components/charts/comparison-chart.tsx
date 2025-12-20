"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface ComparisonChartProps {
  data: Array<{
    vendor: string;
    compliance: number;
    technical: number;
    financial: number;
    total: number;
    isWinner?: boolean;
  }>;
}

const COLORS = {
  compliance: '#10b981',
  technical: '#3b82f6',
  financial: '#f59e0b',
  total: '#8b5cf6',
};

export function ComparisonChart({ data }: ComparisonChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="vendor" />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Legend />
        <Bar dataKey="compliance" name="Compliance" fill={COLORS.compliance}>
          {data.map((entry, index) => (
            <Cell
              key={`cell-compliance-${index}`}
              fill={entry.isWinner ? '#059669' : COLORS.compliance}
            />
          ))}
        </Bar>
        <Bar dataKey="technical" name="Technical" fill={COLORS.technical}>
          {data.map((entry, index) => (
            <Cell
              key={`cell-technical-${index}`}
              fill={entry.isWinner ? '#2563eb' : COLORS.technical}
            />
          ))}
        </Bar>
        <Bar dataKey="financial" name="Financial" fill={COLORS.financial}>
          {data.map((entry, index) => (
            <Cell
              key={`cell-financial-${index}`}
              fill={entry.isWinner ? '#d97706' : COLORS.financial}
            />
          ))}
        </Bar>
        <Bar dataKey="total" name="Total Score" fill={COLORS.total}>
          {data.map((entry, index) => (
            <Cell
              key={`cell-total-${index}`}
              fill={entry.isWinner ? '#7c3aed' : COLORS.total}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

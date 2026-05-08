'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ChartData {
  name: string;
  income: number;
  expenses: number;
}

interface MonthlyChartProps {
  data: ChartData[];
}

const formatNaira = (value: number) =>
  `₦${value.toLocaleString('en-NG', { maximumFractionDigits: 0 })}`;

export default function MonthlyChart({ data }: MonthlyChartProps) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
        No data to display yet.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={formatNaira} tick={{ fontSize: 11 }} width={80} />
        <Tooltip formatter={(value: number) => formatNaira(value)} />
        <Legend />
        <Bar dataKey="income" fill="#16a34a" name="Income" radius={[3, 3, 0, 0]} />
        <Bar dataKey="expenses" fill="#dc2626" name="Expenses" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

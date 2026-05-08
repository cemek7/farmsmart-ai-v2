'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import MonthlyChart from '@/components/charts/MonthlyChart';
import { api } from '@/lib/api';
import { Report } from '@/lib/types';

const formatNaira = (n: number) =>
  `₦${n.toLocaleString('en-NG', { maximumFractionDigits: 2 })}`;

function KPICard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: 'green' | 'red' | 'blue';
}) {
  const colors = {
    green: 'bg-green-50 border-green-200 text-green-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
  };
  return (
    <div className={`rounded-xl border p-5 ${colors[color]}`}>
      <p className="text-sm font-medium opacity-70">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get<Report>('/reports')
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Build monthly chart data from crop breakdowns (summary-level data)
  const chartData = report
    ? Object.keys({ ...report.expense_by_crop, ...report.income_by_crop }).map((crop) => ({
        name: crop,
        income: report.income_by_crop[crop] ?? 0,
        expenses: report.expense_by_crop[crop] ?? 0,
      }))
    : [];

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
            <div className="flex gap-2">
              <Link
                href="/expenses/new"
                className="bg-green-600 hover:bg-green-700 text-white text-sm px-4 py-2 rounded-lg font-medium transition-colors"
              >
                + Add Expense
              </Link>
              <Link
                href="/income/new"
                className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-lg font-medium transition-colors"
              >
                + Add Income
              </Link>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600" />
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
              {error}
            </div>
          ) : report ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <KPICard label="Total Income" value={formatNaira(report.total_income)} color="green" />
                <KPICard label="Total Expenses" value={formatNaira(report.total_expense)} color="red" />
                <KPICard
                  label="Net Profit"
                  value={formatNaira(report.net_profit)}
                  color={report.net_profit >= 0 ? 'green' : 'red'}
                />
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                <h3 className="font-semibold text-gray-700 mb-4">Income vs Expenses by Crop</h3>
                <MonthlyChart data={chartData} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-700 mb-3">Expenses by Crop</h3>
                  {Object.keys(report.expense_by_crop).length === 0 ? (
                    <p className="text-gray-400 text-sm">No expenses recorded yet.</p>
                  ) : (
                    <ul className="space-y-2">
                      {Object.entries(report.expense_by_crop).map(([crop, amount]) => (
                        <li key={crop} className="flex justify-between text-sm">
                          <span className="capitalize text-gray-600">{crop}</span>
                          <span className="font-medium text-red-600">{formatNaira(amount)}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-700 mb-3">Income by Crop</h3>
                  {Object.keys(report.income_by_crop).length === 0 ? (
                    <p className="text-gray-400 text-sm">No income recorded yet.</p>
                  ) : (
                    <ul className="space-y-2">
                      {Object.entries(report.income_by_crop).map(([crop, amount]) => (
                        <li key={crop} className="flex justify-between text-sm">
                          <span className="capitalize text-gray-600">{crop}</span>
                          <span className="font-medium text-green-600">{formatNaira(amount)}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </>
          ) : null}
        </main>
      </div>
    </ProtectedRoute>
  );
}

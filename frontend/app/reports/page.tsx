'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import MonthlyChart from '@/components/charts/MonthlyChart';
import { api } from '@/lib/api';
import { Report } from '@/lib/types';

const formatNaira = (n: number) => `₦${n.toLocaleString('en-NG', { maximumFractionDigits: 2 })}`;
const MONTHS = [
  { value: '', label: 'All months' },
  { value: '1', label: 'January' },
  { value: '2', label: 'February' },
  { value: '3', label: 'March' },
  { value: '4', label: 'April' },
  { value: '5', label: 'May' },
  { value: '6', label: 'June' },
  { value: '7', label: 'July' },
  { value: '8', label: 'August' },
  { value: '9', label: 'September' },
  { value: '10', label: 'October' },
  { value: '11', label: 'November' },
  { value: '12', label: 'December' },
];

export default function ReportsPage() {
  const currentYear = new Date().getFullYear();
  const [year, setYear] = useState(String(currentYear));
  const [month, setMonth] = useState('');
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchReport = () => {
    setLoading(true);
    setError('');
    const params = new URLSearchParams();
    if (year) params.set('year', year);
    if (month) params.set('month', month);
    const qs = params.toString() ? `?${params.toString()}` : '';
    api
      .get<Report>(`/reports${qs}`)
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchReport(); }, [year, month]);

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
          <div className="flex flex-wrap items-center gap-4 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mr-auto">Reports</h2>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-600">Year</label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-green-500"
                min="2000"
                max="2100"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-600">Month</label>
              <select
                value={month}
                onChange={(e) => setMonth(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {MONTHS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600" />
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">{error}</div>
          ) : report ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div className="bg-green-50 border border-green-200 rounded-xl p-5">
                  <p className="text-sm font-medium text-green-700 opacity-70">Total Income</p>
                  <p className="text-2xl font-bold text-green-700 mt-1">{formatNaira(report.total_income)}</p>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-xl p-5">
                  <p className="text-sm font-medium text-red-700 opacity-70">Total Expenses</p>
                  <p className="text-2xl font-bold text-red-700 mt-1">{formatNaira(report.total_expense)}</p>
                </div>
                <div className={`rounded-xl border p-5 ${report.net_profit >= 0 ? 'bg-blue-50 border-blue-200' : 'bg-orange-50 border-orange-200'}`}>
                  <p className={`text-sm font-medium opacity-70 ${report.net_profit >= 0 ? 'text-blue-700' : 'text-orange-700'}`}>
                    Net Profit
                  </p>
                  <p className={`text-2xl font-bold mt-1 ${report.net_profit >= 0 ? 'text-blue-700' : 'text-orange-700'}`}>
                    {formatNaira(report.net_profit)}
                  </p>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                <h3 className="font-semibold text-gray-700 mb-4">Income vs Expenses by Crop</h3>
                <MonthlyChart data={chartData} />
              </div>
            </>
          ) : null}
        </main>
      </div>
    </ProtectedRoute>
  );
}

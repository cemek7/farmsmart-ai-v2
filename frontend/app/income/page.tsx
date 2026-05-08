'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/lib/api';
import { Income } from '@/lib/types';

const formatNaira = (n: number) => `₦${n.toLocaleString('en-NG', { maximumFractionDigits: 2 })}`;

export default function IncomePage() {
  const [incomes, setIncomes] = useState<Income[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get<Income[]>('/income')
      .then(setIncomes)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this income record?')) return;
    try {
      await api.del(`/income/${id}`);
      setIncomes((prev) => prev.filter((i) => i.id !== id));
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Income</h2>
            <Link
              href="/income/new"
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-lg font-medium transition-colors"
            >
              + Add Income
            </Link>
          </div>

          {loading ? (
            <div className="flex justify-center py-16">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">{error}</div>
          ) : incomes.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <p className="text-gray-400">No income records yet.</p>
              <Link href="/income/new" className="text-blue-600 hover:underline text-sm mt-2 inline-block">
                Record your first income
              </Link>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Crop</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Date</th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">Amount</th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">Quantity (kg)</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Paired</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {incomes.map((i) => (
                    <tr key={i.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 capitalize font-medium text-gray-800">{i.crop_type}</td>
                      <td className="px-4 py-3 text-gray-500">{i.date}</td>
                      <td className="px-4 py-3 text-right font-semibold text-green-600">{formatNaira(i.amount)}</td>
                      <td className="px-4 py-3 text-right text-gray-500">{i.quantity}</td>
                      <td className="px-4 py-3 text-center">
                        {i.is_paired ? (
                          <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full font-medium">
                            Paired
                          </span>
                        ) : (
                          <span className="bg-gray-100 text-gray-500 text-xs px-2 py-0.5 rounded-full">
                            Unpaired
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleDelete(i.id)}
                          className="text-red-400 hover:text-red-600 text-xs font-medium"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}

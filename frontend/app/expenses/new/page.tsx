'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/lib/api';
import { Expense, ExpenseCreate } from '@/lib/types';

const CROPS = ['maize', 'rice', 'cassava', 'yam', 'tomato'];

const FIELDS: { name: keyof ExpenseCreate; label: string; type: string; placeholder?: string }[] = [
  { name: 'seed_cost', label: 'Seed Cost (₦)', type: 'number', placeholder: '8000' },
  { name: 'fertilizer_cost', label: 'Fertilizer Cost (₦)', type: 'number', placeholder: '5000' },
  { name: 'labor_cost', label: 'Labor Cost (₦)', type: 'number', placeholder: '15000' },
  { name: 'irrigation_cost', label: 'Irrigation Cost (₦)', type: 'number', placeholder: '2500' },
  { name: 'transport_cost', label: 'Transport Cost (₦)', type: 'number', placeholder: '2000' },
  { name: 'other_cost', label: 'Other Cost (₦)', type: 'number', placeholder: '0' },
  { name: 'farm_size', label: 'Farm Size (hectares)', type: 'number', placeholder: '2.0' },
];

const defaultForm: ExpenseCreate = {
  crop_type: 'maize',
  seed_cost: 0,
  fertilizer_cost: 0,
  labor_cost: 0,
  irrigation_cost: 0,
  transport_cost: 0,
  other_cost: 0,
  farm_size: 0,
  date: new Date().toISOString().split('T')[0],
};

export default function NewExpensePage() {
  const router = useRouter();
  const [form, setForm] = useState<ExpenseCreate>(defaultForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setForm({ ...form, [name]: type === 'number' ? parseFloat(value) || 0 : value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post<Expense>('/expenses', form);
      router.push('/expenses');
    } catch (err: any) {
      setError(err.message ?? 'Failed to save expense');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-2xl mx-auto px-4 py-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Record Expense</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Crop Type</label>
              <select
                name="crop_type"
                value={form.crop_type}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {CROPS.map((c) => (
                  <option key={c} value={c} className="capitalize">
                    {c.charAt(0).toUpperCase() + c.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {FIELDS.map(({ name, label, type, placeholder }) => (
                <div key={name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input
                    type={type}
                    name={name}
                    value={(form as any)[name]}
                    onChange={handleChange}
                    placeholder={placeholder}
                    step="0.01"
                    min="0"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              ))}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                <input
                  type="date"
                  name="date"
                  value={form.date}
                  onChange={handleChange}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
              >
                {loading ? 'Saving...' : 'Save Expense'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 border border-gray-300 text-gray-600 hover:bg-gray-50 rounded-lg text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  );
}

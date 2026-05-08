'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/lib/api';
import { Prediction, PredictionRequest } from '@/lib/types';

const CROPS = ['maize', 'rice', 'cassava', 'yam', 'tomato'];
const formatNaira = (n: number) => `₦${n.toLocaleString('en-NG', { maximumFractionDigits: 2 })}`;

const MODEL_BADGE: Record<string, { label: string; color: string }> = {
  personal: { label: 'Personal Model', color: 'bg-purple-100 text-purple-700' },
  community: { label: 'Community Model', color: 'bg-blue-100 text-blue-700' },
  baseline: { label: 'Baseline Model', color: 'bg-gray-100 text-gray-600' },
};

const defaultForm: PredictionRequest = {
  crop_type: 'maize',
  seed_cost: 0,
  fertilizer_cost: 0,
  labor_cost: 0,
  irrigation_cost: 0,
  transport_cost: 0,
  farm_size: 0,
};

const COST_FIELDS: { name: keyof PredictionRequest; label: string }[] = [
  { name: 'seed_cost', label: 'Seed Cost (₦)' },
  { name: 'fertilizer_cost', label: 'Fertilizer Cost (₦)' },
  { name: 'labor_cost', label: 'Labor Cost (₦)' },
  { name: 'irrigation_cost', label: 'Irrigation Cost (₦)' },
  { name: 'transport_cost', label: 'Transport Cost (₦)' },
  { name: 'farm_size', label: 'Farm Size (ha)' },
];

export default function PredictionsPage() {
  const [form, setForm] = useState<PredictionRequest>(defaultForm);
  const [result, setResult] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get<Prediction[]>('/predict/history').then(setHistory).catch(() => {});
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    setForm({ ...form, [name]: type === 'number' ? parseFloat(value) || 0 : value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const pred = await api.post<Prediction>('/predict', form);
      setResult(pred);
      setHistory((prev) => [pred, ...prev].slice(0, 10));
    } catch (err: any) {
      setError(err.message ?? 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Revenue Predictions</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Prediction Form */}
            <div>
              <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
                <h3 className="font-semibold text-gray-700">Enter Farm Details</h3>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
                    {error}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Crop Type</label>
                  <select
                    name="crop_type"
                    value={form.crop_type}
                    onChange={handleChange}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {CROPS.map((c) => (
                      <option key={c} value={c}>
                        {c.charAt(0).toUpperCase() + c.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {COST_FIELDS.map(({ name, label }) => (
                    <div key={name}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                      <input
                        type="number"
                        name={name}
                        value={(form as any)[name]}
                        onChange={handleChange}
                        min="0"
                        step="0.01"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
                >
                  {loading ? 'Predicting...' : 'Predict Revenue'}
                </button>
              </form>

              {/* Result Card */}
              {result && (
                <div className="mt-4 bg-white rounded-xl border border-green-200 p-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-700">Prediction Result</h3>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        MODEL_BADGE[result.model_used]?.color ?? 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {MODEL_BADGE[result.model_used]?.label ?? result.model_used}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Predicted Revenue</span>
                      <span className="font-bold text-green-600 text-base">
                        {formatNaira(result.predicted_revenue)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Predicted Profit</span>
                      <span className={`font-bold text-base ${result.predicted_profit >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                        {formatNaira(result.predicted_profit)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* History */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-700 mb-4">Recent Predictions</h3>
              {history.length === 0 ? (
                <p className="text-gray-400 text-sm">No predictions yet.</p>
              ) : (
                <div className="space-y-3">
                  {history.map((p) => (
                    <div key={p.id} className="border border-gray-100 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="capitalize font-medium text-gray-700 text-sm">{p.crop_type}</span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            MODEL_BADGE[p.model_used]?.color ?? 'bg-gray-100 text-gray-600'
                          }`}
                        >
                          {p.model_used}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Revenue: <span className="text-green-600 font-medium">{formatNaira(p.predicted_revenue)}</span></span>
                        <span>Profit: <span className={`font-medium ${p.predicted_profit >= 0 ? 'text-blue-600' : 'text-red-600'}`}>{formatNaira(p.predicted_profit)}</span></span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}

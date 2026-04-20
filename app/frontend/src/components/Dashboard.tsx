'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface Metrics {
  traffic: number;
  latency_p50: number;
  latency_p95: number;
  latency_p99: number;
  avg_cost_usd: number;
  total_cost_usd: number;
  tokens_in_total: number;
  tokens_out_total: number;
  error_breakdown: Record<string, number>;
  quality_avg: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get(`${API_BASE}/obs-metrics`, {
          timeout: 5000,
        });
        setMetrics(response.data);
        setLastUpdated(new Date());
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
        setLoading(false);
      }
    };

    // Fetch immediately
    fetchMetrics();

    // Set up auto-refresh every 5 seconds
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <div className="p-6 bg-slate-900 rounded-lg border border-slate-700">
        <p className="text-slate-400">Loading metrics...</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="p-6 bg-red-900/20 rounded-lg border border-red-700">
        <p className="text-red-400">Failed to load metrics. Is the backend running?</p>
      </div>
    );
  }

  const errorCount = Object.values(metrics.error_breakdown).reduce((a, b) => a + b, 0);
  const errorRate = metrics.traffic > 0 ? ((errorCount / metrics.traffic) * 100).toFixed(2) : '0.00';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-100">📊 Observability Dashboard</h2>
        {lastUpdated && (
          <p className="text-xs text-slate-400">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* 6-Panel Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Panel 1: Requests & Traffic */}
        <div className="bg-gradient-to-br from-blue-900/30 to-blue-950/30 p-4 rounded-lg border border-blue-700/50">
          <h3 className="text-sm font-semibold text-blue-300 mb-2">📡 Requests (24h)</h3>
          <p className="text-3xl font-bold text-blue-100">{metrics.traffic}</p>
          <p className="text-xs text-blue-400 mt-1">Total requests processed</p>
        </div>

        {/* Panel 2: Latency P50 */}
        <div className="bg-gradient-to-br from-green-900/30 to-green-950/30 p-4 rounded-lg border border-green-700/50">
          <h3 className="text-sm font-semibold text-green-300 mb-2">⚡ Latency P50</h3>
          <p className="text-3xl font-bold text-green-100">{Math.round(metrics.latency_p50)}ms</p>
          <p className="text-xs text-green-400 mt-1">Median response time</p>
        </div>

        {/* Panel 3: Latency P95 */}
        <div className={`p-4 rounded-lg border ${
          metrics.latency_p95 > 5000
            ? 'bg-gradient-to-br from-red-900/30 to-red-950/30 border-red-700/50'
            : 'bg-gradient-to-br from-orange-900/30 to-orange-950/30 border-orange-700/50'
        }`}>
          <h3 className={`text-sm font-semibold mb-2 ${
            metrics.latency_p95 > 5000 ? 'text-red-300' : 'text-orange-300'
          }`}>
            ⏱️ Latency P95
          </h3>
          <p className={`text-3xl font-bold ${
            metrics.latency_p95 > 5000 ? 'text-red-100' : 'text-orange-100'
          }`}>
            {Math.round(metrics.latency_p95)}ms
          </p>
          <p className={`text-xs mt-1 ${
            metrics.latency_p95 > 5000 ? 'text-red-400' : 'text-orange-400'
          }`}>
            {metrics.latency_p95 > 5000 ? '⚠️ Above SLO (5000ms)' : 'Tail latency'}
          </p>
        </div>

        {/* Panel 4: Error Rate */}
        <div className={`p-4 rounded-lg border ${
          errorCount > 0
            ? 'bg-gradient-to-br from-red-900/30 to-red-950/30 border-red-700/50'
            : 'bg-gradient-to-br from-emerald-900/30 to-emerald-950/30 border-emerald-700/50'
        }`}>
          <h3 className={`text-sm font-semibold mb-2 ${
            errorCount > 0 ? 'text-red-300' : 'text-emerald-300'
          }`}>
            ❌ Error Rate
          </h3>
          <p className={`text-3xl font-bold ${
            errorCount > 0 ? 'text-red-100' : 'text-emerald-100'
          }`}>
            {errorRate}%
          </p>
          <p className={`text-xs mt-1 ${
            errorCount > 0 ? 'text-red-400' : 'text-emerald-400'
          }`}>
            {errorCount} errors detected
          </p>
        </div>

        {/* Panel 5: Cost Tracking */}
        <div className="bg-gradient-to-br from-purple-900/30 to-purple-950/30 p-4 rounded-lg border border-purple-700/50">
          <h3 className="text-sm font-semibold text-purple-300 mb-2">💰 Total Cost</h3>
          <p className="text-3xl font-bold text-purple-100">${metrics.total_cost_usd.toFixed(4)}</p>
          <p className="text-xs text-purple-400 mt-1">
            Avg: ${metrics.avg_cost_usd.toFixed(6)}/req
          </p>
        </div>

        {/* Panel 6: Token Usage & Quality */}
        <div className="bg-gradient-to-br from-indigo-900/30 to-indigo-950/30 p-4 rounded-lg border border-indigo-700/50">
          <h3 className="text-sm font-semibold text-indigo-300 mb-2">🎯 Quality Score</h3>
          <p className="text-3xl font-bold text-indigo-100">{(metrics.quality_avg * 100).toFixed(0)}%</p>
          <p className="text-xs text-indigo-400 mt-1">
            Tokens: {metrics.tokens_in_total + metrics.tokens_out_total} total
          </p>
        </div>
      </div>

      {/* Error Breakdown */}
      {errorCount > 0 && (
        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Error Breakdown</h3>
          <div className="space-y-2">
            {Object.entries(metrics.error_breakdown).map(([errorType, count]) => (
              <div key={errorType} className="flex justify-between items-center">
                <span className="text-sm text-slate-400">{errorType}</span>
                <span className="text-sm font-semibold text-red-400">{count} occurrences</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SLO Status */}
      <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">📈 SLO Status</h3>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">Latency P95 Target</span>
            <span className={`text-sm font-semibold ${
              metrics.latency_p95 <= 5000 ? 'text-green-400' : 'text-red-400'
            }`}>
              {metrics.latency_p95 <= 5000 ? '✅ PASS' : '❌ MISS'} (5000ms target)
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">Error Rate Target</span>
            <span className={`text-sm font-semibold ${
              parseFloat(errorRate) <= 2 ? 'text-green-400' : 'text-red-400'
            }`}>
              {parseFloat(errorRate) <= 2 ? '✅ PASS' : '❌ MISS'} (2% target)
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">Cost Budget (Daily)</span>
            <span className={`text-sm font-semibold ${
              metrics.total_cost_usd <= 8.0 ? 'text-green-400' : 'text-orange-400'
            }`}>
              ${metrics.total_cost_usd.toFixed(2)} (${8.0} limit)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

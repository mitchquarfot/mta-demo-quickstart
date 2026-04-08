import { useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, Legend,
} from "recharts";
import { useCurrentAllocation, useMmmResponseCurves, useForecast, useMmmCoefficients } from "../lib/hooks";
import { CHANNEL_COLORS, fmt, tooltipFmt } from "../lib/format";
import { useFilters } from "../lib/FilterContext";
import FilterBar from "../components/FilterBar";

export default function CampaignPlanner() {
  const { excludeParam } = useFilters();
  const ex = excludeParam || undefined;
  const { data: currentAlloc, isLoading } = useCurrentAllocation(ex);
  const { data: curves } = useMmmResponseCurves(ex);
  const { data: forecast } = useForecast(ex);
  const { data: coefficients } = useMmmCoefficients(ex);
  const [budget, setBudget] = useState(750);
  const [optimized, setOptimized] = useState<any>(null);
  const [optimizing, setOptimizing] = useState(false);

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  const totalCurrentSpend = (currentAlloc ?? []).reduce(
    (s: number, c: any) => s + Number(c.AVG_WEEKLY_SPEND), 0
  );

  const handleOptimize = async () => {
    setOptimizing(true);
    try {
      const res = await fetch("/api/v1/optimize-budget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ total_budget: budget, exclude_channels: excludeParam }),
      });
      setOptimized(await res.json());
    } finally {
      setOptimizing(false);
    }
  };

  const curvesByChannel: Record<string, any[]> = {};
  (curves ?? []).forEach((r: any) => {
    const ch = r.CHANNEL;
    if (!curvesByChannel[ch]) curvesByChannel[ch] = [];
    curvesByChannel[ch].push({ spend: Number(r.SPEND), revenue: Number(r.PREDICTED_REVENUE) });
  });

  const forecastData = (forecast?.forecast ?? []).reduce((acc: Record<string, any>, r: any) => {
    const key = r.WEEK_START;
    if (!acc[key]) acc[key] = { week: key.substring(0, 10) };
    acc[key][r.CHANNEL] = Number(r.VALUE);
    return acc;
  }, {});
  const forecastChartData = Object.values(forecastData);
  const channels = [...new Set((forecast?.forecast ?? []).map((r: any) => r.CHANNEL))];

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-sf-dark">Campaign Planner</h2>

      <FilterBar showDateRange={false} />

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-sm font-semibold mb-4">Budget Optimizer</h3>
        <div className="flex items-center gap-4 mb-4">
          <label className="text-sm text-gray-600">Weekly Budget:</label>
          <input
            type="range"
            min={100}
            max={3000}
            step={50}
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="flex-1"
          />
          <span className="text-lg font-bold text-sf-dark w-24 text-right">{fmt.usd(budget)}</span>
          <button
            onClick={handleOptimize}
            disabled={optimizing}
            className="px-4 py-2 bg-sf-blue text-white rounded-lg text-sm font-medium hover:bg-sf-blue/90 disabled:opacity-50"
          >
            {optimizing ? "Optimizing..." : "Optimize"}
          </button>
        </div>
        <p className="text-xs text-gray-400">
          Current avg weekly spend: {fmt.usd(Math.round(totalCurrentSpend))}
        </p>
      </div>

      {optimized && optimized.allocations && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <h3 className="text-sm font-semibold mb-2">Optimized Allocation</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={optimized.allocations} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(v) => `$${v}`} />
                <YAxis type="category" dataKey="channel" width={60} tick={{ fontSize: 12 }} />
                <Tooltip formatter={tooltipFmt(fmt.usd)} />
                <Bar dataKey="optimized_spend" name="Spend">
                  {optimized.allocations.map((d: any) => (
                    <Cell key={d.channel} fill={CHANNEL_COLORS[d.channel] ?? "#94a3b8"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-3 grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-xs text-gray-500">Total Budget</div>
                <div className="text-sm font-bold">{fmt.usd(optimized.total_budget)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Predicted Revenue</div>
                <div className="text-sm font-bold">{fmt.usd(optimized.total_predicted_revenue)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">ROAS</div>
                <div className="text-sm font-bold">{fmt.roas(optimized.overall_roas)}</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <h3 className="text-sm font-semibold mb-2">Predicted ROAS by Channel</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={optimized.allocations}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="channel" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(v) => `${v.toFixed(1)}x`} />
                <Tooltip formatter={tooltipFmt(fmt.roas)} />
                <Bar dataKey="roas" name="ROAS">
                  {optimized.allocations.map((d: any) => (
                    <Cell key={d.channel} fill={CHANNEL_COLORS[d.channel] ?? "#94a3b8"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {coefficients && coefficients.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-semibold mb-2">MMM Coefficients (Log-Log)</h3>
          <div className="overflow-auto">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 text-left font-medium text-gray-500 uppercase">
                <tr>
                  <th className="px-3 py-2">Channel</th>
                  <th className="px-3 py-2 text-right">β (Elasticity)</th>
                  <th className="px-3 py-2 text-right">R²</th>
                  <th className="px-3 py-2 text-right">Total Spend</th>
                  <th className="px-3 py-2 text-right">Total Revenue</th>
                  <th className="px-3 py-2 text-right">ROAS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {coefficients.map((c: any) => (
                  <tr key={c.CHANNEL} className="hover:bg-gray-50">
                    <td className="px-3 py-2 font-medium">{c.CHANNEL}</td>
                    <td className="px-3 py-2 text-right">{Number(c.BETA).toFixed(3)}</td>
                    <td className="px-3 py-2 text-right">{Number(c.R_SQUARED).toFixed(3)}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(c.TOTAL_SPEND))}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(c.TOTAL_REVENUE))}</td>
                    <td className="px-3 py-2 text-right">{fmt.roas(Number(c.ROAS))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {Object.keys(curvesByChannel).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-semibold mb-2">Response Curves</h3>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="spend"
                type="number"
                tickFormatter={(v) => `$${v}`}
                allowDuplicatedCategory={false}
              />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={tooltipFmt(fmt.usd)} />
              <Legend />
              {Object.entries(curvesByChannel).map(([ch, data]) => (
                <Line
                  key={ch}
                  data={data}
                  dataKey="revenue"
                  name={ch}
                  stroke={CHANNEL_COLORS[ch] ?? "#94a3b8"}
                  dot={false}
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {forecastChartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-semibold mb-2">12-Week Revenue Forecast by Channel</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={forecastChartData as any[]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={tooltipFmt(fmt.usd)} />
              <Legend />
              {(channels as string[]).map((ch) => (
                <Bar
                  key={ch}
                  dataKey={ch}
                  stackId="a"
                  fill={CHANNEL_COLORS[ch] ?? "#94a3b8"}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

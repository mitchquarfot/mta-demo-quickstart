import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { useChannelSummary, useChannelPerformance } from "../lib/hooks";
import { CHANNEL_COLORS, fmt, tooltipFmt } from "../lib/format";
import { useFilters } from "../lib/FilterContext";
import FilterBar from "../components/FilterBar";

const MODELS = ["linear", "last_touch", "first_touch", "time_decay", "position_based", "shapley"];

export default function ChannelPerformance() {
  const [model, setModel] = useState("linear");
  const { excludeParam } = useFilters();
  const { data: summary, isLoading } = useChannelSummary(model, excludeParam || undefined);
  const { data: detail } = useChannelPerformance(model, excludeParam || undefined);

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  const roasData = (summary ?? []).map((d: any) => ({
    channel: d.CHANNEL,
    roas: Number(d.ROAS),
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-sf-dark">Channel Performance</h2>
        <select value={model} onChange={(e) => setModel(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white">
          {MODELS.map((m) => <option key={m} value={m}>{m.replace("_", " ")}</option>)}
        </select>
      </div>

      <FilterBar showDateRange={false} />

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h3 className="text-sm font-semibold mb-2">ROAS by Channel</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={roasData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="channel" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `${v.toFixed(1)}x`} />
            <Tooltip formatter={tooltipFmt(fmt.roas)} />
            <Bar dataKey="roas">
              {roasData.map((d) => (
                <Cell key={d.channel} fill={CHANNEL_COLORS[d.channel] ?? "#94a3b8"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {(summary ?? []).map((ch: any) => (
          <div key={ch.CHANNEL} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHANNEL_COLORS[ch.CHANNEL] ?? "#94a3b8" }} />
              <span className="text-sm font-semibold">{ch.CHANNEL}</span>
            </div>
            <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
              <span>Spend</span><span className="text-right font-medium text-gray-900">{fmt.usd(Number(ch.SPEND))}</span>
              <span>Revenue</span><span className="text-right font-medium text-gray-900">{fmt.usd(Number(ch.ATTRIBUTED_REVENUE))}</span>
              <span>ROAS</span><span className="text-right font-medium text-gray-900">{fmt.roas(Number(ch.ROAS))}</span>
              <span>CPA</span><span className="text-right font-medium text-gray-900">{fmt.usd(Number(ch.CPA))}</span>
            </div>
          </div>
        ))}
      </div>

      {detail && detail.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-sf-dark mb-3">Detailed Campaign Performance</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto max-h-96">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 text-left font-medium text-gray-500 uppercase sticky top-0">
                <tr>
                  <th className="px-3 py-2">Channel</th>
                  <th className="px-3 py-2">Campaign</th>
                  <th className="px-3 py-2 text-right">Impressions</th>
                  <th className="px-3 py-2 text-right">Spend</th>
                  <th className="px-3 py-2 text-right">Revenue</th>
                  <th className="px-3 py-2 text-right">ROAS</th>
                  <th className="px-3 py-2 text-right">CPA</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {detail.map((r: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{r.CHANNEL}</td>
                    <td className="px-3 py-2">{r.CAMPAIGN_NAME}</td>
                    <td className="px-3 py-2 text-right">{Number(r.IMPRESSIONS).toLocaleString()}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(r.SPEND))}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(r.ATTRIBUTED_REVENUE))}</td>
                    <td className="px-3 py-2 text-right">{fmt.roas(Number(r.ROAS))}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(r.CPA))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

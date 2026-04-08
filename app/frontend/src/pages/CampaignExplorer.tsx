import { useState } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line,
} from "recharts";
import { useCampaigns, useCampaignDaily } from "../lib/hooks";
import { CHANNEL_COLORS, fmt, tooltipFmt } from "../lib/format";
import { useFilters } from "../lib/FilterContext";
import FilterBar from "../components/FilterBar";

export default function CampaignExplorer() {
  const { data: campaigns, isLoading: loadingCampaigns } = useCampaigns();
  const [selected, setSelected] = useState<string>("");
  const { excludeParam, dateStart, dateEnd } = useFilters();

  const campaignId = selected || (campaigns && campaigns.length > 0 ? campaigns[0].CAMPAIGN_ID : "");
  const { data: daily, isLoading: loadingDaily } = useCampaignDaily(
    campaignId, "linear",
    excludeParam || undefined,
    dateStart || undefined,
    dateEnd || undefined,
  );

  if (loadingCampaigns) return <p className="text-gray-500">Loading campaigns...</p>;

  const campaignName = (campaigns ?? []).find((c: any) => c.CAMPAIGN_ID === campaignId)?.CAMPAIGN_NAME ?? campaignId;

  const dates = [...new Set((daily ?? []).map((d: any) => d.REPORT_DATE))].sort();
  const channels = [...new Set((daily ?? []).map((d: any) => d.CHANNEL))];

  const impData = dates.map((dt) => {
    const row: any = { date: dt };
    channels.forEach((ch) => {
      const match = (daily ?? []).find((d: any) => d.REPORT_DATE === dt && d.CHANNEL === ch);
      row[ch] = match ? Number(match.IMPRESSIONS) : 0;
    });
    return row;
  });

  const dailyAgg = dates.map((dt) => {
    const rows = (daily ?? []).filter((d: any) => d.REPORT_DATE === dt);
    const spend = rows.reduce((s: number, r: any) => s + Number(r.SPEND), 0);
    const revenue = rows.reduce((s: number, r: any) => s + Number(r.ATTRIBUTED_REVENUE), 0);
    return { date: dt, spend, revenue, roas: spend > 0 ? revenue / spend : 0 };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-sf-dark">Campaign Explorer</h2>
        <select value={campaignId} onChange={(e) => setSelected(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white max-w-xs truncate">
          {(campaigns ?? []).map((c: any) => (
            <option key={c.CAMPAIGN_ID} value={c.CAMPAIGN_ID}>{c.CAMPAIGN_NAME}</option>
          ))}
        </select>
      </div>

      <FilterBar />

      <p className="text-sm text-gray-500">Showing: <strong>{campaignName}</strong></p>

      {loadingDaily ? <p className="text-gray-500">Loading daily data...</p> : daily && daily.length > 0 ? (
        <>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <h3 className="text-sm font-semibold mb-2">Daily Impressions by Channel</h3>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={impData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                {channels.map((ch) => (
                  <Area key={ch} type="monotone" dataKey={ch} stackId="1"
                    fill={CHANNEL_COLORS[ch] ?? "#94a3b8"} stroke={CHANNEL_COLORS[ch] ?? "#94a3b8"} />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
              <h3 className="text-sm font-semibold mb-2">Daily Spend vs Revenue</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={dailyAgg}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                  <YAxis />
                  <Tooltip formatter={tooltipFmt(fmt.usd)} />
                  <Legend />
                  <Line type="monotone" dataKey="spend" stroke="#EF4444" name="Spend" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="revenue" stroke="#10B981" name="Revenue" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
              <h3 className="text-sm font-semibold mb-2">Daily ROAS Trend</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={dailyAgg}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                  <YAxis tickFormatter={(v) => `${v.toFixed(1)}x`} />
                  <Tooltip formatter={tooltipFmt(fmt.roas)} />
                  <Line type="monotone" dataKey="roas" stroke="#29B5E8" name="ROAS" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto max-h-80">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 text-left font-medium text-gray-500 uppercase sticky top-0">
                <tr>
                  <th className="px-3 py-2">Date</th>
                  <th className="px-3 py-2">Channel</th>
                  <th className="px-3 py-2 text-right">Impressions</th>
                  <th className="px-3 py-2 text-right">Spend</th>
                  <th className="px-3 py-2 text-right">Revenue</th>
                  <th className="px-3 py-2 text-right">ROAS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {daily.map((r: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{r.REPORT_DATE}</td>
                    <td className="px-3 py-2">{r.CHANNEL}</td>
                    <td className="px-3 py-2 text-right">{Number(r.IMPRESSIONS).toLocaleString()}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(r.SPEND))}</td>
                    <td className="px-3 py-2 text-right">{fmt.usd(Number(r.ATTRIBUTED_REVENUE))}</td>
                    <td className="px-3 py-2 text-right">{fmt.roas(Number(r.ROAS))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <p className="text-gray-500">No daily data available for this campaign.</p>
      )}
    </div>
  );
}

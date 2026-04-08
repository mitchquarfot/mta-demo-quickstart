import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useUnifiedMeasurement } from "../lib/hooks";
import { fmt, tooltipFmt } from "../lib/format";
import { useFilters } from "../lib/FilterContext";
import FilterBar from "../components/FilterBar";

export default function UnifiedMeasurement() {
  const { excludeParam, dateStart, dateEnd } = useFilters();
  const { data, isLoading } = useUnifiedMeasurement(
    excludeParam || undefined,
    dateStart || undefined,
    dateEnd || undefined,
  );

  if (isLoading) return <p className="text-gray-500">Loading...</p>;
  if (!data) return <p className="text-red-500">Failed to load data</p>;

  const { mta, mmm, incrementality } = data;

  const mmmMap: Record<string, any> = {};
  (mmm ?? []).forEach((d: any) => { mmmMap[d.CHANNEL] = d; });

  const combined = (mta ?? []).map((d: any) => {
    const m = mmmMap[d.CHANNEL];
    const spend = m ? Number(m.TOTAL_SPEND) : 0;
    return {
      channel: d.CHANNEL,
      mta_revenue: Number(d.MTA_REVENUE),
      mta_roas: spend > 0 ? Number(d.MTA_REVENUE) / spend : 0,
      mmm_roas: m ? Number(m.MMM_ROAS) : 0,
      spend,
    };
  });

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-sf-dark">Unified Measurement: MTA vs MMM vs Incrementality</h2>

      <FilterBar />

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h3 className="text-sm font-semibold mb-2">ROAS Comparison: MTA vs MMM by Channel</h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={combined}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="channel" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `${v.toFixed(1)}x`} />
            <Tooltip formatter={tooltipFmt(fmt.roas)} />
            <Legend />
            <Bar dataKey="mta_roas" fill="#29B5E8" name="MTA ROAS" />
            <Bar dataKey="mmm_roas" fill="#F59E0B" name="MMM ROAS" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto">
        <h3 className="text-sm font-semibold px-4 pt-4 mb-2">Measurement Triangulation Table</h3>
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3">Channel</th>
              <th className="px-4 py-3 text-right">MTA Revenue</th>
              <th className="px-4 py-3 text-right">Total Spend</th>
              <th className="px-4 py-3 text-right">MTA ROAS</th>
              <th className="px-4 py-3 text-right">MMM ROAS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {combined.map((r: any) => (
              <tr key={r.channel} className="hover:bg-gray-50">
                <td className="px-4 py-2 font-medium">{r.channel}</td>
                <td className="px-4 py-2 text-right">{fmt.usd(r.mta_revenue)}</td>
                <td className="px-4 py-2 text-right">{fmt.usd(r.spend)}</td>
                <td className="px-4 py-2 text-right">{fmt.roas(r.mta_roas)}</td>
                <td className="px-4 py-2 text-right">{fmt.roas(r.mmm_roas)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {incrementality && incrementality.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-sf-dark mb-3">Incrementality Test Results</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase">
                <tr>
                  {Object.keys(incrementality[0]).map((k) => (
                    <th key={k} className="px-4 py-3">{k.replace(/_/g, " ")}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {incrementality.map((r: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    {Object.values(r).map((v: any, j) => (
                      <td key={j} className="px-4 py-2 whitespace-nowrap">{typeof v === "number" ? v.toLocaleString() : String(v ?? "")}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="bg-sf-dark/5 rounded-xl p-4 text-sm text-gray-600">
        <p className="font-semibold mb-1">Interpretation Guide:</p>
        <ul className="list-disc pl-5 space-y-1">
          <li><strong>MTA</strong> captures user-level touchpoint credit but misses cross-device/offline impact</li>
          <li><strong>MMM</strong> captures macro channel effects but lacks user-level granularity</li>
          <li><strong>Incrementality</strong> provides causal lift measurement but only for tested channels/geos</li>
          <li>When all three agree on a channel's contribution, confidence is highest</li>
        </ul>
      </div>
    </div>
  );
}

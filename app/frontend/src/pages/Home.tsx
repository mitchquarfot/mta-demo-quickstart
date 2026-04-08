import KPICard from "../components/KPICard";
import { useKpis, usePopulation, useDedupReport } from "../lib/hooks";
import { fmt } from "../lib/format";

export default function Home() {
  const { data: kpi, isLoading } = useKpis();
  const { data: pop } = usePopulation();
  const { data: dedup } = useDedupReport();

  if (isLoading) return <p className="text-gray-500">Loading...</p>;
  if (!kpi) return <p className="text-red-500">Failed to load KPIs</p>;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-sf-dark">Identity Health & Signal Loss Monitor</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Total Impressions" value={fmt.num(kpi.total_impressions)} />
        <KPICard label="Total Clicks" value={fmt.num(kpi.total_clicks)} />
        <KPICard label="Total Conversions" value={fmt.num(kpi.total_conversions)} />
        <KPICard label="Total Spend" value={fmt.usd(kpi.total_spend)} />
        <KPICard label="Total Revenue" value={fmt.usd(kpi.total_revenue)} />
        <KPICard label="Identity Match Rate" value={fmt.pct(kpi.identity_match_rate)} />
        <KPICard label="ITP-Affected Rate" value={fmt.pct(kpi.itp_affected_rate)} />
        <KPICard label="Consent-Blocked" value={fmt.pct(kpi.consent_blocked_rate)} />
      </div>

      {dedup && dedup.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-sf-dark mb-3">Conversion Deduplication Summary</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase">
                <tr>
                  {Object.keys(dedup[0]).map((k) => (
                    <th key={k} className="px-4 py-3">{k.replace(/_/g, " ")}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {dedup.map((r: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    {Object.values(r).map((v: any, j) => (
                      <td key={j} className="px-4 py-2 whitespace-nowrap">{typeof v === "number" ? v.toLocaleString() : String(v)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {pop && pop.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-sf-dark mb-3">Population Breakdown</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase">
                <tr>
                  <th className="px-4 py-3">Segment</th>
                  <th className="px-4 py-3">People</th>
                  <th className="px-4 py-3">Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {pop.map((r: any) => (
                  <tr key={r.SEGMENT} className="hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium">{r.SEGMENT}</td>
                    <td className="px-4 py-2">{Number(r.PEOPLE).toLocaleString()}</td>
                    <td className="px-4 py-2">{fmt.pct(Number(r.SHARE))}</td>
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

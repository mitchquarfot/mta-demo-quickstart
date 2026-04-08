import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { useIncrementality, useFootTraffic } from "../lib/hooks";
import KPICard from "../components/KPICard";
import { fmt, tooltipFmt } from "../lib/format";

export default function Incrementality() {
  const { data: incr, isLoading } = useIncrementality();
  const { data: ft } = useFootTraffic();

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  const treatment = (incr ?? []).find((d: any) => d.TEST_GROUP === "treatment");
  const control = (incr ?? []).find((d: any) => d.TEST_GROUP === "control");
  const lift = treatment?.INCREMENTAL_LIFT;

  const barData = (incr ?? []).map((d: any) => ({
    group: d.TEST_GROUP,
    visits: Number(d.TOTAL_VISITS),
  }));

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-sf-dark">Foot Traffic & Incrementality</h2>

      <div className="grid grid-cols-3 gap-4">
        <KPICard label="Treatment Visits" value={treatment ? fmt.num(Number(treatment.TOTAL_VISITS)) : "-"} />
        <KPICard label="Control Visits" value={control ? fmt.num(Number(control.TOTAL_VISITS)) : "-"} />
        <KPICard label="Incremental Lift" value={lift ? fmt.pct(Number(lift)) : "N/A"} />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h3 className="text-sm font-semibold mb-2">Total Store Visits: Treatment vs Control</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="group" />
            <YAxis />
            <Tooltip formatter={tooltipFmt((v) => v.toLocaleString())} />
            <Bar dataKey="visits">
              {barData.map((d) => (
                <Cell key={d.group} fill={d.group === "treatment" ? "#29B5E8" : "#94a3b8"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {incr && incr.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase">
              <tr>
                {Object.keys(incr[0]).map((k) => (
                  <th key={k} className="px-4 py-3">{k.replace(/_/g, " ")}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {incr.map((r: any, i: number) => (
                <tr key={i} className="hover:bg-gray-50">
                  {Object.values(r).map((v: any, j) => (
                    <td key={j} className="px-4 py-2 whitespace-nowrap">{typeof v === "number" ? v.toLocaleString() : String(v ?? "")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {ft && ft.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-sf-dark mb-3">Foot Traffic by DMA</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto max-h-80">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-2">DMA</th>
                  <th className="px-4 py-2 text-right">Visits</th>
                  <th className="px-4 py-2 text-right">Unique Visitors</th>
                  <th className="px-4 py-2 text-right">Avg Dwell (min)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {ft.map((r: any) => (
                  <tr key={r.DMA_CODE} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{r.DMA_NAME} ({r.DMA_CODE})</td>
                    <td className="px-4 py-2 text-right">{Number(r.VISITS).toLocaleString()}</td>
                    <td className="px-4 py-2 text-right">{Number(r.UNIQUE_VISITORS).toLocaleString()}</td>
                    <td className="px-4 py-2 text-right">{Number(r.AVG_DWELL).toFixed(1)}</td>
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

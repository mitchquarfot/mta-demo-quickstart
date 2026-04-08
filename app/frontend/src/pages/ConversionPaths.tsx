import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line,
} from "recharts";
import { usePathStats, useTopSequences, useFrequency, useChannelPosition } from "../lib/hooks";
import { CHANNEL_COLORS } from "../lib/format";
import { useFilters } from "../lib/FilterContext";
import FilterBar from "../components/FilterBar";

export default function ConversionPaths() {
  const { excludeParam } = useFilters();
  const ex = excludeParam || undefined;
  const { data: stats, isLoading } = usePathStats(ex);
  const { data: seqs } = useTopSequences(ex);
  const { data: freq } = useFrequency(ex);
  const { data: pos } = useChannelPosition(ex);

  if (isLoading) return <p className="text-gray-500">Loading...</p>;

  const channels = [...new Set((freq ?? []).map((d: any) => d.CHANNEL))];
  const buckets = [...new Set((freq ?? []).map((d: any) => d.FREQUENCY_BUCKET))].sort((a, b) => Number(a) - Number(b));
  const freqData = buckets.map((b) => {
    const row: any = { bucket: b };
    channels.forEach((ch) => {
      const match = (freq ?? []).find((d: any) => d.CHANNEL === ch && d.FREQUENCY_BUCKET === b);
      row[ch] = match ? Number(match.UNIQUE_USERS) : 0;
    });
    return row;
  });

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-sf-dark">Conversion Paths & Frequency</h2>

      <FilterBar showDateRange={false} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-semibold mb-2">Conversions by Path Length</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="PATH_LENGTH" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="CONVERSIONS" fill="#29B5E8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-semibold mb-2">Avg Hours to Convert by Path Length</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={stats ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="PATH_LENGTH" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="AVG_HOURS_TO_CONVERT" stroke="#8B5CF6" strokeWidth={2} dot />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {pos && pos.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h3 className="text-sm font-semibold mb-2">Channel Position in Conversion Paths</h3>
          <div className="overflow-auto">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 text-left font-medium text-gray-500 uppercase">
                <tr>
                  <th className="px-3 py-2">Channel</th>
                  <th className="px-3 py-2 text-right">Avg Position</th>
                  <th className="px-3 py-2 text-right">Avg Relative Pos</th>
                  <th className="px-3 py-2 text-right">First Touch</th>
                  <th className="px-3 py-2 text-right">Last Touch</th>
                  <th className="px-3 py-2 text-right">Total Touchpoints</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {pos.map((r: any) => (
                  <tr key={r.CHANNEL} className="hover:bg-gray-50">
                    <td className="px-3 py-2 font-medium">{r.CHANNEL}</td>
                    <td className="px-3 py-2 text-right">{Number(r.AVG_POSITION).toFixed(1)}</td>
                    <td className="px-3 py-2 text-right">{Number(r.AVG_RELATIVE_POSITION).toFixed(3)}</td>
                    <td className="px-3 py-2 text-right">{Number(r.FIRST_TOUCH_COUNT).toLocaleString()}</td>
                    <td className="px-3 py-2 text-right">{Number(r.LAST_TOUCH_COUNT).toLocaleString()}</td>
                    <td className="px-3 py-2 text-right">{Number(r.TOTAL_TOUCHPOINTS_IN_PATHS).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {seqs && seqs.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-sf-dark mb-3">Top Channel Sequences</h3>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-auto max-h-80">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-2">#</th>
                  <th className="px-4 py-2">Path</th>
                  <th className="px-4 py-2 text-right">Conversions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {seqs.map((r: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-gray-400">{i + 1}</td>
                    <td className="px-4 py-2 font-mono text-xs">{r.PATH}</td>
                    <td className="px-4 py-2 text-right font-medium">{Number(r.CONVERSIONS).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h3 className="text-sm font-semibold mb-2">User Frequency Distribution by Channel</h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={freqData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="bucket" />
            <YAxis />
            <Tooltip />
            <Legend />
            {channels.map((ch) => (
              <Bar key={ch} dataKey={ch} fill={CHANNEL_COLORS[ch] ?? "#94a3b8"} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

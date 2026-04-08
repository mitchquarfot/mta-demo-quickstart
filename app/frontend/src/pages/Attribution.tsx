import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useAttribution, useAdvertisers } from "../lib/hooks";
import { MODEL_COLORS, fmt, tooltipFmt } from "../lib/format";
import { useFilters } from "../lib/FilterContext";
import FilterBar from "../components/FilterBar";

const ALL_MODELS = ["last_touch", "first_touch", "linear", "time_decay", "position_based", "shapley"];

export default function Attribution() {
  const { data: advs } = useAdvertisers();
  const [adv, setAdv] = useState<string>("");
  const [models, setModels] = useState<string[]>(ALL_MODELS);
  const { excludeParam, dateStart, dateEnd } = useFilters();

  const { data, isLoading } = useAttribution(
    adv || undefined,
    models.join(","),
    excludeParam || undefined,
    dateStart || undefined,
    dateEnd || undefined,
  );

  const toggleModel = (m: string) =>
    setModels((prev) => (prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m]));

  const channels = [...new Set((data ?? []).map((d: any) => d.CHANNEL))];
  const revenueData = channels.map((ch) => {
    const row: any = { channel: ch };
    models.forEach((m) => {
      const match = (data ?? []).find((d: any) => d.CHANNEL === ch && d.MODEL_TYPE === m);
      row[m] = match ? Number(match.REVENUE) : 0;
    });
    return row;
  });
  const convData = channels.map((ch) => {
    const row: any = { channel: ch };
    models.forEach((m) => {
      const match = (data ?? []).find((d: any) => d.CHANNEL === ch && d.MODEL_TYPE === m);
      row[m] = match ? Number(match.CONVERSIONS) : 0;
    });
    return row;
  });

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-sf-dark">Attribution Model Comparison</h2>

      <FilterBar />

      <div className="flex flex-wrap gap-4 items-center">
        <select value={adv} onChange={(e) => setAdv(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white">
          <option value="">All Advertisers</option>
          {(advs ?? []).map((a: any) => (
            <option key={a.ADVERTISER_ID} value={a.ADVERTISER_ID}>{a.ADVERTISER_ID}</option>
          ))}
        </select>
        <div className="flex gap-2">
          {ALL_MODELS.map((m) => (
            <button key={m} onClick={() => toggleModel(m)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                models.includes(m) ? "text-white" : "bg-gray-100 text-gray-500"
              }`}
              style={models.includes(m) ? { backgroundColor: MODEL_COLORS[m] } : {}}>
              {m.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? <p className="text-gray-500">Loading...</p> : (
        <>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <h3 className="text-sm font-semibold mb-2">Attributed Revenue by Channel & Model</h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="channel" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={tooltipFmt(fmt.usd)} />
                <Legend />
                {models.map((m) => (
                  <Bar key={m} dataKey={m} fill={MODEL_COLORS[m]} name={m.replace("_", " ")} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <h3 className="text-sm font-semibold mb-2">Attributed Conversions by Channel & Model</h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={convData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="channel" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip formatter={tooltipFmt((v) => v.toFixed(1))} />
                <Legend />
                {models.map((m) => (
                  <Bar key={m} dataKey={m} fill={MODEL_COLORS[m]} name={m.replace("_", " ")} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}

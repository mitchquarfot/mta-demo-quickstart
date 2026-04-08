import { useFilters } from "../lib/FilterContext";
import { CHANNEL_COLORS } from "../lib/format";

interface Props {
  showDateRange?: boolean;
}

export default function FilterBar({ showDateRange = true }: Props) {
  const { allChannels, excludedChannels, toggleChannel, dateStart, dateEnd, setDateStart, setDateEnd, resetFilters } =
    useFilters();

  const hasFilters = excludedChannels.size > 0 || dateStart || dateEnd;

  return (
    <div className="flex flex-wrap items-center gap-3 bg-white rounded-xl shadow-sm border border-gray-100 px-4 py-3">
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Channels</span>
      <div className="flex flex-wrap gap-1.5">
        {allChannels.map((ch) => {
          const active = !excludedChannels.has(ch);
          return (
            <button
              key={ch}
              onClick={() => toggleChannel(ch)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all ${
                active ? "text-white shadow-sm" : "bg-gray-100 text-gray-400 line-through"
              }`}
              style={active ? { backgroundColor: CHANNEL_COLORS[ch] ?? "#94a3b8" } : {}}
            >
              {ch}
            </button>
          );
        })}
      </div>

      {showDateRange && (
        <>
          <div className="w-px h-6 bg-gray-200 mx-1" />
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Date Range</span>
          <input
            type="date"
            value={dateStart}
            onChange={(e) => setDateStart(e.target.value)}
            className="border rounded-lg px-2 py-1 text-xs bg-white"
          />
          <span className="text-xs text-gray-400">to</span>
          <input
            type="date"
            value={dateEnd}
            onChange={(e) => setDateEnd(e.target.value)}
            className="border rounded-lg px-2 py-1 text-xs bg-white"
          />
        </>
      )}

      {hasFilters && (
        <>
          <div className="w-px h-6 bg-gray-200 mx-1" />
          <button
            onClick={resetFilters}
            className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
          >
            Reset
          </button>
        </>
      )}
    </div>
  );
}

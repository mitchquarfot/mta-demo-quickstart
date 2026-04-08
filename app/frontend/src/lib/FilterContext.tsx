import { createContext, useContext, useState, ReactNode } from "react";

const ALL_CHANNELS = ["search", "social", "display", "ctv", "olv", "native", "audio", "dooh"];

interface FilterState {
  excludedChannels: Set<string>;
  toggleChannel: (ch: string) => void;
  dateStart: string;
  dateEnd: string;
  setDateStart: (v: string) => void;
  setDateEnd: (v: string) => void;
  allChannels: string[];
  activeChannels: string[];
  excludeParam: string;
  resetFilters: () => void;
}

const FilterContext = createContext<FilterState | null>(null);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [excludedChannels, setExcluded] = useState<Set<string>>(new Set());
  const [dateStart, setDateStart] = useState("");
  const [dateEnd, setDateEnd] = useState("");

  const toggleChannel = (ch: string) =>
    setExcluded((prev) => {
      const next = new Set(prev);
      if (next.has(ch)) next.delete(ch);
      else next.add(ch);
      return next;
    });

  const activeChannels = ALL_CHANNELS.filter((ch) => !excludedChannels.has(ch));
  const excludeParam = [...excludedChannels].join(",");

  const resetFilters = () => {
    setExcluded(new Set());
    setDateStart("");
    setDateEnd("");
  };

  return (
    <FilterContext.Provider
      value={{
        excludedChannels,
        toggleChannel,
        dateStart,
        dateEnd,
        setDateStart,
        setDateEnd,
        allChannels: ALL_CHANNELS,
        activeChannels,
        excludeParam,
        resetFilters,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error("useFilters must be inside FilterProvider");
  return ctx;
}

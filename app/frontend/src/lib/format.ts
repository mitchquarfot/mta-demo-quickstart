export const fmt = {
  num: (v: number) => v?.toLocaleString() ?? "0",
  pct: (v: number) => `${(v * 100).toFixed(1)}%`,
  usd: (v: number) => `$${v?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
  roas: (v: number) => `${v?.toFixed(2)}x`,
};

export const tooltipFmt = (fn: (v: number) => string) => (v: any) => fn(Number(v ?? 0));

export const CHANNEL_COLORS: Record<string, string> = {
  search: "#4F46E5",
  social: "#0EA5E9",
  display: "#F59E0B",
  video: "#10B981",
  ctv: "#8B5CF6",
  olv: "#06B6D4",
  audio: "#EC4899",
  native: "#F97316",
  dooh: "#6B7280",
};

export const MODEL_COLORS: Record<string, string> = {
  linear: "#29B5E8",
  last_touch: "#F59E0B",
  first_touch: "#10B981",
  time_decay: "#8B5CF6",
  position_based: "#EC4899",
  shapley: "#EF4444",
};

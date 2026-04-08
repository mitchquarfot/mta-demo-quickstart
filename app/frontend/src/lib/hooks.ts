import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "../lib/api";

function filterQs(exclude?: string, dateStart?: string, dateEnd?: string): string {
  const p = new URLSearchParams();
  if (exclude) p.set("exclude_channels", exclude);
  if (dateStart) p.set("date_start", dateStart);
  if (dateEnd) p.set("date_end", dateEnd);
  const s = p.toString();
  return s ? `&${s}` : "";
}

function filterQsFirst(exclude?: string, dateStart?: string, dateEnd?: string): string {
  const p = new URLSearchParams();
  if (exclude) p.set("exclude_channels", exclude);
  if (dateStart) p.set("date_start", dateStart);
  if (dateEnd) p.set("date_end", dateEnd);
  const s = p.toString();
  return s ? `?${s}` : "";
}

export function useKpis() {
  return useQuery({ queryKey: ["kpis"], queryFn: () => fetchApi<any>("/kpis") });
}
export function useAttribution(advertiserId?: string, models?: string, exclude?: string, dateStart?: string, dateEnd?: string) {
  const params = new URLSearchParams();
  if (advertiserId) params.set("advertiser_id", advertiserId);
  if (models) params.set("models", models);
  if (exclude) params.set("exclude_channels", exclude);
  if (dateStart) params.set("date_start", dateStart);
  if (dateEnd) params.set("date_end", dateEnd);
  const qs = params.toString() ? `?${params}` : "";
  return useQuery({ queryKey: ["attribution", advertiserId, models, exclude, dateStart, dateEnd], queryFn: () => fetchApi<any[]>(`/attribution${qs}`) });
}
export function useAdvertisers() {
  return useQuery({ queryKey: ["advertisers"], queryFn: () => fetchApi<any[]>("/attribution/advertisers") });
}
export function useChannelSummary(model: string, exclude?: string) {
  const qs = `?model_type=${model}${filterQs(exclude)}`;
  return useQuery({ queryKey: ["channel-summary", model, exclude], queryFn: () => fetchApi<any[]>(`/channel-summary${qs}`) });
}
export function useChannelPerformance(model: string, exclude?: string) {
  const qs = `?model_type=${model}${filterQs(exclude)}`;
  return useQuery({ queryKey: ["channel-performance", model, exclude], queryFn: () => fetchApi<any[]>(`/channel-performance${qs}`) });
}
export function usePathStats(exclude?: string) {
  return useQuery({ queryKey: ["path-stats", exclude], queryFn: () => fetchApi<any[]>(`/conversion-paths/stats${filterQsFirst(exclude)}`) });
}
export function useTopSequences(exclude?: string) {
  const qs = exclude ? `?exclude_channels=${exclude}` : "";
  return useQuery({ queryKey: ["top-sequences", exclude], queryFn: () => fetchApi<any[]>(`/conversion-paths/top-sequences${qs}`) });
}
export function useChannelPosition(exclude?: string) {
  return useQuery({ queryKey: ["channel-position", exclude], queryFn: () => fetchApi<any[]>(`/conversion-paths/channel-position${filterQsFirst(exclude)}`) });
}
export function useFrequency(exclude?: string) {
  return useQuery({ queryKey: ["frequency", exclude], queryFn: () => fetchApi<any[]>(`/frequency${filterQsFirst(exclude)}`) });
}
export function useIncrementality() {
  return useQuery({ queryKey: ["incrementality"], queryFn: () => fetchApi<any[]>("/incrementality") });
}
export function useFootTraffic() {
  return useQuery({ queryKey: ["foot-traffic"], queryFn: () => fetchApi<any[]>("/foot-traffic") });
}
export function useUnifiedMeasurement(exclude?: string, dateStart?: string, dateEnd?: string) {
  const qs = filterQsFirst(exclude, dateStart, dateEnd);
  return useQuery({ queryKey: ["unified", exclude, dateStart, dateEnd], queryFn: () => fetchApi<any>(`/unified-measurement${qs}`) });
}
export function useCampaigns() {
  return useQuery({ queryKey: ["campaigns"], queryFn: () => fetchApi<any[]>("/campaigns") });
}
export function useCampaignDaily(id: string, model: string, exclude?: string, dateStart?: string, dateEnd?: string) {
  const qs = `?model_type=${model}${filterQs(exclude, dateStart, dateEnd)}`;
  return useQuery({ queryKey: ["campaign-daily", id, model, exclude, dateStart, dateEnd], queryFn: () => fetchApi<any[]>(`/campaigns/${id}/daily${qs}`), enabled: !!id });
}
export function useDedupReport() {
  return useQuery({ queryKey: ["dedup"], queryFn: () => fetchApi<any[]>("/dedup-report") });
}
export function usePopulation() {
  return useQuery({ queryKey: ["population"], queryFn: () => fetchApi<any[]>("/population") });
}
export function useForecast(exclude?: string) {
  const qs = filterQsFirst(exclude);
  return useQuery({ queryKey: ["forecast", exclude], queryFn: () => fetchApi<any>(`/forecast${qs}`) });
}
export function useMmmCoefficients(exclude?: string) {
  const qs = filterQsFirst(exclude);
  return useQuery({ queryKey: ["mmm-coefficients", exclude], queryFn: () => fetchApi<any[]>(`/mmm-coefficients${qs}`) });
}
export function useMmmResponseCurves(exclude?: string) {
  const qs = filterQsFirst(exclude);
  return useQuery({ queryKey: ["mmm-response-curves", exclude], queryFn: () => fetchApi<any[]>(`/mmm-response-curves${qs}`) });
}
export function useCurrentAllocation(exclude?: string) {
  const qs = filterQsFirst(exclude);
  return useQuery({ queryKey: ["current-allocation", exclude], queryFn: () => fetchApi<any[]>(`/current-allocation${qs}`) });
}
export function usePropensityDistribution() {
  return useQuery({ queryKey: ["propensity-dist"], queryFn: () => fetchApi<any[]>("/propensity/distribution") });
}
export function usePropensityMetrics() {
  return useQuery({ queryKey: ["propensity-metrics"], queryFn: () => fetchApi<any[]>("/propensity/metrics") });
}

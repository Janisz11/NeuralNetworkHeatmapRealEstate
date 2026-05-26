import { useState, useEffect, useRef } from "react";
import { getHeatmap } from "../api/client";
import type { HeatmapResponse, HeatmapParams } from "../types";

export function useHeatmap(runId: number | null, city: string, params: HeatmapParams) {
  const [data, setData] = useState<HeatmapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!runId) return;

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getHeatmap({ run_id: runId, city, ...params });
        setData(result);
      } catch {
        setError("Failed to fetch heatmap");
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [
    runId, city,
    params.area_min, params.area_max,
    params.floor_min, params.floor_max,
    params.year_min, params.year_max,
    params.resolution,
  ]);

  return { data, loading, error };
}

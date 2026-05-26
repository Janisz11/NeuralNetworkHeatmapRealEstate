import type { HeatmapParams, HeatmapResponse } from "../../types";

interface DualSliderProps {
  label: string;
  lo: number;
  hi: number;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
  disabled: boolean;
  onChange: (lo: number, hi: number) => void;
}

function DualSlider({ label, lo, hi, min, max, step, format, disabled, onChange }: DualSliderProps) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-400">
        <span>{label}</span>
        <span className={`font-medium ${disabled ? "text-gray-500" : "text-white"}`}>
          {format(lo)} – {format(hi)}
        </span>
      </div>
      <div className={`space-y-1 ${disabled ? "opacity-40 pointer-events-none" : ""}`}>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 w-4 shrink-0 text-right">Od</span>
          <input
            type="range" min={min} max={max} step={step} value={lo}
            disabled={disabled}
            onChange={e => onChange(Math.min(Number(e.target.value), hi - step), hi)}
            className="flex-1 accent-blue-500 cursor-pointer disabled:cursor-default"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 w-4 shrink-0 text-right">Do</span>
          <input
            type="range" min={min} max={max} step={step} value={hi}
            disabled={disabled}
            onChange={e => onChange(lo, Math.max(Number(e.target.value), lo + step))}
            className="flex-1 accent-blue-500 cursor-pointer disabled:cursor-default"
          />
        </div>
      </div>
    </div>
  );
}

interface SliderDef {
  labelKey: "area" | "floor" | "year";
  label: string;
  minKey: keyof HeatmapParams;
  maxKey: keyof HeatmapParams;
  absMin: number;
  absMax: number;
  step: number;
  format: (v: number) => string;
  p25Key: keyof HeatmapResponse;
  p75Key: keyof HeatmapResponse;
}

const SLIDERS: SliderDef[] = [
  {
    labelKey: "area", label: "Metraż",
    minKey: "area_min", maxKey: "area_max",
    absMin: 15, absMax: 200, step: 5,
    format: v => `${Math.round(v)} m²`,
    p25Key: "area_p25", p75Key: "area_p75",
  },
  {
    labelKey: "floor", label: "Piętro",
    minKey: "floor_min", maxKey: "floor_max",
    absMin: 0, absMax: 20, step: 1,
    format: v => `${Math.round(v)}`,
    p25Key: "floor_p25", p75Key: "floor_p75",
  },
  {
    labelKey: "year", label: "Rok budowy",
    minKey: "year_min", maxKey: "year_max",
    absMin: 1960, absMax: 2024, step: 1,
    format: v => `${Math.round(v)}`,
    p25Key: "year_p25", p75Key: "year_p75",
  },
];

interface Props {
  params: HeatmapParams;
  onChange: (params: HeatmapParams) => void;
  heatmapLoading: boolean;
  isTypical: boolean;
  onTypicalChange: (v: boolean) => void;
  heatmap: HeatmapResponse | null;
}

export function ParameterPanel({ params, onChange, heatmapLoading, isTypical, onTypicalChange, heatmap }: Props) {
  const handleRange = (minKey: keyof HeatmapParams, maxKey: keyof HeatmapParams, lo: number, hi: number) => {
    onChange({ ...params, [minKey]: lo, [maxKey]: hi });
  };

  const handleTypicalToggle = (checked: boolean) => {
    onTypicalChange(checked);
    if (checked) {
      onChange({ ...params, area_min: null, area_max: null, floor_min: null, floor_max: null, year_min: null, year_max: null });
    } else {
      onChange({
        ...params,
        area_min: heatmap?.area_p25 ?? 40,
        area_max: heatmap?.area_p75 ?? 80,
        floor_min: heatmap?.floor_p25 ?? 1,
        floor_max: heatmap?.floor_p75 ?? 5,
        year_min: heatmap?.year_p25 ?? 1995,
        year_max: heatmap?.year_p75 ?? 2015,
      });
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-sm uppercase tracking-wider">Parametry mapy</h2>
        {heatmapLoading && <span className="text-xs text-blue-400 animate-pulse">Generowanie...</span>}
      </div>

      <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
        <input
          type="checkbox"
          checked={isTypical}
          onChange={e => handleTypicalToggle(e.target.checked)}
          className="accent-blue-500"
        />
        Typowy przedział dla miasta
      </label>

      {SLIDERS.map(({ label, minKey, maxKey, absMin, absMax, step, format, p25Key, p75Key }) => {
        const lo = isTypical
          ? (heatmap ? (heatmap[p25Key] as number) : absMin)
          : (params[minKey] as number | null) ?? absMin;
        const hi = isTypical
          ? (heatmap ? (heatmap[p75Key] as number) : absMax)
          : (params[maxKey] as number | null) ?? absMax;

        return (
          <DualSlider
            key={minKey}
            label={label}
            lo={lo}
            hi={hi}
            min={absMin}
            max={absMax}
            step={step}
            format={format}
            disabled={isTypical}
            onChange={(newLo, newHi) => handleRange(minKey, maxKey, newLo, newHi)}
          />
        );
      })}

      <div className="space-y-1">
        <div className="flex justify-between text-xs text-gray-400">
          <span>Rozdzielczość siatki</span>
          <span className="text-white font-medium">{params.resolution}×{params.resolution}</span>
        </div>
        <input
          type="range" min={40} max={200} step={10}
          value={params.resolution}
          onChange={e => onChange({ ...params, resolution: Number(e.target.value) })}
          className="w-full accent-blue-500 cursor-pointer"
        />
      </div>
    </div>
  );
}

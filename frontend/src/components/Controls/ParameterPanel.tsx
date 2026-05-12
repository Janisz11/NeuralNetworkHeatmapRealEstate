import type { HeatmapParams } from "../../types";

interface Props {
  params: HeatmapParams;
  onChange: (params: HeatmapParams) => void;
  heatmapLoading: boolean;
}

interface SliderConfig {
  key: keyof HeatmapParams;
  label: string;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
}

const SLIDERS: SliderConfig[] = [
  { key: "area_m2", label: "Powierzchnia", min: 20, max: 200, step: 5, format: (v) => `${v} m²` },
  { key: "floor", label: "Piętro", min: 0, max: 15, step: 1, format: (v) => `${v}` },
  { key: "build_year", label: "Rok budowy", min: 1960, max: 2024, step: 1, format: (v) => `${v}` },
  { key: "resolution", label: "Rozdzielczość siatki", min: 40, max: 200, step: 10, format: (v) => `${v}×${v}` },
];

export function ParameterPanel({ params, onChange, heatmapLoading }: Props) {
  const handleChange = (key: keyof HeatmapParams, value: number) => {
    onChange({ ...params, [key]: value });
  };

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-sm uppercase tracking-wider">Parametry mapy</h2>
        {heatmapLoading && (
          <span className="text-xs text-blue-400 animate-pulse">Generowanie...</span>
        )}
      </div>

      {SLIDERS.map(({ key, label, min, max, step, format }) => (
        <div key={key} className="space-y-1">
          <div className="flex justify-between text-xs text-gray-400">
            <span>{label}</span>
            <span className="text-white font-medium">{format(params[key])}</span>
          </div>
          <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={params[key]}
            onChange={(e) => handleChange(key, Number(e.target.value))}
            className="w-full accent-blue-500 cursor-pointer"
          />
        </div>
      ))}
    </div>
  );
}

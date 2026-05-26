import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router";
import { getApartments } from "./api/client";
import { useHeatmap } from "./hooks/useHeatmap";
import { useTraining } from "./hooks/useTraining";
import { MapView } from "./components/Map/MapView";
import { ParameterPanel } from "./components/Controls/ParameterPanel";
import { TrainingPanel } from "./components/Controls/TrainingPanel";
import { ModelSelector } from "./components/Controls/ModelSelector";
import { CitySelector } from "./components/Controls/CitySelector";
import { LossChart } from "./components/Charts/LossChart";
import { AdminPanel } from "./components/Admin/AdminPanel";
import type { Apartment, HeatmapParams } from "./types";

const DEFAULT_PARAMS: HeatmapParams = {
  area_min: null,
  area_max: null,
  floor_min: null,
  floor_max: null,
  year_min: null,
  year_max: null,
  resolution: 100,
};

function MainView() {
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [selectedCity, setSelectedCity] = useState<string>("warszawa");
  const [params, setParams] = useState<HeatmapParams>(DEFAULT_PARAMS);
  const [apartments, setApartments] = useState<Apartment[]>([]);
  const [showDataPoints, setShowDataPoints] = useState(true);
  const [isTypical, setIsTypical] = useState(true);
  const [fitTrigger, setFitTrigger] = useState(0);

  const { data: heatmap, loading: heatmapLoading } = useHeatmap(selectedRunId, selectedCity, params);
  const { train, runId: trainingRunId, isTraining, status, lossHistory } = useTraining();

  useEffect(() => {
    getApartments().then((r) => setApartments(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (status?.status === "done" && trainingRunId) {
      setSelectedRunId(trainingRunId);
      setFitTrigger(t => t + 1);
    }
  }, [status?.status, trainingRunId]);

  const handleCitySelectorChange = (city: string) => {
    setSelectedCity(city);
    setFitTrigger(t => t + 1);
  };

  const handleModelSelect = (runId: number) => {
    setSelectedRunId(runId);
    setFitTrigger(t => t + 1);
  };

  const handleMapCityChange = (city: string) => {
    setSelectedCity(city);
    setIsTypical(true);
  };

  return (
    <div className="h-screen bg-gray-950 flex flex-col">
      <header className="bg-gray-900 border-b border-gray-700 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">N</div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">NeuralMap Poland</h1>
            <p className="text-gray-500 text-xs">Neural network real estate heatmap</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showDataPoints}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setShowDataPoints(e.target.checked)}
              className="accent-blue-500"
            />
            Dane treningowe
          </label>
          <Link
            to="/admin"
            className="text-xs text-gray-400 hover:text-white transition-colors border border-gray-700 rounded px-3 py-1"
          >
            Admin
          </Link>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-72 shrink-0 bg-gray-950 border-r border-gray-800 p-3 overflow-y-auto space-y-3">
          <CitySelector selectedCity={selectedCity} onChange={handleCitySelectorChange} />
          <ModelSelector selectedRunId={selectedRunId} onSelect={handleModelSelect} />
          <ParameterPanel
            params={params}
            onChange={setParams}
            heatmapLoading={heatmapLoading}
            isTypical={isTypical}
            onTypicalChange={setIsTypical}
            heatmap={heatmap ?? null}
          />
          <TrainingPanel onTrain={train} isTraining={isTraining} status={status} />
          <LossChart lossHistory={lossHistory} />

        </aside>

        <main className="flex-1 relative">
          <MapView
            heatmap={heatmap}
            apartments={apartments}
            showDataPoints={showDataPoints}
            fitTrigger={fitTrigger}
            currentCity={selectedCity}
            onMapCityChange={handleMapCityChange}
          />

          {/* Floating price range widget */}
          {heatmap && (
            <div className="absolute top-3 right-3 z-[1000] pointer-events-none">
              <div className="bg-slate-950/85 backdrop-blur-md border border-slate-800 rounded-2xl p-4 shadow-2xl min-w-[240px] space-y-3">
                <p className="text-slate-400 text-xs uppercase tracking-wider text-center">
                  Zakres cen w tym widoku
                </p>
                <div className="flex items-end justify-between gap-3">
                  <div>
                    <span className="text-xs text-blue-400 block mb-0.5">Minimum</span>
                    <span className="text-xl font-black text-white tabular-nums">
                      {Math.round(heatmap.min_val).toLocaleString("pl-PL")} zł
                    </span>
                    <span className="text-xs text-slate-500 block">/ m²</span>
                  </div>
                  <div className="text-slate-600 text-lg pb-4">→</div>
                  <div className="text-right">
                    <span className="text-xs text-emerald-400 block mb-0.5">Maksimum</span>
                    <span className="text-xl font-black text-white tabular-nums">
                      {Math.round(heatmap.max_val).toLocaleString("pl-PL")} zł
                    </span>
                    <span className="text-xs text-slate-500 block">/ m²</span>
                  </div>
                </div>
                <div className="h-1.5 rounded-full" style={{
                  background: "linear-gradient(to right, #3b82f6, #06b6d4, #22c55e, #eab308, #ef4444)"
                }} />
              </div>
            </div>
          )}

          {!selectedRunId && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="bg-gray-900/80 backdrop-blur rounded-xl p-6 text-center max-w-xs">
                <p className="text-white font-semibold">Wybierz model</p>
                <p className="text-gray-400 text-sm mt-1">
                  Wytrenuj sieć neuronową lub wybierz zapisany model, aby zobaczyć heatmapę.
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainView />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </BrowserRouter>
  );
}

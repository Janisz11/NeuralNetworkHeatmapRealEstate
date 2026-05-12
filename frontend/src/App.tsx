import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router";
import { getApartments } from "./api/client";
import { useHeatmap } from "./hooks/useHeatmap";
import { useTraining } from "./hooks/useTraining";
import { MapView } from "./components/Map/MapView";
import { ParameterPanel } from "./components/Controls/ParameterPanel";
import { TrainingPanel } from "./components/Controls/TrainingPanel";
import { ModelSelector } from "./components/Controls/ModelSelector";
import { LossChart } from "./components/Charts/LossChart";
import { AdminPanel } from "./components/Admin/AdminPanel";
import type { Apartment, HeatmapParams } from "./types";

const DEFAULT_PARAMS: HeatmapParams = {
  area_m2: 55,
  floor: 3,
  build_year: 2010,
  resolution: 100,
};

function MainView() {
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [params, setParams] = useState<HeatmapParams>(DEFAULT_PARAMS);
  const [apartments, setApartments] = useState<Apartment[]>([]);
  const [showDataPoints, setShowDataPoints] = useState(true);

  const { data: heatmap, loading: heatmapLoading } = useHeatmap(selectedRunId, params);
  const { train, runId: trainingRunId, isTraining, status, lossHistory } = useTraining();

  useEffect(() => {
    getApartments().then((r) => setApartments(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (status?.status === "done" && trainingRunId) {
      setSelectedRunId(trainingRunId);
    }
  }, [status?.status, trainingRunId]);

  return (
    <div className="h-screen bg-gray-950 flex flex-col">
      <header className="bg-gray-900 border-b border-gray-700 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">N</div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">NeuralMap Wrocław</h1>
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
          <ModelSelector selectedRunId={selectedRunId} onSelect={setSelectedRunId} />
          <ParameterPanel params={params} onChange={setParams} heatmapLoading={heatmapLoading} />
          <TrainingPanel onTrain={train} isTraining={isTraining} status={status} />
          <LossChart lossHistory={lossHistory} />

          {heatmap && (
            <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
              <h2 className="text-white font-semibold text-sm uppercase tracking-wider mb-2">Legenda</h2>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-4 rounded" style={{
                  background: "linear-gradient(to right, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000)"
                }} />
              </div>
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>{heatmap.min_val.toLocaleString("pl-PL")} zł</span>
                <span>{heatmap.max_val.toLocaleString("pl-PL")} zł</span>
              </div>
            </div>
          )}
        </aside>

        <main className="flex-1 relative">
          <MapView
            heatmap={heatmap}
            apartments={apartments}
            showDataPoints={showDataPoints}
          />
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

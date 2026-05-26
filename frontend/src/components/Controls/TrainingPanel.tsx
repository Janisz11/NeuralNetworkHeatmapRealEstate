import { useState } from "react";
import type { TrainRequest, TrainStatus } from "../../types";

interface Props {
  onTrain: (req: TrainRequest) => void;
  isTraining: boolean;
  status: TrainStatus | null;
}

export function TrainingPanel({ onTrain, isTraining, status }: Props) {
  const [modelName, setModelName] = useState("model-v1");
  const [epochs, setEpochs] = useState(200);
  const [lr, setLr] = useState(0.001);
  const [hiddenLayers, setHiddenLayers] = useState("128,64,32");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const layers = hiddenLayers
      .split(",")
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n) && n > 0);
    onTrain({ model_name: modelName, epochs, learning_rate: lr, hidden_layers: layers });
  };

  const progress = status
    ? Math.round((status.current_epoch / status.total_epochs) * 100)
    : 0;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-4">
      <h2 className="text-white font-semibold text-sm uppercase tracking-wider">Trenowanie sieci</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Nazwa modelu</label>
          <input
            className="w-full bg-gray-800 text-white text-sm rounded px-3 py-2 border border-gray-600 focus:outline-none focus:border-blue-500"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-400 block mb-1">Epoki: {epochs}</label>
            <input type="range" min={50} max={1000} step={50} value={epochs}
              onChange={(e) => setEpochs(Number(e.target.value))}
              className="w-full accent-blue-500" />
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">LR: {lr}</label>
            <input type="range" min={0.0001} max={0.01} step={0.0001} value={lr}
              onChange={(e) => setLr(Number(e.target.value))}
              className="w-full accent-blue-500" />
          </div>
        </div>

        <div>
          <label className="text-xs text-gray-400 block mb-1">Warstwy ukryte (przecinek)</label>
          <input
            className="w-full bg-gray-800 text-white text-sm rounded px-3 py-2 border border-gray-600 focus:outline-none focus:border-blue-500"
            value={hiddenLayers}
            onChange={(e) => setHiddenLayers(e.target.value)}
            placeholder="128,64,32"
          />
        </div>

        <button
          type="submit"
          disabled={isTraining}
          className="w-full py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white text-sm font-medium transition-colors"
        >
          {isTraining ? "Trenowanie..." : "Uruchom trening"}
        </button>
      </form>

      {isTraining && status && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Epoka {status.current_epoch} / {status.total_epochs}</span>
            <span>MSE: {status.loss?.toFixed(5) ?? "—"}</span>
            <span>R²: {status.r2_score?.toFixed(3) ?? "—"}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {status?.status === "done" && (
        <div className="text-green-400 text-xs text-center">
          Trening zakończony · R² = {status.r2_score?.toFixed(3)}
        </div>
      )}
    </div>
  );
}

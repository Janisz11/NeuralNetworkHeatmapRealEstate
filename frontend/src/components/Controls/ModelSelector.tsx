import { useEffect, useState } from "react";
import { getModels } from "../../api/client";
import type { ModelRun } from "../../types";

interface Props {
  selectedRunId: number | null;
  onSelect: (runId: number) => void;
}

export function ModelSelector({ selectedRunId, onSelect }: Props) {
  const [models, setModels] = useState<ModelRun[]>([]);

  const reload = () => {
    getModels().then(setModels).catch(() => {});
  };

  useEffect(() => {
    reload();
    const id = setInterval(reload, 5000);
    return () => clearInterval(id);
  }, []);

  const doneModels = models.filter((m) => m.status === "done");

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-2">
      <h2 className="text-white font-semibold text-sm uppercase tracking-wider">Wybierz model</h2>

      {doneModels.length === 0 ? (
        <p className="text-gray-500 text-xs">Brak wytrenowanych modeli. Uruchom trening.</p>
      ) : (
        <select
          className="w-full bg-gray-800 text-white text-sm rounded px-3 py-2 border border-gray-600 focus:outline-none focus:border-blue-500"
          value={selectedRunId ?? ""}
          onChange={(e) => onSelect(Number(e.target.value))}
        >
          <option value="">— wybierz model —</option>
          {doneModels.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name} · R²={m.r2_score?.toFixed(3) ?? "?"} · {new Date(m.created_at).toLocaleDateString("pl-PL")}
            </option>
          ))}
        </select>
      )}

      {selectedRunId && (
        <div className="text-xs text-gray-500">
          {doneModels.find((m) => m.id === selectedRunId)?.name} aktywny
        </div>
      )}
    </div>
  );
}

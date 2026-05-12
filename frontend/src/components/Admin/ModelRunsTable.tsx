import type { ModelRun } from "../../types";

interface Props {
  models: ModelRun[];
}

const STATUS_COLOR: Record<string, string> = {
  done: "text-green-400",
  training: "text-yellow-400",
  error: "text-red-400",
  pending: "text-gray-400",
};

export function ModelRunsTable({ models }: Props) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-700">
      <table className="w-full text-sm text-left">
        <thead className="bg-gray-800 text-gray-400 text-xs uppercase">
          <tr>
            {["ID", "Nazwa", "Epoki", "LR", "Warstwy", "MSE", "R²", "Status", "Data"].map((h) => (
              <th key={h} className="px-4 py-3">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {models.map((m) => (
            <tr key={m.id} className="border-t border-gray-700 hover:bg-gray-800 text-gray-300">
              <td className="px-4 py-2">{m.id}</td>
              <td className="px-4 py-2 font-medium text-white">{m.name}</td>
              <td className="px-4 py-2">{m.epochs}</td>
              <td className="px-4 py-2">{m.learning_rate}</td>
              <td className="px-4 py-2">[{m.hidden_layers.join(", ")}]</td>
              <td className="px-4 py-2">{m.mse_loss?.toFixed(5) ?? "—"}</td>
              <td className="px-4 py-2">{m.r2_score?.toFixed(3) ?? "—"}</td>
              <td className={`px-4 py-2 font-medium ${STATUS_COLOR[m.status] ?? ""}`}>{m.status}</td>
              <td className="px-4 py-2 text-gray-500">
                {new Date(m.created_at).toLocaleDateString("pl-PL")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {models.length === 0 && (
        <p className="text-center text-gray-500 py-8">Brak modeli.</p>
      )}
    </div>
  );
}

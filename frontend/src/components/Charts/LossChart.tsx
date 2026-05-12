import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

interface Props {
  lossHistory: number[];
}

export function LossChart({ lossHistory }: Props) {
  if (lossHistory.length === 0) return null;

  const data = lossHistory.map((loss, epoch) => ({ epoch: epoch + 1, loss }));

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
      <h2 className="text-white font-semibold text-sm uppercase tracking-wider mb-3">
        Krzywa uczenia (MSE)
      </h2>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="epoch" tick={{ fill: "#9ca3af", fontSize: 11 }} />
          <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "#1f2937", border: "1px solid #374151", color: "#fff" }}
            formatter={(v: number) => [v.toFixed(5), "MSE"]}
          />
          <Line
            type="monotone"
            dataKey="loss"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

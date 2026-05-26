import { useEffect, useState } from "react";
import { getCities } from "../../api/client";
import type { CityInfo } from "../../types";

interface Props {
  selectedCity: string;
  onChange: (city: string) => void;
}

export function CitySelector({ selectedCity, onChange }: Props) {
  const [cities, setCities] = useState<CityInfo[]>([]);

  useEffect(() => {
    getCities().then(setCities).catch(() => {});
  }, []);

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
      <h2 className="text-white font-semibold text-sm uppercase tracking-wider mb-3">Miasto</h2>
      <select
        value={selectedCity}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-gray-800 border border-gray-600 text-white text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {cities.map((c) => (
          <option key={c.slug} value={c.slug}>
            {c.display_name}
          </option>
        ))}
      </select>
    </div>
  );
}

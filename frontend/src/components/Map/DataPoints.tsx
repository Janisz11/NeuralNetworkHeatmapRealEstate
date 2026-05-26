import { CircleMarker, Tooltip } from "react-leaflet";
import type { Apartment } from "../../types";

interface Props {
  apartments: Apartment[];
}

function priceColor(price: number): string {
  if (price >= 14000) return "#ef4444";
  if (price >= 12000) return "#f97316";
  if (price >= 10000) return "#eab308";
  return "#22c55e";
}

export function DataPoints({ apartments }: Props) {
  return (
    <>
      {apartments.map((apt) => (
        <CircleMarker
          key={apt.id}
          center={[apt.lat, apt.lon]}
          radius={4}
          pathOptions={{
            color: priceColor(apt.price_per_m2),
            fillColor: priceColor(apt.price_per_m2),
            fillOpacity: 0.8,
            weight: 1,
          }}
        >
          <Tooltip>
            <div className="text-sm">
              <p className="font-semibold">{apt.city}</p>
              <p>{apt.price_per_m2.toLocaleString("pl-PL")} zł/m²</p>
              <p>{apt.area_m2} m² · piętro {apt.floor} · {apt.build_year}</p>
            </div>
          </Tooltip>
        </CircleMarker>
      ))}
    </>
  );
}

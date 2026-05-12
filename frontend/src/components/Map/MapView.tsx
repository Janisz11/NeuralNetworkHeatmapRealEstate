import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { HeatmapResponse, Apartment } from "../../types";
import { HeatmapOverlay } from "./HeatmapOverlay";
import { DataPoints } from "./DataPoints";

interface Props {
  heatmap: HeatmapResponse | null;
  apartments: Apartment[];
  showDataPoints: boolean;
}

const WROCLAW_CENTER: [number, number] = [51.107, 17.038];

export function MapView({ heatmap, apartments, showDataPoints }: Props) {
  return (
    <MapContainer
      center={WROCLAW_CENTER}
      zoom={12}
      className="w-full h-full rounded-xl"
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {heatmap && <HeatmapOverlay heatmap={heatmap} />}
      {showDataPoints && <DataPoints apartments={apartments} />}
    </MapContainer>
  );
}

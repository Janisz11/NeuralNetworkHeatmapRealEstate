import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, useMap, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { HeatmapResponse, Apartment } from "../../types";
import { HeatmapOverlay } from "./HeatmapOverlay";
import { DataPoints } from "./DataPoints";

const CITIES: Record<string, { centre_lat: number; centre_lon: number }> = {
  warszawa: { centre_lat: 52.2297, centre_lon: 21.0122 },
  krakow:   { centre_lat: 50.0647, centre_lon: 19.9450 },
  wroclaw:  { centre_lat: 51.1079, centre_lon: 17.0385 },
  gdansk:   { centre_lat: 54.3520, centre_lon: 18.6466 },
  poznan:   { centre_lat: 52.4064, centre_lon: 16.9252 },
  lodz:     { centre_lat: 51.7592, centre_lon: 19.4560 },
};

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

function closestCity(lat: number, lon: number): string {
  let bestSlug = "warszawa";
  let bestDist = Infinity;
  for (const [slug, info] of Object.entries(CITIES)) {
    const d = haversineKm(lat, lon, info.centre_lat, info.centre_lon);
    if (d < bestDist) { bestDist = d; bestSlug = slug; }
  }
  return bestSlug;
}

function MapController({ bounds, fitTrigger, currentCity, onCityChange }: {
  bounds: [[number, number], [number, number]] | null;
  fitTrigger: number;
  currentCity: string;
  onCityChange: (city: string) => void;
}) {
  const map = useMap();
  const isProgrammaticMove = useRef(false);
  // Tracks which city was active the last time fitTrigger fired.
  // If it differs from currentCity the user picked a new city from the dropdown,
  // and the stored bounds belong to the old city — use setView instead of fitBounds.
  const prevFitCity = useRef(currentCity);

  useEffect(() => {
    if (fitTrigger <= 0) return;

    const cityChanged = currentCity !== prevFitCity.current;
    prevFitCity.current = currentCity;

    isProgrammaticMove.current = true;

    if (!cityChanged && bounds) {
      // Same city, different model — zoom to heatmap bounds.
      map.fitBounds(bounds, { animate: true, padding: [10, 10] });
    } else {
      // City changed — bounds are stale (old city); navigate to new city centre.
      const info = CITIES[currentCity];
      if (info) {
        map.setView([info.centre_lat, info.centre_lon], 12, { animate: true });
      }
    }
  }, [fitTrigger, map]); // eslint-disable-line react-hooks/exhaustive-deps

  useMapEvents({
    moveend(e) {
      if (isProgrammaticMove.current) {
        isProgrammaticMove.current = false;
        return;
      }
      const { lat, lng } = e.target.getCenter();
      const nearest = closestCity(lat, lng);
      if (nearest !== currentCity) {
        onCityChange(nearest);
      }
    },
  });

  return null;
}

interface Props {
  heatmap: HeatmapResponse | null;
  apartments: Apartment[];
  showDataPoints: boolean;
  fitTrigger: number;
  currentCity: string;
  onMapCityChange: (city: string) => void;
}

const POLAND_CENTER: [number, number] = [52.07, 19.48];

export function MapView({ heatmap, apartments, showDataPoints, fitTrigger, currentCity, onMapCityChange }: Props) {
  return (
    <MapContainer
      center={POLAND_CENTER}
      zoom={6}
      className="w-full h-full rounded-xl"
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapController
        bounds={heatmap ? heatmap.bounds : null}
        fitTrigger={fitTrigger}
        currentCity={currentCity}
        onCityChange={onMapCityChange}
      />
      {heatmap && <HeatmapOverlay heatmap={heatmap} />}
      {showDataPoints && <DataPoints apartments={apartments} />}
    </MapContainer>
  );
}

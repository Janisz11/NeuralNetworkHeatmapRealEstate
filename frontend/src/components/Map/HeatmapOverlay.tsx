import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import type { HeatmapResponse } from "../../types";

interface Props {
  heatmap: HeatmapResponse;
}

export function HeatmapOverlay({ heatmap }: Props) {
  const map = useMap();
  const overlayRef = useRef<L.ImageOverlay | null>(null);

  useEffect(() => {
    if (!heatmap) return;

    const bounds = L.latLngBounds(
      [heatmap.bounds[0][0], heatmap.bounds[0][1]],
      [heatmap.bounds[1][0], heatmap.bounds[1][1]]
    );

    const imageUrl = `data:image/png;base64,${heatmap.image_base64}`;

    if (overlayRef.current) {
      overlayRef.current.setUrl(imageUrl);
      overlayRef.current.setBounds(bounds);
    } else {
      overlayRef.current = L.imageOverlay(imageUrl, bounds, { opacity: 0.65 });
      overlayRef.current.addTo(map);
    }

    return () => {
      overlayRef.current?.remove();
      overlayRef.current = null;
    };
  }, [heatmap, map]);

  return null;
}

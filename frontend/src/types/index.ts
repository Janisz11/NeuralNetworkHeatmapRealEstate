export interface Apartment {
  id: number;
  lat: number;
  lon: number;
  price_per_m2: number;
  area_m2: number;
  floor: number;
  build_year: number;
  centre_distance: number;
  city: string;
  created_at: string;
}

export interface ApartmentListResponse {
  data: Apartment[];
  total: number;
}

export interface ModelRun {
  id: number;
  name: string;
  epochs: number;
  learning_rate: number;
  hidden_layers: number[];
  mse_loss: number | null;
  r2_score: number | null;
  status: "pending" | "training" | "done" | "error";
  created_at: string;
}

export interface TrainRequest {
  model_name: string;
  epochs: number;
  learning_rate: number;
  hidden_layers: number[];
}

export interface TrainResponse {
  run_id: number;
  status: string;
}

export interface TrainStatus {
  run_id: number;
  status: string;
  current_epoch: number;
  total_epochs: number;
  loss: number | null;
  r2_score: number | null;
}

export interface HeatmapRequest {
  run_id: number;
  city: string;
  resolution: number;
  // null = "use typical (p25–p75 mean)" — backend resolves automatically
  area_min: number | null;
  area_max: number | null;
  floor_min: number | null;
  floor_max: number | null;
  year_min: number | null;
  year_max: number | null;
}

export interface HeatmapResponse {
  image_base64: string;
  min_val: number;
  max_val: number;
  bounds: [[number, number], [number, number]];
  // Typical market ranges from training stats
  area_p25: number;
  area_p75: number;
  floor_p25: number;
  floor_p75: number;
  year_p25: number;
  year_p75: number;
}

// null values mean "typical" mode (backend uses p25–p75 midpoint)
export interface HeatmapParams {
  area_min: number | null;
  area_max: number | null;
  floor_min: number | null;
  floor_max: number | null;
  year_min: number | null;
  year_max: number | null;
  resolution: number;
}

export interface CityInfo {
  slug: string;
  display_name: string;
  centre_lat: number;
  centre_lon: number;
}

export interface User {
  id: number;
  email: string;
  name: string | null;
  picture: string | null;
  role: string;
}

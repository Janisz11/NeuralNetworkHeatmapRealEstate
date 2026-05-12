export interface Apartment {
  id: number;
  lat: number;
  lon: number;
  price_per_m2: number;
  area_m2: number;
  floor: number;
  build_year: number;
  district: string | null;
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
  resolution: number;
  area_m2: number;
  floor: number;
  build_year: number;
}

export interface HeatmapResponse {
  image_base64: string;
  min_val: number;
  max_val: number;
  bounds: [[number, number], [number, number]];
}

export interface HeatmapParams {
  area_m2: number;
  floor: number;
  build_year: number;
  resolution: number;
}

export interface User {
  id: number;
  email: string;
  name: string | null;
  picture: string | null;
  role: string;
}

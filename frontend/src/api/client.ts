
import axios from "axios";
import type {
  ApartmentListResponse,
  HeatmapRequest,
  HeatmapResponse,
  ModelRun,
  TrainRequest,
  TrainResponse,
  TrainStatus,
  User,
} from "../types";

const api = axios.create({ baseURL: "/" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getApartments = (limit = 5000): Promise<ApartmentListResponse> =>
  api.get<ApartmentListResponse>(`/api/apartments?limit=${limit}`).then((r) => r.data);

export const getModels = (): Promise<ModelRun[]> =>
  api.get<ModelRun[]>("/api/models").then((r) => r.data);

export const startTraining = (req: TrainRequest): Promise<TrainResponse> =>
  api.post<TrainResponse>("/api/train", req).then((r) => r.data);

export const getTrainingStatus = (runId: number): Promise<TrainStatus> =>
  api.get<TrainStatus>(`/api/train/${runId}/status`).then((r) => r.data);

export const getHeatmap = (req: HeatmapRequest): Promise<HeatmapResponse> =>
  api.post<HeatmapResponse>("/api/heatmap", req).then((r) => r.data);

export const getMe = (): Promise<User> =>
  api.get<User>("/auth/me").then((r) => r.data);

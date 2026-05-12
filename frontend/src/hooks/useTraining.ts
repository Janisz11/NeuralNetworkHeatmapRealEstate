import { useState, useEffect, useRef, useCallback } from "react";
import { startTraining, getTrainingStatus } from "../api/client";
import type { TrainRequest, TrainStatus } from "../types";

interface TrainingState {
  runId: number | null;
  status: TrainStatus | null;
  lossHistory: number[];
  isTraining: boolean;
  error: string | null;
}

export function useTraining() {
  const [state, setState] = useState<TrainingState>({
    runId: null,
    status: null,
    lossHistory: [],
    isTraining: false,
    error: null,
  });
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const train = useCallback(async (req: TrainRequest) => {
    stopPolling();
    setState({ runId: null, status: null, lossHistory: [], isTraining: true, error: null });

    try {
      const { run_id } = await startTraining(req);
      setState((s) => ({ ...s, runId: run_id }));

      pollRef.current = setInterval(async () => {
        try {
          const statusData = await getTrainingStatus(run_id);
          setState((s) => ({
            ...s,
            status: statusData,
            lossHistory: statusData.loss !== null
              ? [...s.lossHistory, statusData.loss]
              : s.lossHistory,
          }));

          if (statusData.status === "done" || statusData.status === "error") {
            stopPolling();
            setState((s) => ({ ...s, isTraining: false }));
          }
        } catch {
        }
      }, 2000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Training failed";
      setState((s) => ({ ...s, isTraining: false, error: msg }));
    }
  }, []);

  useEffect(() => () => stopPolling(), []);

  return { ...state, train };
}

import { create } from "zustand";

export interface EnvironmentAnalysis {
  temperature: number;
  relative_humidity: number;
  air_speed: number;
  mean_radiant_temperature: number;
  met: number;
  clo: number;
  pet: number;
  comfort: string;
}

export interface EnvironmentValues {
  met: number;
  clo: number;

  ach: number;

  outdoorTemperature: number;
  outdoorHumidity: number;
  outdoorWindSpeed: number;

  solarLatitude: number;
  solarLongitude: number;
  solarDateTime: string;
}

interface EnvironmentStore
  extends EnvironmentValues {
  analysis: EnvironmentAnalysis | null;
  analysisLoading: boolean;
  analysisError: string | null;

  setValues: (
    patch: Partial<EnvironmentValues>,
  ) => void;

  setAnalysis: (
    analysis: EnvironmentAnalysis | null,
  ) => void;

  setAnalysisLoading: (
    loading: boolean,
  ) => void;

  setAnalysisError: (
    error: string | null,
  ) => void;
}

function localDateTimeValue() {
  const now = new Date();

  const local = new Date(
    now.getTime() -
      now.getTimezoneOffset() * 60000,
  );

  return local
    .toISOString()
    .slice(0, 16);
}

export const useEnvironmentStore =
  create<EnvironmentStore>((set) => ({
    met: 1.2,
    clo: 0.5,

    ach: 1.5,

    outdoorTemperature: 29,
    outdoorHumidity: 65,
    outdoorWindSpeed: 2.0,

    solarLatitude: 25.0,
    solarLongitude: 102.0,
    solarDateTime: localDateTimeValue(),

    analysis: null,
    analysisLoading: false,
    analysisError: null,

    setValues: (patch) =>
      set(patch),

    setAnalysis: (analysis) =>
      set({ analysis }),

    setAnalysisLoading: (
      analysisLoading,
    ) =>
      set({ analysisLoading }),

    setAnalysisError: (
      analysisError,
    ) =>
      set({ analysisError }),
  }));
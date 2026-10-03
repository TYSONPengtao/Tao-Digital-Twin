import type {
  EnvironmentAnalysis,
} from "../stores/environmentStore";

export interface EnvironmentRequest {
  temperature: number;
  relative_humidity: number;
  air_speed: number;
  mean_radiant_temperature: number;
  met: number;
  clo: number;
}

export async function analyzeEnvironment(
  payload: EnvironmentRequest,
  signal?: AbortSignal,
): Promise<EnvironmentAnalysis> {
  const response = await fetch(
    "http://127.0.0.1:8000/api/environment/pet",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(payload),

      signal,
    },
  );

  if (!response.ok) {
    throw new Error(
      `Environment API HTTP ${response.status}`,
    );
  }

  return response.json();
}
import { create } from "zustand";

export type RoomName =
  | "Living Room"
  | "Bedroom"
  | "Kitchen"
  | "Balcony";

export interface RoomEnvironmentState {
  temperature: number;
  relativeHumidity: number;
  airSpeed: number;
  meanRadiantTemperature: number;
}

interface RoomEnvironmentStore {
  rooms: Record<RoomName, RoomEnvironmentState>;

  setRoom: (
    room: RoomName,
    patch: Partial<RoomEnvironmentState>,
  ) => void;

  updateRoom: (
    room: RoomName,
    updater: (
      current: RoomEnvironmentState,
    ) => RoomEnvironmentState,
  ) => void;
}

export const useRoomEnvironmentStore =
  create<RoomEnvironmentStore>((set) => ({
    rooms: {
      "Living Room": {
        temperature: 25.0,
        relativeHumidity: 50,
        airSpeed: 0.12,
        meanRadiantTemperature: 25.2,
      },

      Bedroom: {
        temperature: 24.5,
        relativeHumidity: 52,
        airSpeed: 0.08,
        meanRadiantTemperature: 24.7,
      },

      Kitchen: {
        temperature: 26.0,
        relativeHumidity: 55,
        airSpeed: 0.15,
        meanRadiantTemperature: 26.2,
      },

      Balcony: {
        temperature: 27.0,
        relativeHumidity: 60,
        airSpeed: 0.4,
        meanRadiantTemperature: 28.0,
      },
    },

    setRoom: (room, patch) =>
      set((state) => ({
        rooms: {
          ...state.rooms,

          [room]: {
            ...state.rooms[room],
            ...patch,
          },
        },
      })),

    updateRoom: (room, updater) =>
      set((state) => ({
        rooms: {
          ...state.rooms,

          [room]: updater(
            state.rooms[room],
          ),
        },
      })),
  }));
import {
  useEffect,
  useMemo,
} from "react";

import * as SunCalc from "suncalc";

import {
  analyzeEnvironment,
} from "../../services/environmentApi";

import {
  useEnvironmentStore,
} from "../../stores/environmentStore";

import {
  type RoomName,
  useRoomEnvironmentStore,
} from "../../stores/roomEnvironmentStore";

import type {
  DeviceStateMap,
} from "../../types/device";


interface Props {
  selectedRoom: string;
  deviceStates: DeviceStateMap;
}


const ROOM_NAMES: RoomName[] = [
  "Living Room",
  "Bedroom",
  "Kitchen",
  "Balcony",
];


function clamp(
  value: number,
  min: number,
  max: number,
) {
  return Math.min(
    max,
    Math.max(min, value),
  );
}


export function EnvironmentPanel({
  selectedRoom,
  deviceStates,
}: Props) {
  const global =
    useEnvironmentStore();

  const rooms =
    useRoomEnvironmentStore(
      (state) =>
        state.rooms,
    );

  const setRoom =
    useRoomEnvironmentStore(
      (state) =>
        state.setRoom,
    );

  const updateRoom =
    useRoomEnvironmentStore(
      (state) =>
        state.updateRoom,
    );

  const room: RoomName =
    ROOM_NAMES.includes(
      selectedRoom as RoomName,
    )
      ? selectedRoom as RoomName
      : "Living Room";

  const values =
    rooms[room];

  // ==========================================================
  // Reduced-order room simulation
  // ==========================================================

  useEffect(() => {
    const timer =
      window.setInterval(() => {
        const sun =
          SunCalc.getPosition(
            new Date(
              global.solarDateTime,
            ),
            global.solarLatitude,
            global.solarLongitude,
          );

        const solarFactor =
          Math.max(
            0,
            Math.sin(
              sun.altitude *
              Math.PI /
              180,
            ),
          );

        ROOM_NAMES.forEach(
          (roomName) => {
            updateRoom(
              roomName,
              (current) => {
                let temperature =
                  current.temperature;

                let humidity =
                  current.relativeHumidity;

                let mrt =
                  current.meanRadiantTemperature;

                let airSpeed =
                  current.airSpeed;

                // --------------------------------------------
                // Ventilation / envelope exchange
                // --------------------------------------------

                const exchange =
                  clamp(
                    global.ach / 6,
                    0,
                    1,
                  );

                temperature +=
                  (
                    global.outdoorTemperature -
                    temperature
                  ) *
                  0.0025 *
                  exchange;

                humidity +=
                  (
                    global.outdoorHumidity -
                    humidity
                  ) *
                  0.003 *
                  exchange;

                const targetAirSpeed =
                  0.04 +
                  global.outdoorWindSpeed *
                  0.12 *
                  exchange;

                airSpeed +=
                  (
                    targetAirSpeed -
                    airSpeed
                  ) * 0.08;

                // --------------------------------------------
                // Solar / MRT
                // --------------------------------------------

                let roomSolarGain =
                  roomName === "Balcony"
                    ? 1.0
                    : roomName === "Living Room"
                      ? 0.75
                      : roomName === "Bedroom"
                        ? 0.45
                        : 0.35;

                // Living room curtain attenuates solar gain.
                if (
                  roomName ===
                    "Living Room" &&
                  deviceStates[
                    "living-room-curtain"
                  ]?.open !== true
                ) {
                  roomSolarGain *=
                    0.35;
                }

                const solarMrtTarget =
                  temperature +
                  solarFactor *
                  roomSolarGain *
                  5;

                mrt +=
                  (
                    solarMrtTarget -
                    mrt
                  ) * 0.04;

                // --------------------------------------------
                // Bedroom air conditioner
                // --------------------------------------------

                if (
                  roomName ===
                    "Bedroom" &&
                  deviceStates[
                    "bedroom-ac"
                  ]?.power === true
                ) {
                  const target = 23;

                  temperature +=
                    (
                      target -
                      temperature
                    ) * 0.025;

                  humidity +=
                    (
                      48 -
                      humidity
                    ) * 0.012;
                }

                // --------------------------------------------
                // Internal equipment heat
                // --------------------------------------------

                const activeLight =
                  roomName ===
                    "Living Room"
                    ? deviceStates[
                        "living-room-light-main"
                      ]?.power
                    : roomName ===
                        "Bedroom"
                      ? deviceStates[
                          "bedroom-light"
                        ]?.power
                      : roomName ===
                          "Kitchen"
                        ? deviceStates[
                            "kitchen-light"
                          ]?.power
                        : false;

                if (activeLight) {
                  temperature +=
                    0.0015;

                  mrt +=
                    0.003;
                }

                if (
                  roomName ===
                    "Living Room" &&
                  deviceStates[
                    "living-room-tv"
                  ]?.power === true
                ) {
                  temperature +=
                    0.002;
                }

                // --------------------------------------------
                // Balcony irrigation
                // --------------------------------------------

                if (
                  roomName ===
                    "Balcony" &&
                  deviceStates[
                    "balcony-irrigation"
                  ]?.power === true
                ) {
                  humidity +=
                    0.035;

                  temperature -=
                    0.002;
                }

                return {
                  temperature:
                    clamp(
                      temperature,
                      -10,
                      50,
                    ),

                  relativeHumidity:
                    clamp(
                      humidity,
                      0,
                      100,
                    ),

                  airSpeed:
                    clamp(
                      airSpeed,
                      0,
                      5,
                    ),

                  meanRadiantTemperature:
                    clamp(
                      mrt,
                      -10,
                      70,
                    ),
                };
              },
            );
          },
        );
      }, 1000);

    return () =>
      window.clearInterval(
        timer,
      );
  }, [
    deviceStates,
    global.ach,
    global.outdoorTemperature,
    global.outdoorHumidity,
    global.outdoorWindSpeed,
    global.solarLatitude,
    global.solarLongitude,
    global.solarDateTime,
    updateRoom,
  ]);

  // ==========================================================
  // PET request for currently selected room
  // ==========================================================

  useEffect(() => {
    const controller =
      new AbortController();

    const timer =
      window.setTimeout(
        async () => {
          global.setAnalysisLoading(
            true,
          );

          global.setAnalysisError(
            null,
          );

          try {
            const result =
              await analyzeEnvironment(
                {
                  temperature:
                    values.temperature,

                  relative_humidity:
                    values.relativeHumidity,

                  air_speed:
                    values.airSpeed,

                  mean_radiant_temperature:
                    values.meanRadiantTemperature,

                  met:
                    global.met,

                  clo:
                    global.clo,
                },

                controller.signal,
              );

            global.setAnalysis(
              result,
            );
          } catch (error) {
            if (
              error instanceof
                DOMException &&
              error.name ===
                "AbortError"
            ) {
              return;
            }

            global.setAnalysisError(
              "PET API unavailable",
            );
          } finally {
            global.setAnalysisLoading(
              false,
            );
          }
        },
        250,
      );

    return () => {
      window.clearTimeout(
        timer,
      );

      controller.abort();
    };
  }, [
    room,
    values.temperature,
    values.relativeHumidity,
    values.airSpeed,
    values.meanRadiantTemperature,
    global.met,
    global.clo,
  ]);

  const sun =
    useMemo(
      () =>
        SunCalc.getPosition(
          new Date(
            global.solarDateTime,
          ),
          global.solarLatitude,
          global.solarLongitude,
        ),
      [
        global.solarDateTime,
        global.solarLatitude,
        global.solarLongitude,
      ],
    );

  return (
    <section className="environment-analysis">
      <div className="analysis-header">
        <span>
          ROOM ENVIRONMENT
        </span>

        <span className="analysis-model">
          {room.toUpperCase()}
        </span>
      </div>

      <div className="environment-grid">

        <label>
          <span>AIR TEMP</span>

          <input
            type="number"
            step="0.1"
            value={
              values.temperature.toFixed(
                2,
              )
            }
            onChange={(event) =>
              setRoom(
                room,
                {
                  temperature:
                    Number(
                      event.target.value,
                    ),
                },
              )
            }
          />

          <small>C</small>
        </label>

        <label>
          <span>HUMIDITY</span>

          <input
            type="number"
            step="0.1"
            value={
              values.relativeHumidity.toFixed(
                1,
              )
            }
            onChange={(event) =>
              setRoom(
                room,
                {
                  relativeHumidity:
                    Number(
                      event.target.value,
                    ),
                },
              )
            }
          />

          <small>%</small>
        </label>

        <label>
          <span>AIR SPEED</span>

          <input
            type="number"
            step="0.01"
            value={
              values.airSpeed.toFixed(
                2,
              )
            }
            onChange={(event) =>
              setRoom(
                room,
                {
                  airSpeed:
                    Number(
                      event.target.value,
                    ),
                },
              )
            }
          />

          <small>m/s</small>
        </label>

        <label>
          <span>MRT</span>

          <input
            type="number"
            step="0.1"
            value={
              values.meanRadiantTemperature.toFixed(
                2,
              )
            }
            onChange={(event) =>
              setRoom(
                room,
                {
                  meanRadiantTemperature:
                    Number(
                      event.target.value,
                    ),
                },
              )
            }
          />

          <small>C</small>
        </label>

      </div>

      <div className="pet-result">
        <div>
          <span>
            PHYSIOLOGICAL
            EQUIVALENT TEMPERATURE
          </span>

          <strong>
            {global.analysisLoading
              ? "..."
              : global.analysis
                ? `${global.analysis.pet.toFixed(
                    2,
                  )} C`
                : "--"}
          </strong>
        </div>

        <div className="pet-comfort-label">
          {global.analysis?.comfort ??
            "NO DATA"}
        </div>
      </div>

      <p className="analysis-note">
        PET uses the backend
        pythermalcomfort model.
        Room conditions are currently
        reduced-order simulation values.
      </p>

      <div className="analysis-divider" />

      <div className="analysis-header">
        <span>
          OUTDOOR / VENTILATION
        </span>

        <span className="analysis-model">
          REDUCED ORDER
        </span>
      </div>

      <div className="environment-grid">

        <label>
          <span>OUTDOOR TEMP</span>

          <input
            type="number"
            step="0.1"
            value={
              global.outdoorTemperature
            }
            onChange={(event) =>
              global.setValues({
                outdoorTemperature:
                  Number(
                    event.target.value,
                  ),
              })
            }
          />

          <small>C</small>
        </label>

        <label>
          <span>OUTDOOR RH</span>

          <input
            type="number"
            step="1"
            value={
              global.outdoorHumidity
            }
            onChange={(event) =>
              global.setValues({
                outdoorHumidity:
                  Number(
                    event.target.value,
                  ),
              })
            }
          />

          <small>%</small>
        </label>

        <label>
          <span>ACH</span>

          <input
            type="number"
            step="0.1"
            min="0"
            value={
              global.ach
            }
            onChange={(event) =>
              global.setValues({
                ach:
                  Number(
                    event.target.value,
                  ),
              })
            }
          />

          <small>1/h</small>
        </label>

        <label>
          <span>WIND</span>

          <input
            type="number"
            step="0.1"
            min="0"
            value={
              global.outdoorWindSpeed
            }
            onChange={(event) =>
              global.setValues({
                outdoorWindSpeed:
                  Number(
                    event.target.value,
                  ),
              })
            }
          />

          <small>m/s</small>
        </label>

      </div>

      <div className="analysis-divider" />

      <div className="analysis-header">
        <span>SOLAR</span>

        <span className="analysis-model">
          SUN POSITION
        </span>
      </div>

      <div className="solar-metrics">

        <div>
          <span>ALTITUDE</span>
          <strong>
            {sun.altitude.toFixed(1)}
          </strong>
        </div>

        <div>
          <span>AZIMUTH</span>
          <strong>
            {sun.azimuth.toFixed(1)}
          </strong>
        </div>

        <div>
          <span>TIME</span>
          <strong>
            {
              global.solarDateTime
                .split("T")[1]
            }
          </strong>
        </div>

      </div>
    </section>
  );
}
import {
  Canvas,
} from "@react-three/fiber";

import {
  OrbitControls,
} from "@react-three/drei";

import {
  Suspense,
  useState,
} from "react";

import {
  DemoHouse,
} from "./scene/house/DemoHouse";

import {
  demoDevices,
  demoDeviceMap,
} from "./data/demoDevices";

import type {
  DemoDevice,
  DeviceProperties,
  DeviceStateMap,
} from "./types/device";

import { EnvironmentPanel } from "./components/environment/EnvironmentPanel";
import { SolarLighting } from "./scene/environment/SolarLighting";
import "./App.css";

function getDeviceStatus(
  device: DemoDevice,
  properties: DeviceProperties,
) {
  if (
    device.type === "smoke_sensor"
  ) {
    return String(
      properties.status ?? "UNKNOWN",
    ).toUpperCase();
  }

  if (
    device.type === "curtain"
  ) {
    return properties.open === true
      ? "OPEN"
      : "CLOSED";
  }

  if (
    typeof properties.power ===
    "boolean"
  ) {
    return properties.power
      ? "ON"
      : "OFF";
  }

  return "READY";
}

function getActionLabel(
  device: DemoDevice,
  properties: DeviceProperties,
) {
  if (
    device.type === "curtain"
  ) {
    return properties.open === true
      ? "CLOSE CURTAIN"
      : "OPEN CURTAIN";
  }

  if (
    typeof properties.power ===
    "boolean"
  ) {
    return properties.power
      ? "TURN OFF"
      : "TURN ON";
  }

  return "NO CONTROL";
}

export default function App() {
  const [
    selectedDeviceId,
    setSelectedDeviceId,
  ] = useState(
    "living-room-light-main",
  );

  const [
    deviceStates,
    setDeviceStates,
  ] = useState<DeviceStateMap>(() => {
    return Object.fromEntries(
      demoDevices.map((device) => [
        device.id,
        {
          ...device.properties,
        },
      ]),
    ) as DeviceStateMap;
  });

  const selectedDevice =
    demoDeviceMap.get(
      selectedDeviceId,
    ) ?? demoDevices[0];

  const selectedProperties =
    deviceStates[selectedDevice.id] ??
    selectedDevice.properties;

  const selectedStatus =
    getDeviceStatus(
      selectedDevice,
      selectedProperties,
    );

  const toggleSelectedDevice = () => {
    if (
      !selectedDevice.controllable
    ) {
      return;
    }

    setDeviceStates((current) => {
      const currentProperties =
        current[selectedDevice.id] ?? {
          ...selectedDevice.properties,
        };

      const nextProperties = {
        ...currentProperties,
      };

      if (
        typeof nextProperties.power ===
        "boolean"
      ) {
        nextProperties.power =
          !nextProperties.power;

        if (
          selectedDevice.type ===
          "irrigation"
        ) {
          nextProperties.flow =
            nextProperties.power
              ? 2.4
              : 0;
        }
      } else if (
        typeof nextProperties.open ===
        "boolean"
      ) {
        nextProperties.open =
          !nextProperties.open;
      }

      return {
        ...current,
        [selectedDevice.id]:
          nextProperties,
      };
    });
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand-line">
            <span className="brand-mark">
              TAO
            </span>

            <span className="brand-separator">
              /
            </span>

            <span>
              DIGITAL TWIN
            </span>
          </div>

          <p>
            Demo House  Device Simulation
          </p>
        </div>

        <div className="connection">
          <span className="connection-dot online" />
          LOCAL SIMULATION
        </div>
      </header>

      <section className="house-layout">
        <section className="house-scene-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                DIGITAL SPACE
              </span>

              <h1>
                Demo House
              </h1>
            </div>

            <div className="scene-meta">
              <span>
                4 ROOMS
              </span>

              <span>
                8 DEVICES
              </span>
            </div>
          </div>

          <div className="canvas-wrap">
            <Canvas
              shadows
              camera={{
                position: [
                  11,
                  10,
                  13,
                ],
                fov: 42,
              }}
            >
              <color
                attach="background"
                args={[
                  "#071018",
                ]}
              />

                            <SolarLighting />

              <ambientLight
                intensity={0.4}
              />

              <directionalLight
                position={[
                  8,
                  12,
                  8,
                ]}
                intensity={1.2}
                castShadow
              />

              <mesh
                rotation={[
                  -Math.PI / 2,
                  0,
                  0,
                ]}
                position={[
                  0,
                  -0.04,
                  0,
                ]}
                receiveShadow
              >
                <planeGeometry
                  args={[
                    32,
                    32,
                  ]}
                />

                <meshStandardMaterial
                  color="#071118"
                  roughness={0.96}
                />
              </mesh>

              <gridHelper
                args={[
                  32,
                  32,
                  "#23495d",
                  "#102b38",
                ]}
                position={[
                  0,
                  0.01,
                  0,
                ]}
              />

              <Suspense fallback={null}>
                <DemoHouse
                  selectedDeviceId={
                    selectedDeviceId
                  }
                  deviceStates={
                    deviceStates
                  }
                  onSelectDevice={
                    setSelectedDeviceId
                  }
                />
              </Suspense>

              <OrbitControls
                makeDefault
                target={[
                  0,
                  1,
                  0,
                ]}
                enableDamping
                dampingFactor={0.07}
                minDistance={5}
                maxDistance={28}
              />
            </Canvas>

            <div className="scene-help">
              CLICK DEVICE / DRAG TO ROTATE /
              SCROLL TO ZOOM
            </div>
          </div>
        </section>

        <aside className="house-sidebar">
          <div className="detail-heading">
            <span>
              SELECTED DEVICE
            </span>

            <span>
              {
                selectedDevice.room
              }
            </span>
          </div>

          <section className="house-device-card">
            <span className="house-room-name">
              {
                selectedDevice.type
                  .replaceAll("_", " ")
                  .toUpperCase()
              }
            </span>

            <h2>
              {
                selectedDevice.name
              }
            </h2>

            <div
              className={`house-power-state ${
                selectedStatus === "ON" ||
                selectedStatus === "OPEN" ||
                selectedStatus === "NORMAL"
                  ? "on"
                  : ""
              }`}
            >
              {selectedStatus}
            </div>

            {selectedDevice.controllable ? (
              <button
                className="house-toggle-button"
                onClick={
                  toggleSelectedDevice
                }
              >
                {getActionLabel(
                  selectedDevice,
                  selectedProperties,
                )}
              </button>
            ) : (
              <div className="sensor-readonly">
                SENSOR  READ ONLY
              </div>
            )}

            <div className="device-properties">
              {Object.entries(
                selectedProperties,
              ).map(
                ([key, value]) => (
                  <div
                    className="device-property-row"
                    key={key}
                  >
                    <span>
                      {key}
                    </span>

                    <strong>
                      {String(value)}
                    </strong>
                  </div>
                ),
              )}
            </div>

            <p>
              TAO Entity
              <br />

              <strong>
                {
                  selectedDevice.id
                }
              </strong>
            </p>

            <p>
              Scene Node
              <br />

              <strong>
                {
                  selectedDevice.sceneNode
                }
              </strong>
            </p>
          </section>

          <section className="device-list-section">
            <div className="device-list-title">
              DEVICE REGISTRY
              <span>
                {demoDevices.length}
              </span>
            </div>

            <div className="device-list">
              {demoDevices.map(
                (device) => {
                  const properties =
                    deviceStates[
                      device.id
                    ];

                  const status =
                    getDeviceStatus(
                      device,
                      properties,
                    );

                  return (
                    <button
                      key={
                        device.id
                      }
                      className={`device-list-button ${
                        device.id ===
                        selectedDeviceId
                          ? "selected"
                          : ""
                      }`}
                      onClick={() =>
                        setSelectedDeviceId(
                          device.id,
                        )
                      }
                    >
                      <span className="device-list-main">
                        <strong>
                          {
                            device.name
                          }
                        </strong>

                        <small>
                          {
                            device.room
                          }
                        </small>
                      </span>

                      <span
                        className={`device-list-state ${
                          status ===
                            "ON" ||
                          status ===
                            "OPEN" ||
                          status ===
                            "NORMAL"
                            ? "active"
                            : ""
                        }`}
                      >
                        {status}
                      </span>
                    </button>
                  );
                },
              )}
            </div>
          </section>
                  <EnvironmentPanel
  selectedRoom={selectedDevice.room}
  deviceStates={deviceStates}
/>
        </aside>
      </section>
    </main>
  );
}
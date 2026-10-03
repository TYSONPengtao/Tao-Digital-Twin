import { Canvas } from "@react-three/fiber";
import { Html, OrbitControls } from "@react-three/drei";
import { useEffect, useMemo, useState } from "react";
import "./App.css";

type DeviceStatus = "online" | "warning";

type Device = {
  id: string;
  name: string;
  status: DeviceStatus;
  temperature: number;
  load: number;
  timestamp: string;
};

const devicePositions: [number, number, number][] = [
  [-4, 0.65, -2],
  [-2, 0.65, 2],
  [0, 0.65, -1],
  [2, 0.65, 2],
  [4, 0.65, -2],
];

function TwinDevice({
  device,
  position,
  selected,
  onSelect,
}: {
  device: Device;
  position: [number, number, number];
  selected: boolean;
  onSelect: () => void;
}) {
  const color = device.status === "warning" ? "#ffad33" : "#4cffb0";

  return (
    <group position={position}>
      <mesh
        castShadow
        receiveShadow
        scale={selected ? 1.14 : 1}
        onClick={(event) => {
          event.stopPropagation();
          onSelect();
        }}
      >
        <boxGeometry args={[1.5, 0.9, 1.5]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={selected ? 0.55 : 0.16}
          metalness={0.45}
          roughness={0.35}
        />
      </mesh>

      <mesh position={[0, -0.55, 0]} receiveShadow>
        <cylinderGeometry args={[0.85, 1, 0.22, 32]} />
        <meshStandardMaterial color="#1b2530" metalness={0.7} roughness={0.35} />
      </mesh>

      <Html position={[0, 1.25, 0]} center distanceFactor={11}>
        <button
          className={`device-label ${selected ? "selected" : ""}`}
          onClick={onSelect}
        >
          <span className="status-dot" style={{ background: color }} />
          {device.name}
        </button>
      </Html>
    </group>
  );
}

function Scene({
  devices,
  selectedId,
  onSelect,
}: {
  devices: Device[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}) {
  return (
    <Canvas
      shadows
      camera={{ position: [8, 7, 10], fov: 45 }}
      onPointerMissed={() => onSelect(null)}
    >
      <color attach="background" args={["#071018"]} />

      <ambientLight intensity={1.1} />

      <directionalLight
        castShadow
        position={[8, 12, 7]}
        intensity={2.5}
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />

      <pointLight position={[-8, 5, -5]} intensity={18} color="#1677ff" />

      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[30, 24]} />
        <meshStandardMaterial
          color="#0b1620"
          metalness={0.15}
          roughness={0.85}
        />
      </mesh>

      <gridHelper
        args={[24, 24, "#24475e", "#142b3a"]}
        position={[0, 0.012, 0]}
      />

      {devices.map((device, index) => (
        <TwinDevice
          key={device.id}
          device={device}
          position={devicePositions[index] ?? [0, 0.65, 0]}
          selected={selectedId === device.id}
          onSelect={() => onSelect(device.id)}
        />
      ))}

      <OrbitControls
        makeDefault
        enableDamping
        dampingFactor={0.07}
        minDistance={6}
        maxDistance={22}
        maxPolarAngle={Math.PI / 2.05}
      />
    </Canvas>
  );
}

export default function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("--");

  useEffect(() => {
    let active = true;

    const loadDevices = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/devices");

        if (!response.ok) {
          throw new Error("API request failed");
        }

        const data: Device[] = await response.json();

        if (!active) return;

        setDevices(data);
        setConnected(true);
        setLastUpdate(new Date().toLocaleTimeString());
      } catch {
        if (!active) return;
        setConnected(false);
      }
    };

    loadDevices();

    const timer = window.setInterval(loadDevices, 2000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const selectedDevice = useMemo(
    () => devices.find((device) => device.id === selectedId) ?? null,
    [devices, selectedId],
  );

  const onlineCount = devices.filter(
    (device) => device.status === "online",
  ).length;

  const warningCount = devices.filter(
    (device) => device.status === "warning",
  ).length;

  const averageTemperature =
    devices.length > 0
      ? (
          devices.reduce((sum, device) => sum + device.temperature, 0) /
          devices.length
        ).toFixed(1)
      : "--";

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand-line">
            <span className="brand-mark">TAO</span>
            <span className="brand-separator">/</span>
            <span>DIGITAL TWIN</span>
          </div>
          <p>Realtime spatial monitoring prototype</p>
        </div>

        <div className="connection">
          <span className={`connection-dot ${connected ? "online" : "offline"}`} />
          {connected ? "API CONNECTED" : "API OFFLINE"}
        </div>
      </header>

      <section className="dashboard">
        <div className="scene-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">LIVE SCENE</span>
              <h1>Facility Twin</h1>
            </div>

            <div className="scene-meta">
              <span>5 DEVICES</span>
              <span>UPDATE {lastUpdate}</span>
            </div>
          </div>

          <div className="canvas-wrap">
            <Scene
              devices={devices}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />

            <div className="scene-help">
              DRAG TO ROTATE / SCROLL TO ZOOM / CLICK DEVICE
            </div>
          </div>
        </div>

        <aside className="sidebar">
          <section className="summary-grid">
            <article className="metric-card">
              <span>ONLINE</span>
              <strong>{onlineCount}</strong>
            </article>

            <article className="metric-card warning">
              <span>WARNING</span>
              <strong>{warningCount}</strong>
            </article>

            <article className="metric-card wide">
              <span>AVG TEMP</span>
              <strong>{averageTemperature} C</strong>
            </article>
          </section>

          <section className="detail-panel">
            <div className="detail-heading">
              <span>DEVICE INSPECTOR</span>
              <span>{selectedDevice ? selectedDevice.id : "--"}</span>
            </div>

            {selectedDevice ? (
              <>
                <div className="selected-title">
                  <div
                    className={`large-status ${
                      selectedDevice.status === "warning"
                        ? "warning"
                        : "online"
                    }`}
                  />
                  <div>
                    <h2>{selectedDevice.name}</h2>
                    <p>{selectedDevice.status.toUpperCase()}</p>
                  </div>
                </div>

                <div className="telemetry">
                  <div>
                    <span>TEMPERATURE</span>
                    <strong>{selectedDevice.temperature} C</strong>
                  </div>

                  <div>
                    <span>LOAD</span>
                    <strong>{selectedDevice.load}%</strong>
                  </div>
                </div>

                <div className="load-block">
                  <div className="load-header">
                    <span>DEVICE LOAD</span>
                    <span>{selectedDevice.load}%</span>
                  </div>

                  <div className="load-track">
                    <div
                      className="load-value"
                      style={{
                        width: `${Math.min(selectedDevice.load, 100)}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="timestamp">
                  LAST TELEMETRY
                  <br />
                  {new Date(selectedDevice.timestamp).toLocaleString()}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-symbol">+</div>
                <p>Select a device in the 3D scene to inspect live telemetry.</p>
              </div>
            )}
          </section>

          <section className="device-list">
            <div className="detail-heading">
              <span>ASSETS</span>
              <span>{devices.length}</span>
            </div>

            {devices.map((device) => (
              <button
                key={device.id}
                className={selectedId === device.id ? "active" : ""}
                onClick={() => setSelectedId(device.id)}
              >
                <span
                  className={`list-dot ${
                    device.status === "warning" ? "warning" : "online"
                  }`}
                />
                <span>{device.name}</span>
                <small>{device.temperature} C</small>
              </button>
            ))}
          </section>
        </aside>
      </section>
    </main>
  );
}
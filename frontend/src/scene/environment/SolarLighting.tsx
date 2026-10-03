import { useMemo } from "react";
import * as THREE from "three";
import * as SunCalc from "suncalc";

import {
  useEnvironmentStore,
} from "../../stores/environmentStore";

export function SolarLighting() {
  const latitude =
    useEnvironmentStore(
      (state) =>
        state.solarLatitude,
    );

  const longitude =
    useEnvironmentStore(
      (state) =>
        state.solarLongitude,
    );

  const dateTime =
    useEnvironmentStore(
      (state) =>
        state.solarDateTime,
    );

  const sun = useMemo(() => {
    const date = new Date(dateTime);

    const position =
      SunCalc.getPosition(
        date,
        latitude,
        longitude,
      );

    const altitude =
      THREE.MathUtils.degToRad(
        position.altitude,
      );

    const azimuth =
      THREE.MathUtils.degToRad(
        position.azimuth,
      );

    const radius = 18;

    // Three.js convention used here:
    // +Y = up
    // -Z = north
    // +X = east
    const horizontal =
      Math.cos(altitude) *
      radius;

    const x =
      Math.sin(azimuth) *
      horizontal;

    const y =
      Math.sin(altitude) *
      radius;

    const z =
      -Math.cos(azimuth) *
      horizontal;

    return {
      altitude:
        position.altitude,

      azimuth:
        position.azimuth,

      position: [
        x,
        y,
        z,
      ] as [
        number,
        number,
        number,
      ],
    };
  }, [
    latitude,
    longitude,
    dateTime,
  ]);

  if (sun.altitude <= 0) {
    return null;
  }

  const altitudeFactor =
    Math.max(
      0.15,
      Math.sin(
        THREE.MathUtils.degToRad(
          sun.altitude,
        ),
      ),
    );

  return (
    <>
      <directionalLight
        position={sun.position}
        intensity={
          1.8 * altitudeFactor
        }
        color="#fff1d0"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-left={-14}
        shadow-camera-right={14}
        shadow-camera-top={14}
        shadow-camera-bottom={-14}
        shadow-camera-near={0.1}
        shadow-camera-far={50}
      />

      <mesh
        position={sun.position}
      >
        <sphereGeometry
          args={[
            0.32,
            24,
            24,
          ]}
        />

        <meshBasicMaterial
          color="#fff1a6"
        />
      </mesh>
    </>
  );
}
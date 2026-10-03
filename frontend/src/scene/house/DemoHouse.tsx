import {
  Html,
  useGLTF,
} from "@react-three/drei";

import type {
  ThreeEvent,
} from "@react-three/fiber";

import {
  useEffect,
  useMemo,
} from "react";

import * as THREE from "three";

import {
  demoDevices,
  sceneNodeDeviceMap,
} from "../../data/demoDevices";

import type {
  DeviceStateMap,
} from "../../types/device";

import {
  useEnvironmentStore,
} from "../../stores/environmentStore";

const MODEL_URL =
  "/models/tao-demo-house-v0.1/demo-house.glb";

type DemoHouseProps = {
  selectedDeviceId: string;

  deviceStates:
    DeviceStateMap;

  onSelectDevice: (
    deviceId: string,
  ) => void;
};

function AirflowArrow({
  start,
  end,
}: {
  start: [
    number,
    number,
    number,
  ];

  end: [
    number,
    number,
    number,
  ];
}) {
  const arrow =
    useMemo(() => {
      const origin =
        new THREE.Vector3(
          ...start,
        );

      const destination =
        new THREE.Vector3(
          ...end,
        );

      const direction =
        destination
          .clone()
          .sub(origin);

      const length =
        direction.length();

      direction.normalize();

      return new THREE.ArrowHelper(
        direction,
        origin,
        length,
        0x36d9ff,
        0.32,
        0.16,
      );
    }, [
      start[0],
      start[1],
      start[2],
      end[0],
      end[1],
      end[2],
    ]);

  return (
    <primitive object={arrow} />
  );
}

function CeilingLight({
  position,
}: {
  position: [
    number,
    number,
    number,
  ];
}) {
  const target =
    useMemo(
      () =>
        new THREE.Object3D(),
      [],
    );

  return (
    <>
      <primitive
        object={target}
        position={[
          position[0],
          0.15,
          position[2],
        ]}
      />

      <spotLight
        position={[
          position[0],
          position[1] - 0.05,
          position[2],
        ]}
        target={target}
        intensity={55}
        distance={7}
        angle={Math.PI / 3.1}
        penumbra={0.7}
        decay={2}
        color="#ffe1a0"
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />

      <pointLight
        position={[
          position[0],
          position[1] - 0.12,
          position[2],
        ]}
        intensity={3.5}
        distance={1.8}
        decay={2}
        color="#fff0c4"
      />

      <mesh
        position={position}
      >
        <sphereGeometry
          args={[
            0.12,
            20,
            20,
          ]}
        />

        <meshStandardMaterial
          color="#fff7d5"
          emissive="#ffd86d"
          emissiveIntensity={7}
        />
      </mesh>
    </>
  );
}

export function DemoHouse({
  selectedDeviceId,
  deviceStates,
  onSelectDevice,
}: DemoHouseProps) {
  const gltf =
    useGLTF(MODEL_URL);

  const ach =
    useEnvironmentStore(
      (state) =>
        state.ach,
    );

  const scene =
    useMemo(() => {
      const clone =
        gltf.scene.clone(true);

      clone.traverse(
        (object) => {
          if (
            !(
              object instanceof
              THREE.Mesh
            )
          ) {
            return;
          }

          object.castShadow =
            true;

          object.receiveShadow =
            true;

          if (
            Array.isArray(
              object.material,
            )
          ) {
            object.material =
              object.material.map(
                (material) =>
                  material.clone(),
              );
          } else if (
            object.material
          ) {
            object.material =
              object.material.clone();
          }
        },
      );

      clone.rotation.x =
        -Math.PI / 2;

      clone.updateMatrixWorld(
        true,
      );

      const box =
        new THREE.Box3()
          .setFromObject(
            clone,
          );

      const center =
        box.getCenter(
          new THREE.Vector3(),
        );

      clone.position.x -=
        center.x;

      clone.position.z -=
        center.z;

      clone.position.y -=
        box.min.y;

      clone.updateMatrixWorld(
        true,
      );

      return clone;
    }, [gltf.scene]);

  const devicePositions =
    useMemo(() => {
      scene.updateMatrixWorld(
        true,
      );

      const positions:
        Record<
          string,
          [
            number,
            number,
            number,
          ]
        > = {};

      demoDevices.forEach(
        (device) => {
          const target =
            scene.getObjectByName(
              device.sceneNode,
            );

          if (!target) {
            console.warn(
              `Scene node not found: ${device.sceneNode}`,
            );

            return;
          }

          const position =
            new THREE.Vector3();

          target.getWorldPosition(
            position,
          );

          positions[
            device.id
          ] = [
            position.x,
            position.y,
            position.z,
          ];
        },
      );

      return positions;
    }, [scene]);

  useEffect(() => {
    demoDevices.forEach(
      (device) => {
        const target =
          scene.getObjectByName(
            device.sceneNode,
          );

        if (!target) {
          return;
        }

        const properties =
          deviceStates[
            device.id
          ] ??
          device.properties;

        const selected =
          device.id ===
          selectedDeviceId;

        const powered =
          properties.power ===
          true;

        target.traverse(
          (object) => {
            if (
              !(
                object instanceof
                THREE.Mesh
              )
            ) {
              return;
            }

            const materials =
              Array.isArray(
                object.material,
              )
                ? object.material
                : [
                    object.material,
                  ];

            materials.forEach(
              (material) => {
                if (
                  !(
                    material instanceof
                    THREE.MeshStandardMaterial
                  )
                ) {
                  return;
                }

                if (
                  device.type ===
                    "light" &&
                  powered
                ) {
                  material.emissive.set(
                    "#ffe5a0",
                  );

                  material.emissiveIntensity =
                    4;
                } else if (
                  selected
                ) {
                  material.emissive.set(
                    "#18c8ff",
                  );

                  material.emissiveIntensity =
                    0.75;
                } else {
                  material.emissive.set(
                    "#000000",
                  );

                  material.emissiveIntensity =
                    0;
                }

                material.needsUpdate =
                  true;
              },
            );
          },
        );
      },
    );
  }, [
    scene,
    selectedDeviceId,
    deviceStates,
  ]);

  const findDevice =
    (
      start:
        THREE.Object3D,
    ) => {
      let object:
        | THREE.Object3D
        | null = start;

      while (object) {
        const device =
          sceneNodeDeviceMap.get(
            object.name,
          );

        if (device) {
          return device;
        }

        object =
          object.parent;
      }

      return null;
    };

  const handleClick =
    (
      event:
        ThreeEvent<MouseEvent>,
    ) => {
      const device =
        findDevice(
          event.object,
        );

      if (!device) {
        return;
      }

      event.stopPropagation();

      onSelectDevice(
        device.id,
      );
    };

  const handlePointerOver =
    (
      event:
        ThreeEvent<PointerEvent>,
    ) => {
      const device =
        findDevice(
          event.object,
        );

      if (!device) {
        return;
      }

      event.stopPropagation();

      document.body.style.cursor =
        "pointer";
    };

  const handlePointerOut =
    () => {
      document.body.style.cursor =
        "default";
    };

  const selectedPosition =
    devicePositions[
      selectedDeviceId
    ] ??
    ([0, 2.5, 0] as [
      number,
      number,
      number,
    ]);

  const activeLights =
    demoDevices.filter(
      (device) => {
        if (
          device.type !==
          "light"
        ) {
          return false;
        }

        return (
          deviceStates[
            device.id
          ]?.power === true
        );
      },
    );

  const living =
    devicePositions[
      "living-room-light-main"
    ];

  const bedroom =
    devicePositions[
      "bedroom-light"
    ];

  const kitchen =
    devicePositions[
      "kitchen-light"
    ];

  const balcony =
    devicePositions[
      "balcony-irrigation"
    ];

  const breathingPoint =
    (
      point:
        | [
            number,
            number,
            number,
          ]
        | undefined,
    ):
      | [
          number,
          number,
          number,
        ]
      | undefined => {
      if (!point) {
        return undefined;
      }

      return [
        point[0],
        1.25,
        point[2],
      ];
    };

  return (
    <group>
      <primitive
        object={scene}
        onClick={
          handleClick
        }
        onPointerOver={
          handlePointerOver
        }
        onPointerOut={
          handlePointerOut
        }
      />

      {activeLights.map(
        (device) => {
          const position =
            devicePositions[
              device.id
            ];

          if (!position) {
            return null;
          }

          return (
            <CeilingLight
              key={
                device.id
              }
              position={
                position
              }
            />
          );
        },
      )}

      {ach > 0 &&
        balcony &&
        living && (
          <AirflowArrow
            start={
              breathingPoint(
                balcony,
              )!
            }
            end={
              breathingPoint(
                living,
              )!
            }
          />
        )}

      {ach > 0 &&
        living &&
        bedroom && (
          <AirflowArrow
            start={
              breathingPoint(
                living,
              )!
            }
            end={
              breathingPoint(
                bedroom,
              )!
            }
          />
        )}

      {ach > 0 &&
        living &&
        kitchen && (
          <AirflowArrow
            start={
              breathingPoint(
                living,
              )!
            }
            end={
              breathingPoint(
                kitchen,
              )!
            }
          />
        )}

      <Html
        position={[
          selectedPosition[0],
          selectedPosition[1] +
            0.5,
          selectedPosition[2],
        ]}
        center
        distanceFactor={12}
      >
        <div className="selected-device-label">
          {
            demoDevices.find(
              (device) =>
                device.id ===
                selectedDeviceId,
            )?.name
          }
        </div>
      </Html>
    </group>
  );
}

useGLTF.preload(
  MODEL_URL,
);
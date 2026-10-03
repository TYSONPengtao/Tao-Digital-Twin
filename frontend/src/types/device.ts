export type DeviceType =
  | "light"
  | "tv"
  | "curtain"
  | "air_conditioner"
  | "smoke_sensor"
  | "irrigation";

export type DeviceValue =
  | boolean
  | number
  | string;

export type DeviceProperties =
  Record<string, DeviceValue>;

export type DeviceStateMap =
  Record<string, DeviceProperties>;

export interface DemoDevice {
  id: string;
  name: string;
  room: string;
  type: DeviceType;
  sceneNode: string;
  controllable: boolean;
  properties: DeviceProperties;
}
import type { DemoDevice } from "../types/device";

export const demoDevices: DemoDevice[] = [
  {
    id: "living-room-light-main",
    name: "Living Room Main Light",
    room: "Living Room",
    type: "light",
    sceneNode: "DEV_Light_Living_Main",
    controllable: true,
    properties: {
      power: false,
      brightness: 100,
    },
  },

  {
    id: "living-room-tv",
    name: "Living Room TV",
    room: "Living Room",
    type: "tv",
    sceneNode: "DEV_TV_Living",
    controllable: true,
    properties: {
      power: false,
    },
  },

  {
    id: "living-room-curtain",
    name: "Living Room Curtain",
    room: "Living Room",
    type: "curtain",
    sceneNode: "DEV_Curtain_Living",
    controllable: true,
    properties: {
      open: false,
    },
  },

  {
    id: "bedroom-light",
    name: "Bedroom Light",
    room: "Bedroom",
    type: "light",
    sceneNode: "DEV_Light_Bedroom",
    controllable: true,
    properties: {
      power: false,
      brightness: 100,
    },
  },

  {
    id: "bedroom-ac",
    name: "Bedroom Air Conditioner",
    room: "Bedroom",
    type: "air_conditioner",
    sceneNode: "DEV_AC_Bedroom",
    controllable: true,
    properties: {
      power: false,
      temperature: 24,
      mode: "cool",
    },
  },

  {
    id: "kitchen-light",
    name: "Kitchen Light",
    room: "Kitchen",
    type: "light",
    sceneNode: "DEV_Light_Kitchen",
    controllable: true,
    properties: {
      power: false,
      brightness: 100,
    },
  },

  {
    id: "kitchen-smoke-sensor",
    name: "Kitchen Smoke Sensor",
    room: "Kitchen",
    type: "smoke_sensor",
    sceneNode: "DEV_SmokeSensor_Kitchen",
    controllable: false,
    properties: {
      status: "normal",
      smoke: 0,
    },
  },

  {
    id: "balcony-irrigation",
    name: "Balcony Irrigation",
    room: "Balcony",
    type: "irrigation",
    sceneNode: "DEV_Irrigation_Balcony",
    controllable: true,
    properties: {
      power: false,
      flow: 0,
    },
  },
];

export const demoDeviceMap = new Map(
  demoDevices.map((device) => [
    device.id,
    device,
  ]),
);

export const sceneNodeDeviceMap = new Map(
  demoDevices.map((device) => [
    device.sceneNode,
    device,
  ]),
);
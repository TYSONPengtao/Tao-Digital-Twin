# TAO Home Digital Twin Architecture

## Goal

TAO brings the residential model, UE5 interactions, environment data and household device states into one home digital twin.

The local UE5 project has verified scene and environment workflows. The repository's Web client displays simulated telemetry. The layers below describe how both clients can share household state and commands when device adapters are ready. [Project history](history/README.md)

## Five-layer architecture

```text
1. Visualization
   Web / Three.js / Unreal Engine / VR / AR
                    |
                    v
2. TAO Core
   Device Registry
   State Manager
   Command Router
   Event Bus
   Automation / AI
                    |
                    v
3. Adapters
   Home Assistant / MQTT / Matter / Modbus / OPC UA / HTTP
                    |
                    v
4. Edge
   ESP32 / STM32 / Raspberry Pi / PLC / gateways
                    |
                    v
5. Physical World
   Lights / door and window motors / switches / sensors / cameras
```

## Core rule

Visualization clients never control physical hardware directly.

UE5 and Web clients communicate with TAO Core using stable platform APIs. TAO Core selects the correct adapter for each physical device.

## TAO Core responsibilities

### Device Registry
Maintains canonical identity and metadata for every controllable or observable entity.

### State Manager
Stores the latest known state of each entity and distributes changes.

### Command Router
Validates a command, resolves the target adapter and routes the command to the physical system.

### Event Bus
Normalizes incoming events so all clients receive the same state transitions regardless of protocol.

### Automation and AI
Future layer for rules, scheduling, anomaly detection and natural-language control. It must use the same command and state interfaces as human clients.

## Control flow

```text
UE5 / Web
   |
   | command
   v
TAO API
   |
Command Router
   |
Adapter
   |
Physical device
```

## State flow

```text
Physical device
   |
Adapter / Edge gateway
   |
Event Bus
   |
State Manager
   |
WebSocket
   |
+-- UE5
+-- Web
+-- Automation
+-- AI
```

## Adapter model

Adapters translate external systems into the canonical TAO model.

Initial adapter targets:

- Simulator
- Home Assistant
- MQTT
- Modbus
- OPC UA

Future adapters may include Matter, BACnet, CAN, Zigbee gateways or vendor APIs.

## Clients

### Web
The existing React + Three.js frontend remains the fast browser-based visualization and development client.

### Unreal Engine
The local UE5 scene supports walkthroughs, door and window poses, sun and night lighting, and wind data. The runtime connection to TAO Core is planned.

UE5 should use REST for queries/commands and WebSocket for realtime state synchronization.

## Home domain

Spaces represent the home, floors, rooms and courtyard. An observable device can be bound to a space and to one or more scene nodes. Geometry revisions, precomputed CFD data and device telemetry each retain their own source and validity. [Home domain](../domains/smart_home/README.md)

## Asset model

3D assets should bind scene nodes to stable TAO entity IDs.

Example:

```text
UE5 scene node:
LivingRoom_Light_Main

TAO entity:
living-room-light-main
```

The scene must not contain Home Assistant entity IDs, MQTT topics or PLC register addresses as its primary identity.

Those bindings belong in configuration and adapters.

## Persistence

The first platform milestone can run in memory.

Later:

- PostgreSQL for configuration and metadata
- TimescaleDB or another time-series store for telemetry history
- Object storage for models and large assets

## Deployment direction

Local-first deployment is preferred for physical control:

```text
LAN
├── TAO Core
├── MQTT broker
├── Home Assistant
├── UE5 workstation
├── Web clients
└── edge devices
```

Cloud services may be added later for remote access, backup or AI, but local control should not require the public internet.

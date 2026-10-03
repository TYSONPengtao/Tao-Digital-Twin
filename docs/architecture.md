# TAO Digital Twin Platform Architecture

## Goal

TAO Digital Twin Platform is a protocol-independent bridge between digital 3D environments and the physical world.

The platform must support multiple visualization clients, multiple device ecosystems and multiple application domains without coupling them together.

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
   Lights / pumps / valves / motors / sensors / cameras / equipment
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
UE5 will become the high-fidelity 3D client for real buildings, farms and other physical environments.

UE5 should use REST for queries/commands and WebSocket for realtime state synchronization.

## Domain modules

Initial domains:

- Smart Home
- Agriculture

Later domains may include:

- Building automation
- Energy
- Factory
- Environment

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

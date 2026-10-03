# TAO Digital Twin Platform

A modular digital twin platform that connects 3D virtual environments with real-world devices, sensors and control systems.

The long-term goal is to let a user view a real space in Web or Unreal Engine, inspect live state, and safely control physical equipment from the digital twin.

## Vision

TAO Digital Twin Platform separates visualization from physical-device protocols.

```text
Web / Three.js       Unreal Engine / VR / AR
       \                    /
        \                  /
         +---- TAO Core ---+
               |
      Device / State / Command / Event
               |
     +---------+---------+---------+
     |         |         |         |
Home Assistant MQTT    Modbus    OPC UA
     |         |         |         |
 Smart Home   ESP32    PLC/IO   Industrial
```

The same core can support:

- Smart homes
- Building automation
- Automatic irrigation
- Agriculture digital twins
- Energy systems
- Future industrial and environmental twins

## Current Foundation

The existing prototype already provides:

- React + TypeScript frontend
- Three.js / React Three Fiber scene
- FastAPI backend
- REST API
- WebSocket realtime telemetry
- Interactive virtual devices
- GitHub PR and semantic-version workflow
- Modular project structure

Current stable foundation: **v0.2.1**

## Platform Principles

1. **TAO Core is the center.** UE5, Web, Home Assistant and microcontrollers are clients or adapters.
2. **One canonical device model.** A virtual object never depends directly on a hardware brand or protocol.
3. **Bidirectional synchronization.** Virtual controls affect reality, and physical state changes update every client.
4. **Adapters isolate protocols.** MQTT, Home Assistant, Modbus and OPC UA remain outside domain logic.
5. **Safety before automation.** Commands to physical equipment must support validation, permissions, timeouts and fail-safe behavior.
6. **Local-first architecture.** The platform should continue to operate on a local network whenever possible.

## Repository Direction

```text
Tao-Digital-Twin/
├── frontend/                   # Existing Web / Three.js client
├── backend/
│   └── app/
│       ├── core/               # Device registry, state, commands, events
│       ├── api/                # REST interface
│       ├── websocket/          # Realtime synchronization
│       ├── models/             # Canonical domain models
│       ├── services/           # Application services
│       └── adapters/           # External protocols/platforms
├── clients/
│   └── unreal/                 # Future UE5 client
├── firmware/
│   ├── esp32/                  # Edge devices and smart switches
│   └── stm32/
├── domains/
│   ├── smart_home/
│   └── agriculture/
├── config/
├── assets/
└── docs/
```

## Example: Smart Home

```text
Click light in UE5
        |
        v
TAO Core command
        |
        v
Home Assistant or MQTT adapter
        |
        v
Physical light ON
        |
        v
State event returns to TAO Core
        |
        +--> UE5 updates
        +--> Web updates
```

## Example: Agriculture

```text
Soil sensor / water level / valve state
        |
      ESP32
        |
       MQTT
        |
     TAO Core
        |
        +--> UE5 farm twin
        +--> Web dashboard
        +--> Automation

User opens irrigation valve in the twin
        |
     TAO Core
        |
       MQTT
        |
      ESP32
        |
Physical solenoid valve
```

## Documentation

- [Architecture](docs/architecture.md)
- [Domain model](docs/domain-model.md)
- [Communication protocols](docs/protocols.md)
- [Safety and security](docs/security.md)
- [Roadmap](docs/roadmap.md)

## Author

TYSON Pengtao

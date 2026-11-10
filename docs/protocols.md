# Home Device Protocols

The Web simulator currently uses REST and WebSocket. The table describes the planned routes for connecting the local UE scene and household equipment.

| Connection | Primary protocol | Purpose |
| --- | --- | --- |
| Web -> TAO Core | REST + WebSocket | Query, command, realtime state |
| UE5 -> TAO Core | REST + WebSocket | High-fidelity twin control and synchronization |
| Home Assistant -> TAO Core | REST + WebSocket | Smart-home integration |
| ESP32 -> TAO Core | MQTT | Sensors, switches, relays, actuators |
| STM32 -> gateway/core | MQTT or serial gateway | Embedded control |
| Local control gateway -> TAO Core | Modbus / OPC UA | Household equipment that already uses a wired controller |
| Cameras | RTSP/WebRTC + TAO control API | Video plus device control |

## REST

Use for initial snapshots, entity discovery, configuration, commands and health checks.

## WebSocket

Use for realtime state updates, device availability, command results, alarms, and synchronization across Web and UE5.

## MQTT

Recommended topic pattern:

```text
tao/{domain}/{site}/{entity}/state
tao/{domain}/{site}/{entity}/set
tao/{domain}/{site}/{entity}/telemetry
tao/{domain}/{site}/{entity}/availability
```

MQTT topics are transport details, not canonical visualization identities.

## Modbus and OPC UA

Map registers, tags and nodes to stable TAO entity IDs through adapters.

## Versioning

Client-facing TAO APIs should be versioned independently of adapter implementations so UE5 scenes do not break when hardware integrations change.

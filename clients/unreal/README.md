# Unreal Engine Client

UE5 is the planned high-fidelity visualization and interaction client.

The [building digital twin field guide (中文)](../../docs/case-studies/ue5-building-twin.zh-CN.md) documents a separately verified local UE5 workflow. It covers asset identity, Datasmith reimport, scene interaction, and CFD. The responsibilities below describe the planned connection to TAO Core.

## Responsibilities

- Load real building, farm or facility scenes
- Bind Actors/Components to TAO entity IDs
- Query initial state using REST
- Receive realtime state using WebSocket
- Send user commands through the TAO API
- Visualize confirmed physical state

## Rule

UE5 must not directly depend on Home Assistant, MQTT topics, Modbus registers or PLC tags.

Example:

```text
UE5 Actor: BP_LivingRoomLight
TAO Entity: living-room-light-main

UE5 -> TAO Core -> Adapter -> Physical device
```

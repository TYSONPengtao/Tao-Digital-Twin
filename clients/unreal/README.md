# Unreal Engine Client

UE5 is the planned high-fidelity visualization and interaction client.

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

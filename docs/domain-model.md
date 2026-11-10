# TAO Home Domain Model

## Why a canonical model

TAO Core must present the same model to UE5 and Web regardless of whether a physical entity is connected through Home Assistant, MQTT, Modbus, OPC UA or a simulator.

## Space

A physical or logical location.

Examples:

- home
- building
- floor
- room
- courtyard
- utility room

## Entity

A stable TAO identity for something observable or controllable.

```json
{
  "id": "living-room-light-main",
  "name": "Living Room Main Light",
  "domain": "smart_home",
  "space_id": "living-room",
  "type": "light",
  "adapter": "home_assistant"
}
```

## State

```json
{
  "entity_id": "living-room-light-main",
  "online": true,
  "properties": {
    "power": true,
    "brightness": 80
  },
  "timestamp": "2026-10-03T14:00:00Z"
}
```

## Capability

Examples:

- power
- brightness
- color
- temperature
- humidity
- moisture
- pressure
- flow
- level
- open_close
- position
- video_stream

## Command

```json
{
  "command_id": "cmd-001",
  "entity_id": "kitchen-window-motor",
  "action": "open",
  "parameters": {},
  "source": "unreal"
}
```

A command should pass authorization, validation and safety checks before reaching an adapter.

## Event

Examples:

- state_changed
- command_requested
- command_completed
- command_failed
- device_online
- device_offline
- alarm_triggered

## Adapter binding

Home Assistant example:

```json
{
  "entity_id": "living-room-light-main",
  "adapter": "home_assistant",
  "binding": {
    "ha_entity_id": "light.living_room_main"
  }
}
```

MQTT example:

```json
{
  "entity_id": "kitchen-window-motor",
  "adapter": "mqtt",
  "binding": {
    "command_topic": "tao/smart_home/home/kitchen-window-motor/set",
    "state_topic": "tao/smart_home/home/kitchen-window-motor/state"
  }
}
```

## Scene binding

```json
{
  "scene": "home-main",
  "node": "LivingRoom_Light_Main",
  "entity_id": "living-room-light-main"
}
```

UE5, Three.js and future clients should all use the same TAO entity ID.

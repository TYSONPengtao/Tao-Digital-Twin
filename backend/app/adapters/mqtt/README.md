# MQTT Adapter

Primary path for custom ESP32/STM32 edge devices.

Responsibilities:

- Subscribe to state, telemetry and availability topics
- Publish validated commands
- Map MQTT topics/payloads to canonical TAO events
- Track device availability

MQTT topics remain behind the adapter boundary.

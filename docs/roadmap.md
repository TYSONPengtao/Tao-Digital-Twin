# TAO Digital Twin Platform Roadmap

## Phase 0 - Foundation

- [x] React + TypeScript frontend
- [x] Three.js / React Three Fiber prototype
- [x] FastAPI backend
- [x] REST API
- [x] WebSocket realtime telemetry
- [x] GitHub PR workflow
- [x] Semantic version tags
- [x] Modular repository structure

## Phase 1 - Platform Core

- [ ] Canonical Entity model
- [ ] Device Registry
- [ ] State Manager
- [ ] Command Router
- [ ] Event Bus
- [ ] Adapter interface
- [ ] Simulator adapter
- [ ] Versioned REST API
- [ ] Stable realtime event schema

## Phase 2 - Smart Home Pilot

- [ ] Home Assistant adapter
- [ ] MQTT adapter
- [ ] Import first real building model
- [ ] Map 3D scene nodes to TAO entities
- [ ] Control one real light from the digital twin
- [ ] Synchronize physical wall-switch changes back to the twin
- [ ] Add television / curtain / socket examples

## Phase 3 - Unreal Engine Client

- [ ] UE5 project/client skeleton
- [ ] REST client
- [ ] WebSocket client
- [ ] TAO Entity actor/component
- [ ] Runtime state synchronization
- [ ] Interactive device controls
- [ ] High-fidelity building visualization

## Phase 4 - Edge Hardware

- [ ] ESP32 firmware foundation
- [ ] MQTT device identity
- [ ] Relay output
- [ ] Physical switch input
- [ ] Sensor telemetry
- [ ] Availability / heartbeat
- [ ] OTA strategy
- [ ] STM32 gateway strategy

## Phase 5 - Agriculture Pilot

- [ ] Farm / greenhouse domain model
- [ ] Soil-moisture sensors
- [ ] Water-level sensors
- [ ] Pump model
- [ ] Solenoid valve model
- [ ] Irrigation-zone model
- [ ] Manual irrigation from UE5/Web
- [ ] Physical feedback confirmation
- [ ] Safe automatic irrigation rules

## Phase 6 - Automation Protocols

- [ ] Modbus adapter
- [ ] OPC UA adapter
- [ ] PLC integration
- [ ] Historical telemetry storage
- [ ] Alarm and event logging

## Phase 7 - Intelligence

- [ ] Rule engine
- [ ] Scheduling
- [ ] Anomaly detection
- [ ] Predictive maintenance
- [ ] Natural-language assistant
- [ ] AI-assisted operation with permission boundaries

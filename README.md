# Tao Digital Twin

Interactive web-based digital twin platform for 3D visualization, real-time telemetry and simulation.

## Current MVP

The first working prototype includes:

- Interactive 3D scene
- Five virtual devices
- Device selection
- Simulated telemetry
- Temperature monitoring
- Load monitoring
- Device status visualization
- FastAPI backend
- React frontend

## Architecture

```text
FastAPI
   |
   | REST API
   v
React + TypeScript
   |
   v
React Three Fiber
   |
   v
Three.js 3D Scene
```

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Three.js
- React Three Fiber
- Drei
- Zustand
- ECharts

### Backend

- Python
- FastAPI
- Uvicorn
- WebSocket

## Roadmap

- [x] Basic 3D scene
- [x] Virtual devices
- [x] Simulated telemetry
- [x] Device inspector
- [ ] WebSocket realtime telemetry
- [ ] Historical charts
- [ ] GLB / glTF models
- [ ] Alarm system
- [ ] PostgreSQL / TimescaleDB
- [ ] MQTT
- [ ] GIS / CesiumJS
- [ ] AI-assisted analysis

## Author

TYSON Pengtao

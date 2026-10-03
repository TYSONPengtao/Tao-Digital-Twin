# Tao Digital Twin Architecture

## Goal

Tao Digital Twin is designed as a modular digital twin platform for 3D visualization, realtime telemetry, simulation and future spatial intelligence.

## System Architecture

Frontend
  React + TypeScript
        |
        +-- UI Components
        +-- Three.js / React Three Fiber Scene
        +-- State Management
        +-- Telemetry Services
        |
        v
WebSocket / REST
        |
        v
Backend
  FastAPI
        |
        +-- API Routes
        +-- WebSocket Services
        +-- Domain Models
        +-- Telemetry Services
        |
        v
Future Infrastructure
        +-- PostgreSQL / TimescaleDB
        +-- MQTT
        +-- GIS / CesiumJS
        +-- AI Analysis

## Frontend Structure

- components/ : reusable interface components
- scene/ : Three.js and React Three Fiber scene logic
- services/ : HTTP and WebSocket clients
- stores/ : global application state
- types/ : shared TypeScript types

## Backend Structure

- api/ : REST API endpoints
- core/ : application configuration
- models/ : domain and API models
- services/ : business and telemetry logic
- websocket/ : realtime communication

## Asset Structure

- assets/models/ : GLB and glTF models
- assets/textures/ : model textures
- assets/gis/ : future GIS and spatial datasets

## Design Principle

The project separates rendering, data transport, state, domain logic and infrastructure so that future capabilities can be added without rewriting the core application.

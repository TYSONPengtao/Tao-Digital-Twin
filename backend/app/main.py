from datetime import datetime
import asyncio
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Tao Digital Twin API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_devices():
    return [
        {
            "id": f"device-{i:03d}",
            "name": f"Device {i:02d}",
            "status": random.choice(
                ["online", "online", "online", "warning"]
            ),
            "temperature": round(random.uniform(20, 40), 1),
            "load": round(random.uniform(10, 100), 1),
            "timestamp": datetime.now().isoformat(),
        }
        for i in range(1, 6)
    ]


@app.get("/")
def root():
    return {
        "project": "Tao Digital Twin",
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/api/devices")
def get_devices():
    return build_devices()


@app.websocket("/ws/telemetry")
async def telemetry(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await websocket.send_json(
                {
                    "type": "telemetry",
                    "devices": build_devices(),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass

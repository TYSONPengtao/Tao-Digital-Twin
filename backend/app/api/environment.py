from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.services.environment_service import (
    EnvironmentInput,
    analyze_environment,
)


router = APIRouter(
    prefix="/api/environment",
    tags=["environment"],
)


class EnvironmentAnalysisRequest(BaseModel):
    temperature: float = Field(
        default=25.0,
        ge=-30,
        le=60,
    )

    relative_humidity: float = Field(
        default=50.0,
        ge=0,
        le=100,
    )

    air_speed: float = Field(
        default=0.1,
        ge=0,
        le=20,
    )

    mean_radiant_temperature: float = Field(
        default=25.0,
        ge=-30,
        le=80,
    )

    met: float = Field(
        default=1.2,
        ge=0.7,
        le=4.0,
    )

    clo: float = Field(
        default=0.5,
        ge=0,
        le=4.0,
    )


@router.get("/health")
def environment_health():
    return {
        "status": "ok",
        "service": "TAO Environment Analysis",
        "pet_model": "MEMI / PET steady",
    }


@router.post("/pet")
def calculate_pet(
    payload: EnvironmentAnalysisRequest,
):
    data = EnvironmentInput(
        temperature=payload.temperature,
        relative_humidity=payload.relative_humidity,
        air_speed=payload.air_speed,
        mean_radiant_temperature=(
            payload.mean_radiant_temperature
        ),
        met=payload.met,
        clo=payload.clo,
    )

    return analyze_environment(data)
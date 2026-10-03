from dataclasses import dataclass
from pythermalcomfort.models import pet_steady


@dataclass
class EnvironmentInput:
    temperature: float = 25.0
    relative_humidity: float = 50.0
    air_speed: float = 0.1
    mean_radiant_temperature: float = 25.0
    met: float = 1.2
    clo: float = 0.5


def calculate_pet(data: EnvironmentInput) -> float:
    result = pet_steady(
        tdb=data.temperature,
        tr=data.mean_radiant_temperature,
        v=data.air_speed,
        rh=data.relative_humidity,
        met=data.met,
        clo=data.clo,
    )

    return float(result.pet)


def pet_comfort_label(pet: float) -> str:
    if pet < 4:
        return "Very Cold"
    if pet < 8:
        return "Cold"
    if pet < 13:
        return "Cool"
    if pet < 18:
        return "Slightly Cool"
    if pet < 23:
        return "Comfortable"
    if pet < 29:
        return "Slightly Warm"
    if pet < 35:
        return "Warm"
    if pet < 41:
        return "Hot"

    return "Very Hot"


def analyze_environment(data: EnvironmentInput) -> dict:
    pet = calculate_pet(data)

    return {
        "temperature": data.temperature,
        "relative_humidity": data.relative_humidity,
        "air_speed": data.air_speed,
        "mean_radiant_temperature":
            data.mean_radiant_temperature,
        "met": data.met,
        "clo": data.clo,
        "pet": round(pet, 2),
        "comfort": pet_comfort_label(pet),
    }
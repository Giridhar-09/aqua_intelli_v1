"""
AquaIntelli - API Routes: Smart Farm
"""
from fastapi import APIRouter
from ...services.farm_service import get_fields, get_sensors, get_schedule

router = APIRouter(prefix="/farm", tags=["Smart Farm"])


@router.get("/fields", summary="Get all monitored fields",
            description="Returns all farm fields with current sensor data and irrigation status.")
async def list_fields():
    return {"fields": get_fields()}


@router.get("/sensors", summary="Sensor readings",
            description="Get all IoT sensor readings across fields.")
async def sensor_readings():
    return {"sensors": get_sensors()}


@router.get("/schedule", summary="Irrigation schedule",
            description="Get AI-optimized 7-day irrigation schedule.")
async def irrigation_schedule():
    return {"schedule": get_schedule()}

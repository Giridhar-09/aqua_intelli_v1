"""
AquaIntelli - API Routes: Irrigation Optimization
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from ...services.irrigation_service import calculate_etc, optimize_schedule

router = APIRouter(prefix="/irrigation", tags=["Irrigation"])


class IrrigationRequest(BaseModel):
    crop_type: str = Field("wheat", examples=["rice","wheat","cotton","sugarcane","maize","soybean"])
    growth_stage: str = Field("mid", examples=["ini","mid","late"])
    temp_c: float = Field(28.0, description="Temperature °C")
    humidity_pct: float = Field(60.0, description="Relative humidity %")
    wind_ms: float = Field(2.0, description="Wind speed m/s")
    radiation_mj: float = Field(20.0, description="Solar radiation MJ/m²/day")
    soil_moisture_pct: float = Field(40.0, description="Soil moisture %")
    groundwater_availability: str = Field("MODERATE", examples=["SAFE","MODERATE","CRITICAL"])
    forecast_rainfall_mm: float = Field(0.0, description="Forecast rainfall (mm)")


@router.post("/calculate", summary="Calculate irrigation requirement",
             description="FAO-56 Penman-Monteith crop water requirement + schedule optimization.")
async def calculate_irrigation(req: IrrigationRequest):
    etc = calculate_etc(req.crop_type, req.growth_stage, req.temp_c,
                        req.humidity_pct, req.wind_ms, req.radiation_mj)
    schedule = optimize_schedule(req.crop_type, req.soil_moisture_pct,
                                 req.groundwater_availability, req.forecast_rainfall_mm)
    return {**etc, **schedule}

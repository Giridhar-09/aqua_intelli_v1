"""
AquaIntelli - API Routes: Borewell Prediction
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from ...services.borewell_service import borewell_predictor

router = APIRouter(prefix="/borewell", tags=["Borewell"])


class BorewellRequest(BaseModel):
    lat: float = Field(16.5, description="Latitude")
    lon: float = Field(80.6, description="Longitude")
    soil_type: str = Field("red", description="Soil type", examples=["red","black","alluvial","laterite","sandy"])
    depth_m: float = Field(200, description="Requested depth in meters")
    aquifer_type: str = Field("fractured_granite", description="Aquifer type",
                              examples=["fractured_granite","alluvial_gravel","basalt_vesicular","sandstone","shale"])
    district_historical_rate: float = Field(0.6, description="Historical success rate (0-1)")
    grace_anomaly_m: float = Field(-2.0, description="GRACE anomaly in meters")
    soil_moisture_pct: float = Field(45, description="Soil moisture %")
    rainfall_mm: float = Field(600, description="Annual rainfall mm")
    distance_to_river_km: float = Field(5.0, description="Distance to nearest river (km)")
    elevation_m: float = Field(200, description="Elevation in meters")
    slope_degrees: float = Field(2.0, description="Terrain slope in degrees")


@router.post("/predict", summary="Predict borewell success",
             description="AI-powered borewell drilling success prediction using satellite data fusion.")
async def predict_borewell(req: BorewellRequest):
    return borewell_predictor.predict(
        lat=req.lat, lon=req.lon, soil_type=req.soil_type,
        depth_m=req.depth_m, aquifer_type=req.aquifer_type,
        district_historical_rate=req.district_historical_rate,
        grace_anomaly_m=req.grace_anomaly_m,
        soil_moisture_pct=req.soil_moisture_pct,
        rainfall_mm=req.rainfall_mm,
        distance_to_river_km=req.distance_to_river_km,
        elevation_m=req.elevation_m,
        slope_degrees=req.slope_degrees,
    )

"""
AquaIntelli - API Routes: Satellite Data
"""
from fastapi import APIRouter, Query
from ...services.satellite_service import grace_service, sentinel_service, rainfall_service

router = APIRouter(prefix="/satellite", tags=["Satellite"])


@router.get("/grace", summary="GRACE-FO groundwater anomaly",
            description="Get GRACE-FO terrestrial water storage anomaly for a location.")
async def grace_anomaly(
    lat: float = Query(16.5, description="Latitude"),
    lon: float = Query(80.6, description="Longitude"),
):
    return grace_service.mock_anomaly(lat, lon)


@router.get("/soil-moisture", summary="Sentinel-1 soil moisture",
            description="Get SAR-derived soil moisture estimate.")
async def soil_moisture(
    lat: float = Query(16.5), lon: float = Query(80.6),
):
    return sentinel_service.get_soil_moisture(lat, lon)


@router.get("/ndvi", summary="Sentinel-2 NDVI",
            description="Get vegetation index for crop health assessment.")
async def ndvi(
    lat: float = Query(16.5), lon: float = Query(80.6),
):
    return sentinel_service.get_ndvi(lat, lon)


@router.get("/rainfall", summary="Rainfall data",
            description="Get cumulative rainfall from NASA POWER API.")
async def rainfall(
    lat: float = Query(16.5), lon: float = Query(80.6),
    days_back: int = Query(30, description="Days of history"),
):
    return await rainfall_service.get_rainfall(lat, lon, days_back)

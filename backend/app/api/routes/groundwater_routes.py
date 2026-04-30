"""
AquaIntelli - API Routes: Groundwater
"""
from fastapi import APIRouter, Query
from ...services.groundwater_service import get_groundwater_status

router = APIRouter(prefix="/groundwater", tags=["Groundwater"])


@router.get("/status", summary="Get groundwater status for a location",
            description="Returns GRACE-FO anomaly, soil moisture, rainfall, AI forecast, and alert severity.")
async def groundwater_status(
    lat: float = Query(16.5, description="Latitude"),
    lon: float = Query(80.6, description="Longitude"),
    district: str = Query("Krishna", description="District name"),
    state: str = Query("Andhra Pradesh", description="State name"),
):
    return await get_groundwater_status(lat, lon, district, state)


@router.get("/regional", summary="Regional groundwater overview",
            description="Returns groundwater status for multiple locations in a state.")
async def regional_overview(
    state: str = Query("Andhra Pradesh", description="State name"),
):
    regions = {
        "Andhra Pradesh": [
            {"district": "Krishna", "lat": 16.5, "lon": 80.6},
            {"district": "Guntur", "lat": 16.3, "lon": 80.5},
            {"district": "Anantapur", "lat": 14.7, "lon": 77.6},
        ],
        "Rajasthan": [
            {"district": "Jodhpur", "lat": 26.3, "lon": 73.0},
            {"district": "Jaipur", "lat": 26.9, "lon": 75.8},
            {"district": "Barmer", "lat": 25.7, "lon": 71.4},
        ],
        "Punjab": [
            {"district": "Ludhiana", "lat": 30.9, "lon": 75.9},
            {"district": "Amritsar", "lat": 31.6, "lon": 74.9},
            {"district": "Patiala", "lat": 30.3, "lon": 76.4},
        ],
    }
    locations = regions.get(state, regions["Andhra Pradesh"])
    results = []
    for loc in locations:
        status = await get_groundwater_status(loc["lat"], loc["lon"], loc["district"], state)
        results.append(status)
    return {"state": state, "districts": results, "count": len(results)}

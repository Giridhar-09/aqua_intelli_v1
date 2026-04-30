"""
AquaIntelli - API Routes: Reservoir & Water Bodies
"""
from fastapi import APIRouter, Query
from ...services.reservoir_service import reservoir_service

router = APIRouter(prefix="/reservoirs", tags=["Water Resources"])

@router.get("/nearby")
async def get_nearby(
    lat: float = Query(16.5),
    lon: float = Query(80.6),
    radius: float = Query(200.0)
):
    """Get reservoirs near a specific coordinate."""
    return reservoir_service.get_nearby_reservoirs(lat, lon, radius)

@router.get("/basins")
async def get_basins():
    """Get list of major river basins."""
    return reservoir_service.get_all_basins()

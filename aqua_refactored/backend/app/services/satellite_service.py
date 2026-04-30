"""
AquaIntelli - Satellite Data Service
Handles GRACE-FO, Sentinel-1/2, NASA POWER, Rainfall data.
"""
import numpy as np
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class GRACEService:
    """GRACE-FO groundwater anomaly retrieval."""

    def mock_anomaly(self, lat: float, lon: float) -> dict:
        """Synthetic GRACE data (Rajasthan/Punjab severe; Kerala/NE mild)."""
        base = -2.0 if 20 < lat < 32 else -0.5
        if 25 < lat < 30 and 68 < lon < 78:
            base = -8.0  # Rajasthan severe
        noise = np.random.normal(0, 0.3)
        return {
            "lat": lat, "lon": lon,
            "anomaly_m": round(base + noise, 3),
            "uncertainty_m": round(abs(noise * 0.3), 3),
            "date": datetime.utcnow().isoformat(),
            "source": "GRACE-FO (synthetic)"
        }


class SentinelService:
    """Sentinel-1 soil moisture + Sentinel-2 NDVI."""

    def get_soil_moisture(self, lat: float, lon: float) -> dict:
        sm = max(5, min(95, 45 + np.random.normal(0, 15)))
        return {
            "lat": lat, "lon": lon,
            "soil_moisture_pct": round(sm, 1),
            "vv_db": round(-15 + np.random.normal(0, 3), 2),
            "source": "Sentinel-1 (synthetic)"
        }

    def get_ndvi(self, lat: float, lon: float) -> dict:
        ndvi = max(0.1, min(0.9, 0.45 + np.random.normal(0, 0.12)))
        return {
            "lat": lat, "lon": lon,
            "ndvi": round(ndvi, 4),
            "crop_health": "GOOD" if ndvi > 0.5 else "MODERATE" if ndvi > 0.3 else "POOR",
            "source": "Sentinel-2 (synthetic)"
        }


class RainfallService:
    """Rainfall data from NASA POWER."""

    async def get_rainfall(self, lat: float, lon: float, days_back: int = 30) -> dict:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            "parameters": "PRECTOTCORR,T2M,RH2M,ALLSKY_SFC_SW_DWN",
            "community": "AG",
            "longitude": lon, "latitude": lat,
            "start": start.strftime("%Y%m%d"),
            "end": end.strftime("%Y%m%d"),
            "format": "JSON"
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(url, params=params)
                if r.status_code == 200:
                    data = r.json()["properties"]["parameter"]
                    prec = [p for p in data["PRECTOTCORR"].values() if p > 0]
                    return {
                        "lat": lat, "lon": lon,
                        "total_rainfall_mm": round(sum(prec), 2),
                        "avg_temp_c": round(np.mean(list(data["T2M"].values())), 2),
                        "avg_rh_pct": round(np.mean(list(data["RH2M"].values())), 2),
                        "avg_radiation_mj": round(np.mean(list(data["ALLSKY_SFC_SW_DWN"].values())), 3),
                        "days": days_back,
                        "source": "NASA POWER"
                    }
        except Exception as e:
            logger.warning(f"NASA POWER fetch failed: {e}")
        # Fallback mock
        return {
            "lat": lat, "lon": lon,
            "total_rainfall_mm": round(np.random.uniform(10, 120), 2),
            "avg_temp_c": round(np.random.uniform(22, 38), 2),
            "avg_rh_pct": round(np.random.uniform(40, 80), 2),
            "avg_radiation_mj": round(np.random.uniform(15, 25), 3),
            "days": days_back,
            "source": "mock"
        }


# Singleton instances
grace_service = GRACEService()
sentinel_service = SentinelService()
rainfall_service = RainfallService()

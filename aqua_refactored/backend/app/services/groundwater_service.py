"""
AquaIntelli - Groundwater Forecasting Service
Fuses satellite data + AI forecast model.
"""
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
from .satellite_service import grace_service, sentinel_service, rainfall_service

ROOT = Path(__file__).parent.parent.parent
CGWB_PATH = ROOT / "data" / "cgwb" / "cgwb_district_gw_2022.json"

def load_cgwb_data():
    try:
        if CGWB_PATH.exists():
            with open(CGWB_PATH, "r") as f:
                return json.load(f).get("districts", [])
    except Exception:
        pass
    return []

CGWB_DATA = load_cgwb_data()


class GroundwaterForecaster:
    """Synthetic groundwater forecast (replace with trained TFT model)."""

    def predict(self, features: np.ndarray) -> dict:
        base = features[0] * 10  # anomaly → depth
        forecast = base + np.linspace(0, features[0] * 2, 90) + np.random.normal(0, 0.5, 90)
        current = float(forecast[0])
        in_30d = float(forecast[29])
        in_90d = float(forecast[-1])
        depletion_rate = (in_90d - current) / 90
        return {
            "current_depth_m": round(abs(current) + 5, 2),
            "forecast_30d_m": round(abs(in_30d) + 7, 2),
            "forecast_90d_m": round(abs(in_90d) + 9, 2),
            "depletion_rate_m_per_day": round(depletion_rate, 4),
            "trend": "DEPLETING" if depletion_rate < -0.01 else "RECOVERING" if depletion_rate > 0.01 else "STABLE",
            "forecast_array": [round(float(f), 2) for f in forecast[:30]],
        }


forecaster = GroundwaterForecaster()


async def get_groundwater_status(lat: float, lon: float, district: str, state: str) -> dict:
    """Full groundwater assessment for a location."""
    anomaly = grace_service.mock_anomaly(lat, lon)
    sm = sentinel_service.get_soil_moisture(lat, lon)
    rainfall = await rainfall_service.get_rainfall(lat, lon, days_back=30)

    features = np.array([
        anomaly.get("anomaly_m", 0),
        sm.get("soil_moisture_pct", 50) / 100,
        rainfall.get("total_rainfall_mm", 50) / 500,
        rainfall.get("avg_temp_c", 28) / 50,
        rainfall.get("avg_rh_pct", 60) / 100,
        1.0,
    ], dtype=np.float32)

    forecast = forecaster.predict(features)

    # 4. Integrate Real-World CGWB Data
    cgwb_info = next((d for d in CGWB_DATA if d["district"].lower() == district.lower()), None)

    severity = "normal"
    description = "Levels within normal range."
    
    if cgwb_info:
        status = cgwb_info.get("status", "unknown").upper()
        description = f"CGWB Status: {status}. Annual Recharge: {cgwb_info.get('annual_recharge_bcm')} BCM."
        if status == "OVER-EXPLOITED":
            severity = "critical"
        elif status == "SEMI-CRITICAL":
            severity = "warning"

    # Overlay with satellite evidence
    if anomaly["anomaly_m"] < -5.0:
        severity = "critical"
        description += f" [SATELLITE ALERT] GRACE anomaly {anomaly['anomaly_m']:.2f}m detected."
    elif anomaly["anomaly_m"] < -2.0:
        severity = "warning"
        description += f" [SATELLITE WARNING] GRACE anomaly {anomaly['anomaly_m']:.2f}m detected."

    return {
        "location": {"lat": lat, "lon": lon, "district": district, "state": state},
        "satellite_data": {
            "grace_anomaly_m": anomaly["anomaly_m"],
            "soil_moisture_pct": sm["soil_moisture_pct"],
            "rainfall_30d_mm": rainfall["total_rainfall_mm"],
            "avg_temp_c": rainfall.get("avg_temp_c", 0),
        },
        "cgwb_historical": cgwb_info,
        "ai_forecast": forecast,
        "alert": {"severity": severity, "description": description},
        "timestamp": datetime.utcnow().isoformat()
    }

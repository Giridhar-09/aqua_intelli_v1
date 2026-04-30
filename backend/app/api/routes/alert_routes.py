"""
AquaIntelli - API Routes: Alerts & Crisis Events
"""
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Query

router = APIRouter(prefix="/alerts", tags=["Alerts"])

CRISIS_EVENTS = [
    {"id": 1, "type": "DROUGHT", "severity": "CRITICAL", "district": "Jodhpur", "state": "Rajasthan",
     "lat": 26.3, "lon": 73.0, "description": "Severe groundwater depletion. GRACE anomaly: -18.2M. " 
     "Water table dropped 12m in 5 years. 340% over-extraction rate.", "source": "GRACE-FO + CGWB"},
    {"id": 2, "type": "CONTAMINATION", "severity": "HIGH", "district": "Ludhiana", "state": "Punjab",
     "lat": 30.9, "lon": 75.9, "description": "Fluoride contamination detected at 2.8ppm " 
     "(WHO limit: 1.5ppm). 12 villages affected.", "source": "CGWB Water Quality"},
    {"id": 3, "type": "DEPLETION", "severity": "WARNING", "district": "Chennai", "state": "Tamil Nadu",
     "lat": 13.08, "lon": 80.27, "description": "Urban groundwater stress. Extraction exceeds " 
     "recharge by 180%. Reservoir levels at 34%.", "source": "GRACE-FO + CWC"},
    {"id": 4, "type": "FLOOD_RISK", "severity": "MEDIUM", "district": "Patna", "state": "Bihar",
     "lat": 25.6, "lon": 85.1, "description": "Saturated soil + high Ganga levels. " 
     "Sentinel-1 SAR detects standing water in 48 villages.", "source": "Sentinel-1"},
    {"id": 5, "type": "DROUGHT", "severity": "CRITICAL", "district": "Anantapur", "state": "Andhra Pradesh",
     "lat": 14.7, "lon": 77.6, "description": "Chronic drought zone. Only 22% borewell success. " 
     "67% of wells dried up in last 3 years.", "source": "CGWB + Sentinel-2"},
    {"id": 6, "type": "RECHARGE_SUCCESS", "severity": "LOW", "district": "Ahmedabad", "state": "Gujarat",
     "lat": 23.0, "lon": 72.5, "description": "GRACE shows +4.2M recharge. " 
     "Narmada canal project successfully recharging aquifers.", "source": "GRACE-FO"},
]


@router.get("/active", summary="Get active crisis alerts",
            description="Returns all active water crisis alerts across India.")
async def active_alerts():
    for alert in CRISIS_EVENTS:
        alert["created_at"] = (datetime.utcnow() - timedelta(hours=random.randint(1, 72))).isoformat()
        alert["is_active"] = True
    return {"alerts": CRISIS_EVENTS, "total": len(CRISIS_EVENTS)}


@router.get("/by-state", summary="Alerts by state")
async def alerts_by_state(state: str = Query("Rajasthan")):
    filtered = [a for a in CRISIS_EVENTS if a["state"].lower() == state.lower()]
    return {"state": state, "alerts": filtered, "count": len(filtered)}


@router.get("/summary", summary="Crisis summary statistics")
async def alert_summary():
    return {
        "total_alerts": len(CRISIS_EVENTS),
        "critical": len([a for a in CRISIS_EVENTS if a["severity"] == "CRITICAL"]),
        "high": len([a for a in CRISIS_EVENTS if a["severity"] == "HIGH"]),
        "warning": len([a for a in CRISIS_EVENTS if a["severity"] == "WARNING"]),
        "states_affected": list(set(a["state"] for a in CRISIS_EVENTS)),
        "most_common_type": "DROUGHT",
    }

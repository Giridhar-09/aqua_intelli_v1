"""
AquaIntelli - Farm Service
Smart farm monitoring, sensor simulation, and field management.
"""
import random
import numpy as np
from datetime import datetime, timedelta


DEMO_FIELDS = [
    {"id": 1, "name": "Field Alpha", "crop": "rice", "area_ha": 2.5, "lat": 16.5, "lon": 80.6},
    {"id": 2, "name": "Field Bravo", "crop": "wheat", "area_ha": 1.8, "lat": 16.52, "lon": 80.62},
    {"id": 3, "name": "Field Charlie", "crop": "cotton", "area_ha": 3.2, "lat": 16.48, "lon": 80.58},
    {"id": 4, "name": "Field Delta", "crop": "sugarcane", "area_ha": 4.0, "lat": 16.54, "lon": 80.64},
]


def get_fields() -> list[dict]:
    return [{
        **f,
        "soil_moisture_pct": round(random.uniform(25, 65), 1),
        "irrigation_status": random.choice(["ACTIVE", "SCHEDULED", "IDLE"]),
        "etc_today_mm": round(random.uniform(3, 8), 1),
        "next_irrigation": (datetime.utcnow() + timedelta(hours=random.randint(2, 48))).isoformat(),
        "health": random.choice(["GOOD", "MODERATE", "NEEDS_ATTENTION"]),
    } for f in DEMO_FIELDS]


def get_sensors() -> list[dict]:
    sensors = []
    for f in DEMO_FIELDS:
        sensors.append({
            "field_id": f["id"], "field_name": f["name"], "type": "soil_moisture",
            "value": round(random.uniform(25, 65), 1), "unit": "%",
            "status": "ONLINE", "battery_pct": random.randint(60, 100),
            "timestamp": datetime.utcnow().isoformat()
        })
        sensors.append({
            "field_id": f["id"], "field_name": f["name"], "type": "temperature",
            "value": round(random.uniform(24, 38), 1), "unit": "°C",
            "status": "ONLINE", "battery_pct": random.randint(60, 100),
            "timestamp": datetime.utcnow().isoformat()
        })
    return sensors


def get_schedule() -> list[dict]:
    schedule = []
    for day_offset in range(7):
        dt = datetime.utcnow() + timedelta(days=day_offset)
        for f in DEMO_FIELDS:
            if random.random() > 0.4:
                schedule.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "field_id": f["id"], "field_name": f["name"],
                    "irrigation_mm": round(random.uniform(5, 20), 1),
                    "time_slot": random.choice(["05:00-07:00", "17:00-19:00"]),
                    "method": random.choice(["drip", "sprinkler", "flood"]),
                    "ai_optimized": True,
                })
    return schedule

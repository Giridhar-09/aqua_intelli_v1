"""
AquaIntelli - Reservoir & Water Body Service
Manages real-world data from CWC, India-WRIS and GADM.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional

ROOT = Path(__file__).parent.parent.parent
RESERVOIR_PATH = ROOT / "data" / "reservoirs" / "india_reservoirs.json"
WATER_BODIES_PATH = ROOT / "data" / "reservoirs" / "india_water_bodies.json"

class ReservoirService:
    def __init__(self):
        self.reservoirs = []
        self.water_bodies = {"rivers": [], "lakes": []}
        self._load_data()

    def _load_data(self):
        try:
            # 1. Try to load major dams from geojson
            GEOJSON_PATH = ROOT / "data" / "reservoirs" / "india_dams.geojson"
            if GEOJSON_PATH.exists():
                with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for feat in data.get("features", []):
                        props = feat.get("properties", {})
                        geom = feat.get("geometry", {})
                        if geom.get("type") == "Point":
                            coords = geom.get("coordinates", [0,0])
                            self.reservoirs.append({
                                "name": props.get("name") or props.get("NAM") or "Unknown Reservoir",
                                "state": props.get("state") or props.get("STN") or "India",
                                "lat": coords[1],
                                "lon": coords[0],
                                "river": props.get("river") or "Unknown River",
                                "capacity_mcm": props.get("capacity") or props.get("CAP") or 0
                            })

            # 2. Fallback to existing json if reservoirs still empty
            if not self.reservoirs and RESERVOIR_PATH.exists():
                with open(RESERVOIR_PATH, "r") as f:
                    self.reservoirs = json.load(f).get("reservoirs", [])
            
            # 3. Load rivers/lakes
            if WATER_BODIES_PATH.exists():
                with open(WATER_BODIES_PATH, "r") as f:
                    data = json.load(f)
                    self.water_bodies["rivers"] = data.get("rivers", [])
                    self.water_bodies["lakes"] = data.get("lakes", [])
        except Exception as e:
            print(f"Error loading reservoir data: {e}")

    def get_nearby_reservoirs(self, lat: float, lon: float, radius_km: float = 100) -> List[Dict]:
        """Find reservoirs within a radius using simple Haversine approximation."""
        from math import radians, cos, sin, asin, sqrt
        
        nearby = []
        for r in self.reservoirs:
            # Haversine
            dlon = radians(r["lon"] - lon)
            dlat = radians(r["lat"] - lat)
            a = sin(dlat/2)**2 + cos(radians(lat)) * cos(radians(r["lat"])) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c
            
            if km <= radius_km:
                r_copy = r.copy()
                r_copy["distance_km"] = round(km, 1)
                nearby.append(r_copy)
        
        return sorted(nearby, key=lambda x: x["distance_km"])

    def get_all_basins(self) -> List[Dict]:
        """Get major basins (rivers)."""
        return self.water_bodies["rivers"]

reservoir_service = ReservoirService()

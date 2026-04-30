"""
AquaIntelli - API Routes: Location Search
"""
from fastapi import APIRouter, Query
from typing import List, Dict
import json
import os
from pathlib import Path

router = APIRouter(prefix="/search", tags=["Navigation"])

# Load GADM level 2 (districts) for search
ROOT = Path(__file__).parent.parent.parent.parent
GADM_PATH = ROOT / "data" / "gadm" / "gadm41_IND_2.json"

@router.get("/locations")
async def search_locations(q: str = Query("", min_length=2)):
    """Fuzzy search for Indian districts."""
    if not q or len(q) < 2:
        return []
    
    q = q.lower()
    matches = []
    
    try:
        if GADM_PATH.exists():
            with open(GADM_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                features = data.get("features", [])
                for feat in features:
                    props = feat.get("properties", {})
                    name = props.get("NAME_2", "")  # District
                    state = props.get("NAME_1", "") # State
                    
                    if q in name.lower() or q in state.lower():
                        # Simple centroid or representative point
                        # GADM Level 2 has coordinates in geometry
                        # For simplicity, we'll return the name and let the frontend geocode or use pre-stored centroids
                        matches.append({
                            "name": f"{name}, {state}, India",
                            "district": name,
                            "state": state,
                            "type": "district"
                        })
                        if len(matches) > 10: break
    except Exception:
        pass
    
    # Fallback/Hardcoded major cities if JSON fails or too slow
    hardcoded = [
        {"name": "Hyderabad, Telangana, India", "lat": 17.385, "lon": 78.487},
        {"name": "Vijayawada, Andhra Pradesh, India", "lat": 16.506, "lon": 80.648},
        {"name": "Chennai, Tamil Nadu, India", "lat": 13.0827, "lon": 80.2707},
        {"name": "Bengaluru, Karnataka, India", "lat": 12.9716, "lon": 77.5946},
        {"name": "Delhi, India", "lat": 28.6139, "lon": 77.2090},
        {"name": "Mumbai, Maharashtra, India", "lat": 19.0760, "lon": 72.8777},
    ]
    
    for h in hardcoded:
        if q in h["name"].lower():
            matches.append(h)
            
    return matches[:15]

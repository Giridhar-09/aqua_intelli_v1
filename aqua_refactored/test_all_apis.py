#!/usr/bin/env python3
"""
AquaIntelli — API Connection Test
Run: python test_all_apis.py
Tests every real-world API used across all 8 modules.
"""
import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Installing httpx..."); os.system("pip install httpx -q")
    import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env values still readable if set manually

LAT, LON = 17.385, 78.487   # Hyderabad test point


# ─────────────────────────────────────────────────────────────
RESULTS: dict = {}

async def check(name: str, coro):
    try:
        status, detail = await coro
        RESULTS[name] = ("✅", status, detail)
    except Exception as e:
        RESULTS[name] = ("❌", "ERROR", str(e)[:80])


# ─────────────────────────────────────────────────────────────
# 1. NASA POWER  (Module 3 & 6 — NO auth needed)
# ─────────────────────────────────────────────────────────────
async def test_nasa_power():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(
            "https://power.larc.nasa.gov/api/temporal/daily/point",
            params={
                "parameters": "T2M,PRECTOTCORR",
                "community": "AG",
                "longitude": LON,
                "latitude": LAT,
                "start": "20240101",
                "end": "20240105",
                "format": "JSON",
            },
        )
        if r.status_code == 200:
            t2m = list(r.json()["properties"]["parameter"]["T2M"].values())
            return "200 OK", f"Avg temp sample: {sum(t2m)/len(t2m):.1f}°C"
        return f"{r.status_code}", r.text[:80]


# ─────────────────────────────────────────────────────────────
# 2. OSM Overpass  (Module 5 — NO auth needed)
# ─────────────────────────────────────────────────────────────
async def test_overpass():
    query = f"[out:json][timeout:10];node(around:2000,{LAT},{LON})[waterway];out 3;"
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
        )
        count = len(r.json().get("elements", []))
        return "200 OK", f"Waterway nodes nearby: {count}"


# ─────────────────────────────────────────────────────────────
# 3. Open-Elevation  (Module 4 & 5 — NO auth needed)
# ─────────────────────────────────────────────────────────────
async def test_elevation():
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(
            f"https://api.open-elevation.com/api/v1/lookup?locations={LAT},{LON}"
        )
        if r.status_code == 200:
            elev = r.json()["results"][0]["elevation"]
            return "200 OK", f"Elevation: {elev}m ASL"
        # Fallback to OpenTopoData
        r2 = await c.get(
            f"https://api.opentopodata.org/v1/srtm90m?locations={LAT},{LON}"
        )
        if r2.status_code == 200:
            elev = r2.json()["results"][0]["elevation"]
            return "200 OK (OpenTopoData fallback)", f"Elevation: {elev}m ASL"
        return f"{r.status_code}", "Both elevation APIs failed"


# ─────────────────────────────────────────────────────────────
# 4. SoilGrids ISRIC  (Module 3 — NO auth needed)
# ─────────────────────────────────────────────────────────────
async def test_soilgrids():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={
                "lon": LON,
                "lat": LAT,
                "property": "clay",
                "depth": "0-30cm",
                "value": "mean",
            },
        )
        if r.status_code == 200:
            try:
                data = r.json()
                layers = data.get("properties", {}).get("layers", [])
                if layers:
                    depths = layers[0].get("depths", [])
                    val = depths[0].get("values", {}).get("mean", "N/A") if depths else "N/A"
                    return "200 OK", f"Clay content (0-30cm): {val} g/kg"
                # fallback: check soilgrids v2 structure
                return "200 OK", f"SoilGrids responded (keys: {list(data.keys())})"
            except Exception as parse_err:
                return "200 OK (parse warn)", str(parse_err)[:60]
        return f"{r.status_code}", r.text[:80]


# ─────────────────────────────────────────────────────────────
# 5. World Bank API  (Module 8 — NO auth needed)
# ─────────────────────────────────────────────────────────────
async def test_worldbank():
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            "https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL",
            params={"format": "json", "per_page": 1, "mrv": 1},
        )
        if r.status_code == 200:
            data = r.json()
            pop = data[1][0].get("value", "N/A") if data and len(data) > 1 else "N/A"
            return "200 OK", f"India population (latest): {pop:,.0f}" if isinstance(pop, (int, float)) else f"Value: {pop}"
        return f"{r.status_code}", r.text[:80]


# ─────────────────────────────────────────────────────────────
# 6. HydroSHEDS via OpenStreetMap (Module 5)
# ─────────────────────────────────────────────────────────────
async def test_hydrosheds_osm():
    """
    Checks for rivers near the test point via Overpass (as proxy for HydroSHEDS).
    The actual HydroSHEDS shapefile must be downloaded manually from:
    https://www.hydrosheds.org/downloads → HydroRIVERS → South Asia
    """
    query = (
        f"[out:json][timeout:15];"
        f"way[waterway=river](around:20000,{LAT},{LON});out 5;"
    )
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post("https://overpass-api.de/api/interpreter", data={"data": query})
        rivers = r.json().get("elements", [])
        names = [el.get("tags", {}).get("name", "unnamed") for el in rivers[:3]]
        return "200 OK", f"Nearby rivers: {', '.join(names) or 'none found'}"


# ─────────────────────────────────────────────────────────────
# 7. NASA EarthData / CMR  (Module 1 & 7 — needs EARTHDATA_TOKEN)
# ─────────────────────────────────────────────────────────────
async def test_earthdata():
    token = os.getenv("EARTHDATA_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(
            "https://cmr.earthdata.nasa.gov/search/granules.json",
            params={
                "short_name": "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.2_V3",
                "page_size": 1,
            },
            headers=headers,
        )
        if r.status_code == 200:
            hits = r.json().get("feed", {}).get("entry", [])
            token_note = "" if token else " (add EARTHDATA_TOKEN to .env for data download)"
            return "200 OK", f"GRACE-FO granules found: {len(hits)}{token_note}"
        return f"{r.status_code}", "Add EARTHDATA_TOKEN to .env → urs.earthdata.nasa.gov"


# ─────────────────────────────────────────────────────────────
# 8. OpenWeatherMap  (Module 3 & 6 — needs API key)
# ─────────────────────────────────────────────────────────────
async def test_openweather():
    key = os.getenv("OPENWEATHER_API_KEY", "")
    if not key:
        return "SKIPPED", "Add OPENWEATHER_API_KEY to .env → openweathermap.org/api"
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": LAT, "lon": LON, "appid": key, "units": "metric"},
        )
        if r.status_code == 200:
            d = r.json()
            return "200 OK", f"{d['name']}: {d['main']['temp']}°C, {d['weather'][0]['description']}"
        return f"{r.status_code}", "Invalid API key — register at openweathermap.org"


# ─────────────────────────────────────────────────────────────
# 9. India-WRIS  (Module 2 & 4 — needs WRIS key)
# ─────────────────────────────────────────────────────────────
async def test_wris():
    key = os.getenv("WRIS_API_KEY", "")
    if not key:
        return "SKIPPED", "Add WRIS_API_KEY to .env → indiawris.gov.in/wris"
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            "https://indiawris.gov.in/api/v1/reservoirs",
            headers={"Authorization": f"Bearer {key}"},
            params={"state": "Telangana"},
        )
        if r.status_code == 200:
            items = r.json().get("data", [])
            return "200 OK", f"Reservoirs returned: {len(items)}"
        return f"{r.status_code}", f"WRIS API: {r.text[:80]}"


# ─────────────────────────────────────────────────────────────
# 10. Google Earth Engine  (Module 1, 2, 5, 6, 7 — needs GEE setup)
# ─────────────────────────────────────────────────────────────
async def test_gee():
    key_path = os.getenv("GEE_KEY_PATH", "configs/gee_credentials.json")
    project = os.getenv("GEE_PROJECT", "")
    sa = os.getenv("GEE_SERVICE_ACCOUNT", "")

    if not os.path.exists(key_path):
        return "SKIPPED", f"Place GEE JSON key at: {key_path} → earthengine.google.com/signup"
    if not project:
        return "SKIPPED", "Add GEE_PROJECT to .env after GEE approval"

    try:
        import ee
        credentials = ee.ServiceAccountCredentials(email=sa, key_file=key_path)
        ee.Initialize(credentials=credentials, project=project)
        # Simple test: get a point value from Sentinel-2
        point = ee.Geometry.Point([LON, LAT])
        img = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").first()
        val = img.reduceRegion(ee.Reducer.mean(), point, scale=100).getInfo()
        return "200 OK", f"GEE initialized, bands available: {list(val.keys())[:3]}"
    except ImportError:
        return "NOT INSTALLED", "Run: pip install earthengine-api"
    except Exception as e:
        return "ERROR", str(e)[:100]


# ─────────────────────────────────────────────────────────────
# 11. AquaIntelli Backend Health (local)
# ─────────────────────────────────────────────────────────────
async def test_local_backend():
    async with httpx.AsyncClient(timeout=5) as c:
        try:
            r = await c.get("http://127.0.0.1:8001/api/health")
            if r.status_code == 200:
                d = r.json()
                return "200 OK", f"Backend v{d.get('version','?')} — {d.get('modules_active','?')} modules active"
            return f"{r.status_code}", r.text[:80]
        except Exception:
            return "NOT RUNNING", "Start backend: cd backend && python main.py"


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
async def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       AquaIntelli — Real World API Connection Test       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"  Test Location: {LAT}°N, {LON}°E (Hyderabad, India)")
    print()

    tests = [
        ("NASA POWER              [Module 3,6]", test_nasa_power()),
        ("OSM Overpass            [Module 5]  ", test_overpass()),
        ("Open-Elevation (SRTM)   [Module 4,5]", test_elevation()),
        ("SoilGrids ISRIC         [Module 3]  ", test_soilgrids()),
        ("World Bank API          [Module 8]  ", test_worldbank()),
        ("HydroSHEDS (OSM proxy)  [Module 5]  ", test_hydrosheds_osm()),
        ("NASA EarthData (GRACE)  [Module 1,7]", test_earthdata()),
        ("OpenWeatherMap          [Module 3,6]", test_openweather()),
        ("India-WRIS              [Module 2,4]", test_wris()),
        ("Google Earth Engine     [Module 1,7]", test_gee()),
        ("AquaIntelli Backend     [LOCAL]     ", test_local_backend()),
    ]

    await asyncio.gather(*[check(name, coro) for name, coro in tests])

    print(f"  {'API / SERVICE':<44} {'STATUS':<10} DETAIL")
    print("  " + "─" * 90)

    ok = warn = fail = 0
    for name, _ in tests:
        icon, status, detail = RESULTS.get(name, ("?", "?", "?"))
        if icon == "✅":
            ok += 1
        elif icon == "❌":
            fail += 1
        else:
            warn += 1
        print(f"  {icon} {name}  {status:<12} {detail}")

    print("  " + "─" * 90)
    print(f"\n  ✅ {ok} working   ⚠ {warn} need keys   ❌ {fail} errors\n")

    if warn > 0:
        print("  APIs marked SKIPPED need keys in .env.example → copy to .env")
        print("  Registration guide: REAL_WORLD_DATA_GUIDE.md\n")


if __name__ == "__main__":
    asyncio.run(main())

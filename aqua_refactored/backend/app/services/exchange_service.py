"""
AquaIntelli - Water Futures Exchange Service
AI-driven water pricing oracle + order book + trade engine.
"""
import random
import numpy as np
from datetime import datetime


ASSETS = {
    "WFX-AP-Q2": {"base_price": 847,  "region": "Andhra Pradesh", "quarter": "Q2-2026", "grace": -12.4},
    "WFX-RJ-Q2": {"base_price": 1204, "region": "Rajasthan",      "quarter": "Q2-2026", "grace": -18.2},
    "WFX-PB-Q2": {"base_price": 623,  "region": "Punjab",         "quarter": "Q2-2026", "grace": -8.7},
    "WFX-GJ-Q3": {"base_price": 389,  "region": "Gujarat",        "quarter": "Q3-2026", "grace": +4.2},
    "WFX-TN-Q2": {"base_price": 512,  "region": "Tamil Nadu",     "quarter": "Q2-2026", "grace": -5.1},
}

# Live prices (mutable state)
live_prices = {k: float(v["base_price"]) for k, v in ASSETS.items()}


def tick_prices():
    """Update prices with random walk."""
    for k in live_prices:
        live_prices[k] += random.gauss(0, live_prices[k] * 0.002)
        live_prices[k] = max(ASSETS[k]["base_price"] * 0.5, min(ASSETS[k]["base_price"] * 2, live_prices[k]))


def get_all_assets() -> list[dict]:
    tick_prices()
    return [{
        "id": k, "region": v["region"], "quarter": v["quarter"],
        "base_price": v["base_price"], "price": round(live_prices[k], 2),
        "change_pct": round((live_prices[k] - v["base_price"]) / v["base_price"] * 100, 2),
        "grace_anomaly": v["grace"],
    } for k, v in ASSETS.items()]


def get_order_book(asset_id: str) -> dict:
    mid = live_prices.get(asset_id, 847)
    spread = mid * 0.003
    bids = [{"price": round(mid - spread * (i + 1), 1), "qty": random.randint(200, 4000)} for i in range(8)]
    asks = [{"price": round(mid + spread * (i + 1), 1), "qty": random.randint(200, 4000)} for i in range(8)]
    return {"asset_id": asset_id, "mid": round(mid, 1), "bids": bids, "asks": asks, "ts": datetime.utcnow().isoformat()}


def get_price_oracle(asset_id: str) -> dict:
    forecasts = {
        "WFX-AP-Q2": {"d7": 831, "d30": 798, "d90": 1012, "factors": ["GRACE anomaly: -12.4M", "Rainfall deficit: 34%", "Monsoon forecast: avg", "Crop demand: HIGH"], "conf": 84},
        "WFX-RJ-Q2": {"d7": 1280, "d30": 1350, "d90": 1580, "factors": ["Severe GRACE: -18.2M", "Rainfall deficit: 61%", "No monsoon recharge", "Demand: CRITICAL"], "conf": 91},
        "WFX-PB-Q2": {"d7": 618, "d30": 602, "d90": 570, "factors": ["Overextraction: 340%", "Policy intervention risk", "Rabi season ending", "Export ban likely"], "conf": 77},
        "WFX-GJ-Q3": {"d7": 405, "d30": 440, "d90": 520, "factors": ["Recharge: +4.2M", "Good pre-monsoon", "Low demand season", "New policy: positive"], "conf": 82},
        "WFX-TN-Q2": {"d7": 518, "d30": 530, "d90": 548, "factors": ["Stable Cauvery flow", "Normal rainfall", "Steady crop demand", "Policy stable"], "conf": 72},
    }
    f = forecasts.get(asset_id, forecasts["WFX-AP-Q2"])
    base = live_prices.get(asset_id, 847)
    return {
        "asset_id": asset_id, "current_price": round(base, 1),
        "forecast_7d": f["d7"], "forecast_30d": f["d30"], "forecast_90d": f["d90"],
        "pct_7d": round((f["d7"] - base) / base * 100, 1),
        "pct_30d": round((f["d30"] - base) / base * 100, 1),
        "pct_90d": round((f["d90"] - base) / base * 100, 1),
        "driving_factors": f["factors"],
        "confidence_pct": f["conf"],
        "model": "TFT-Groundwater v2 + GRACE-FO fusion",
    }


def generate_trades(count: int = 10) -> list[dict]:
    users = ["FARMER_AP_001", "IRRIGATION_DEPT_AP", "SABARMATI_WATER", "PUNJAB_AGRI_BOARD",
             "CGWB_RESERVE", "MAHA_WATER_CO", "TELANGANA_RITU"]
    trades = []
    for _ in range(count):
        asset_id = random.choice(list(ASSETS.keys()))
        side = random.choice(["BUY", "SELL"])
        price = live_prices[asset_id] + random.gauss(0, live_prices[asset_id] * 0.005)
        qty = random.randint(100, 2000)
        now = datetime.utcnow()
        trades.append({
            "time": now.strftime("%H:%M:%S"), "side": side, "asset": asset_id,
            "qty": qty, "price": round(price, 1),
            "user": random.choice(users), "ts": now.isoformat()
        })
    return trades

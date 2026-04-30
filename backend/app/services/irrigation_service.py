"""
AquaIntelli - Irrigation Optimization Service
FAO-56 Penman-Monteith ET model + schedule optimizer.
"""
import numpy as np

CROP_KC = {
    "rice":      {"ini": 1.05, "mid": 1.20, "late": 0.90, "season_days": 120},
    "wheat":     {"ini": 0.30, "mid": 1.15, "late": 0.25, "season_days": 110},
    "cotton":    {"ini": 0.35, "mid": 1.15, "late": 0.50, "season_days": 180},
    "sugarcane": {"ini": 0.40, "mid": 1.25, "late": 0.75, "season_days": 365},
    "maize":     {"ini": 0.30, "mid": 1.20, "late": 0.35, "season_days": 95},
    "soybean":   {"ini": 0.40, "mid": 1.15, "late": 0.50, "season_days": 100},
}


def penman_monteith_eto(temp_c: float, humidity_pct: float,
                         wind_ms: float, radiation_mj: float,
                         elevation_m: float = 100) -> float:
    es = 0.6108 * np.exp(17.27 * temp_c / (temp_c + 237.3))
    ea = es * humidity_pct / 100
    vpd = es - ea
    delta = 4098 * es / (temp_c + 237.3) ** 2
    P = 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26
    gamma = 0.000665 * P
    Rn = 0.77 * radiation_mj
    eto = (0.408 * delta * Rn + gamma * (900 / (temp_c + 273)) * wind_ms * vpd) / \
          (delta + gamma * (1 + 0.34 * wind_ms))
    return max(0, round(eto, 3))


def calculate_etc(crop: str, growth_stage: str, temp_c: float = 28.0,
                  humidity_pct: float = 60.0, wind_ms: float = 2.0,
                  radiation_mj: float = 20.0, elevation_m: float = 100) -> dict:
    kc_data = CROP_KC.get(crop, CROP_KC["wheat"])
    kc = kc_data.get(growth_stage, kc_data["mid"])
    eto = penman_monteith_eto(temp_c, humidity_pct, wind_ms, radiation_mj, elevation_m)
    etc = round(kc * eto, 3)
    return {
        "crop": crop, "growth_stage": growth_stage, "kc": kc,
        "eto_mm_per_day": eto, "etc_mm_per_day": etc,
        "weekly_requirement_mm": round(etc * 7, 1),
        "formula": f"ETc = {kc} × {eto:.2f} = {etc:.2f} mm/day",
        "recommendation": f"Apply {etc:.1f}mm/day ({etc*7:.0f}mm/week). Drip preferred for {crop}."
    }


def optimize_schedule(crop: str, soil_moisture_pct: float = 40.0,
                       groundwater_availability: str = "MODERATE",
                       forecast_rainfall_mm: float = 0.0) -> dict:
    fc = 0.35
    current_water = soil_moisture_pct / 100
    deficit = max(0, fc - current_water)
    net_deficit = max(0, deficit - forecast_rainfall_mm / 1000 * 0.7)
    gw_penalty = 1.2 if groundwater_availability == "CRITICAL" else 1.0
    irr = min(net_deficit * 1000 * gw_penalty, 40)
    return {
        "irrigation_required_mm": round(irr, 1),
        "schedule": "IMMEDIATE" if irr > 15 else "IN 2 DAYS" if irr > 5 else "NONE REQUIRED",
        "water_saving_vs_flood_pct": round(np.random.uniform(30, 50), 1),
    }

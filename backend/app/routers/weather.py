# ═══════════════════════════════════════════════════════════════════════
#  DAY 2: Weather endpoint — proxies WeatherAPI.com for external signals
# ═══════════════════════════════════════════════════════════════════════

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from ..config import Settings, get_settings

router = APIRouter(tags=["Weather"])

WEATHERAPI_CURRENT = "https://api.weatherapi.com/v1/current.json"


# ── DAY 2 START: Current weather for a location ─────────────────────
@router.get("/weather")
def current_weather(
    q: str = Query(..., min_length=1, description="City name or lat,lon"),
    settings: Settings = Depends(get_settings),
):
    if not settings.weatherapi_key.strip():
        raise HTTPException(
            status_code=503,
            detail="WEATHERAPI_KEY missing. Add it to .env (see .env.example).",
        )

    params = {"key": settings.weatherapi_key, "q": q, "aqi": "no"}
    with httpx.Client(timeout=20.0) as client:
        r = client.get(WEATHERAPI_CURRENT, params=params)

    if r.status_code != 200:
        try:
            msg = r.json().get("error", {}).get("message", r.text)
        except Exception:
            msg = r.text
        raise HTTPException(status_code=r.status_code, detail=msg)

    data = r.json()
    loc = data.get("location") or {}
    cur = data.get("current") or {}
    cond = cur.get("condition") or {}

    return {
        "query": q,
        "location": {
            "name": loc.get("name"),
            "region": loc.get("region"),
            "country": loc.get("country"),
            "lat": loc.get("lat"),
            "lon": loc.get("lon"),
            "localtime": loc.get("localtime"),
        },
        "current": {
            "temp_c": cur.get("temp_c"),
            "temp_f": cur.get("temp_f"),
            "humidity": cur.get("humidity"),
            "precip_mm": cur.get("precip_mm"),
            "condition": cond.get("text"),
            "wind_kph": cur.get("wind_kph"),
        },
    }
# ── DAY 2 END ────────────────────────────────────────────────────────

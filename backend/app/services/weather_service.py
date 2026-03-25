# ═══════════════════════════════════════════════════════════════════════
#  DAY 2: WeatherAPI.com integration service
# ═══════════════════════════════════════════════════════════════════════

import httpx
from ..config import get_settings

WEATHERAPI_CURRENT = "https://api.weatherapi.com/v1/current.json"


# ── DAY 2 START: Fetch current weather for a location ────────────────

def fetch_current_weather(location: str) -> dict | None:
    settings = get_settings()
    if not settings.weatherapi_key.strip():
        return None

    params = {"key": settings.weatherapi_key, "q": location, "aqi": "no"}
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(WEATHERAPI_CURRENT, params=params)
        if r.status_code != 200:
            return {"error": r.json().get("error", {}).get("message", r.text)}
        data = r.json()
        loc = data.get("location", {})
        cur = data.get("current", {})
        cond = cur.get("condition", {})
        return {
            "name": loc.get("name"),
            "region": loc.get("region"),
            "country": loc.get("country"),
            "lat": loc.get("lat"),
            "lon": loc.get("lon"),
            "localtime": loc.get("localtime"),
            "temp_c": cur.get("temp_c"),
            "temp_f": cur.get("temp_f"),
            "humidity": cur.get("humidity"),
            "precip_mm": cur.get("precip_mm"),
            "condition": cond.get("text"),
            "wind_kph": cur.get("wind_kph"),
        }
    except Exception as exc:
        return {"error": str(exc)}

# ── DAY 2 END ────────────────────────────────────────────────────────

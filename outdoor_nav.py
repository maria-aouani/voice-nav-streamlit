import requests
import os

GOOGLE_API_KEY = "AIzaSyAwQ9270sBZZYMOb7lAujSrWL2oCHuIt6c"

def get_outdoor_route(origin_lat, origin_lon, dest_lat, dest_lon, mode="walking", alternatives=False, timeout=10):
    """
    origin_lat, origin_lon: floats (real GPS)
    dest_lat, dest_lon: floats
    mode: driving|walking|bicycling
    returns parsed JSON (or None on error)
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin_lat},{origin_lon}",
        "destination": f"{dest_lat},{dest_lon}",
        "mode": mode,
        "key": GOOGLE_API_KEY,
        "alternatives": "true" if alternatives else "false"
    }
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "OK":
            # you can log data.get("error_message") if needed
            return data
        return data
    except requests.RequestException as e:
        print("Directions API request failed:", e)
        return None
    except ValueError:
        print("Directions API returned non-JSON")
        return None

import requests

def search_poi(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "blind-nav-app"})
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        poi = data[0]
        return {
            "name": poi.get("display_name"),
            "lat": float(poi["lat"]),
            "lon": float(poi["lon"])
        }
    except requests.RequestException as e:
        print("Ошибка запроса к API:", e)
        return None

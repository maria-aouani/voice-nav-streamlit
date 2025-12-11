# indoor_nav.py
import requests

# Пример карты здания (фиктивные координаты комнат и точек)
INDOOR_MAP = {
    "Entrance": (43.238950, 76.889700),
    "Reception": (43.238970, 76.889750),
    "Store A": (43.238990, 76.889800),
    "Store B": (43.239010, 76.889850),
    "Cafe": (43.239030, 76.889900),
}

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # замените на ваш ключ

def get_indoor_route(poi):
    """
    Эмулируем indoor-навигацию.
    poi: словарь с ключами 'name', 'lat', 'lon' (например из search_poi)
    """
    # Начальная точка внутри здания
    origin_name = "Entrance"
    origin_coord = INDOOR_MAP[origin_name]

    destination_coord = (poi["lat"], poi["lon"])

    # Создаём "шаги маршрута" через несколько промежуточных точек внутри здания
    # В реальном проекте можно использовать граф комнат, коридоров и лестниц
    steps = []

    intermediate_points = list(INDOOR_MAP.values())
    for i, coord in enumerate(intermediate_points):
        if coord == origin_coord:
            continue
        if coord == destination_coord:
            break
        steps.append({
            "html_instructions": f"Go to {intermediate_points[i]} inside the building",
            "distance": {"text": "10 m", "value": 10},
            "duration": {"text": "15 sec", "value": 15},
            "end_location": {"lat": coord[0], "lng": coord[1]},
        })

    # Финальная точка
    steps.append({
        "html_instructions": f"Arrive at {poi['name']}",
        "distance": {"text": "5 m", "value": 5},
        "duration": {"text": "10 sec", "value": 10},
        "end_location": {"lat": destination_coord[0], "lng": destination_coord[1]},
    })

    route = {
        "routes": [
            {
                "legs": [
                    {
                        "steps": steps
                    }
                ]
            }
        ]
    }

    return route
